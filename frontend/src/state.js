import { reactive, ref, computed } from 'vue'
import { colorForUser } from './colors.js'
import { DESKS } from './desks.js'
import {
  getToken, setToken,
  apiGetAuthConfig, apiGetMe, apiListUsers, apiUpdateMe,
  apiListOffices, apiCreateOffice,
  apiListSeats, apiCreateSeat,
  apiListPresences,
  apiCreatePresence, apiUpdatePresence, apiDeletePresence,
} from './api.js'

// ─── Auth state ───────────────────────────────────────────────────────────────
export const authToken = ref(getToken())
export const loggedUser = ref(null)   // UserPublic from backend
export const officeId = ref(null)     // int
export const isLoading = ref(false)
export const ssoEnabled = ref(false)

// ─── Persons & bookings ───────────────────────────────────────────────────────
export const persons = reactive([])
export const bookings = reactive([])
export const selectedPersonId = ref(null)
export const currentWeekOffset = ref(0)

export const isPastWeek = computed(() => currentWeekOffset.value < 0)

// Maps deskId (SVG string, e.g. "desk1") ↔ backend seat integer id
const deskToSeatId = reactive({}) // { 'desk1': 3, ... }
const seatToDeskId = reactive({}) // { 3: 'desk1', ... }


// Set of "weekKey-day-slot" keys where confirmed count exceeds seat capacity
export const overbookedSlots = computed(() => {
  const counts = {}
  for (const b of bookings) {
    if (b.state !== 'confirmed') continue
    const key = `${b.weekKey}-${b.day}-${b.slot}`
    counts[key] = (counts[key] || 0) + 1
  }
  const result = new Set()
  for (const [key, count] of Object.entries(counts)) {
    if (count > DESKS.length) result.add(key)
  }
  return result
})

export function getTodayDayIndex(offset) {
  if (offset < 0) return 5
  if (offset > 0) return -1
  const dow = new Date().getDay()
  if (dow === 0 || dow === 6) return 5
  return dow - 1
}

let personIdCounter = 0

export const selectedPerson = computed(() =>
  persons.find(p => p.id === selectedPersonId.value) || null
)

export const sortedPersons = computed(() =>
  [...persons].sort((a, b) => {
    if (a.isLoggedUser) return -1
    if (b.isLoggedUser) return 1
    return 0
  })
)

export function getWeekKey(offset) {
  const now = new Date()
  const monday = getMonday(now)
  monday.setDate(monday.getDate() + offset * 7)
  const year = monday.getFullYear()
  const weekNum = getISOWeekNumber(monday)
  return `${year}-W${String(weekNum).padStart(2, '0')}`
}

export function getWeekDates(offset) {
  const now = new Date()
  const monday = getMonday(now)
  monday.setDate(monday.getDate() + offset * 7)
  const dates = []
  for (let i = 0; i < 5; i++) {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    dates.push(d)
  }
  return dates
}

export function currentWeekKey() {
  return getWeekKey(currentWeekOffset.value)
}

// ─── Date conversion helpers ──────────────────────────────────────────────────

// weekKeyDayToISO("2026-W08", 0) → "2026-02-16"  (day: 0=Mon, 4=Fri)
export function weekKeyDayToISO(weekKey, day) {
  const [yearStr, weekStr] = weekKey.split('-W')
  const year = parseInt(yearStr)
  const week = parseInt(weekStr)
  // Jan 4 is always in ISO week 1
  const jan4 = new Date(Date.UTC(year, 0, 4))
  const jan4dow = jan4.getUTCDay() || 7 // 1=Mon…7=Sun
  const week1Monday = new Date(jan4)
  week1Monday.setUTCDate(jan4.getUTCDate() - (jan4dow - 1))
  const target = new Date(week1Monday)
  target.setUTCDate(week1Monday.getUTCDate() + (week - 1) * 7 + day)
  const y = target.getUTCFullYear()
  const m = String(target.getUTCMonth() + 1).padStart(2, '0')
  const d = String(target.getUTCDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

// isoToWeekKeyDay("2026-02-16") → { weekKey: "2026-W08", day: 0 }
export function isoToWeekKeyDay(isoDate) {
  const [y, mo, d] = isoDate.split('-').map(Number)
  const date = new Date(Date.UTC(y, mo - 1, d))
  const dow = date.getUTCDay() || 7 // 1=Mon…7=Sun
  // Compute ISO week: find Thursday of this week
  const thursday = new Date(date)
  thursday.setUTCDate(date.getUTCDate() + 4 - dow)
  const yearStart = new Date(Date.UTC(thursday.getUTCFullYear(), 0, 1))
  const week = Math.ceil(((thursday - yearStart) / 86400000 + 1) / 7)
  const year = thursday.getUTCFullYear()
  const weekKey = `${year}-W${String(week).padStart(2, '0')}`
  const day = dow - 1 // 0=Mon…6=Sun
  return { weekKey, day }
}

// ─── Person management ────────────────────────────────────────────────────────

// Takes a UserPublic object from backend
export function addPerson(userData, { select = true, isLoggedUser = false } = {}) {
  personIdCounter++
  const person = {
    id: `p${personIdCounter}`,
    backendId: userData.id,
    name: userData.username,
    color: colorForUser(userData.id),
    deskPreference: userData.favorite_seat_id ? (seatToDeskId[userData.favorite_seat_id] ?? null) : null,
    isLoggedUser,
  }
  persons.push(person)
  if (select) selectedPersonId.value = person.id
  return person
}

export function removePerson(id) {
  const idx = persons.findIndex(p => p.id === id)
  if (idx !== -1) persons.splice(idx, 1)
  for (let i = bookings.length - 1; i >= 0; i--) {
    if (bookings[i].personId === id) bookings.splice(i, 1)
  }
  if (selectedPersonId.value === id) {
    selectedPersonId.value = persons.length ? persons[0].id : null
  }
}

export async function setDeskPreference(personId, deskId) {
  const person = persons.find(p => p.id === personId)
  if (!person) return
  const prev = person.deskPreference
  person.deskPreference = person.deskPreference === deskId ? null : deskId
  if (person.isLoggedUser) {
    try {
      const backendSeatId = person.deskPreference ? (deskToSeatId[person.deskPreference] ?? null) : null
      await apiUpdateMe(backendSeatId)
    } catch (e) {
      console.error('Failed to save desk preference:', e)
      person.deskPreference = prev // rollback
    }
  }
}

// ─── Booking local helpers ────────────────────────────────────────────────────

function _applyBookingLocal(personId, weekKey, day, slot, state, backendId, seatId = null) {
  const idx = bookings.findIndex(
    b => b.personId === personId && b.weekKey === weekKey && b.day === day && b.slot === slot
  )
  if (idx !== -1) {
    bookings[idx].state = state
    bookings[idx].backendId = backendId
    bookings[idx].seatId = seatId
  } else {
    bookings.push({ personId, weekKey, day, slot, state, backendId, seatId })
  }
}

function _removeBookingLocal(personId, weekKey, day, slot) {
  const idx = bookings.findIndex(
    b => b.personId === personId && b.weekKey === weekKey && b.day === day && b.slot === slot
  )
  if (idx !== -1) bookings.splice(idx, 1)
}

export function getBookingState(personId, weekKey, day, slot) {
  const b = bookings.find(
    b => b.personId === personId && b.weekKey === weekKey && b.day === day && b.slot === slot
  )
  return b ? b.state : null
}

export function hasBooking(personId, weekKey, day, slot) {
  return bookings.some(
    b => b.personId === personId && b.weekKey === weekKey && b.day === day && b.slot === slot
  )
}

// ─── Async booking operations ─────────────────────────────────────────────────

export async function toggleBooking(personId, weekKey, day, slot) {
  const idx = bookings.findIndex(
    b => b.personId === personId && b.weekKey === weekKey && b.day === day && b.slot === slot
  )
  const person = persons.find(p => p.id === personId)

  if (idx !== -1) {
    const current = bookings[idx].state
    const booking = bookings[idx]
    if (current === 'confirmed') {
      // confirmed → maybe
      bookings[idx].state = 'maybe'
      if (person?.isLoggedUser && booking.backendId) {
        try {
          const iso = weekKeyDayToISO(weekKey, day)
          const backendSeatId = booking.seatId ? (deskToSeatId[booking.seatId] ?? null) : null
          await apiUpdatePresence(booking.backendId, iso, slot, 'maybe', officeId.value, backendSeatId)
        } catch (e) {
          console.error('Failed to update presence (confirmed→maybe):', e)
          bookings[idx].state = 'confirmed' // rollback
        }
      }
    } else {
      // maybe → null
      const savedBooking = { ...booking }
      bookings.splice(idx, 1)
      if (person?.isLoggedUser && savedBooking.backendId) {
        try {
          await apiDeletePresence(savedBooking.backendId)
        } catch (e) {
          console.error('Failed to delete presence:', e)
          bookings.push(savedBooking) // rollback
        }
      }
    }
  } else {
    // null → confirmed
    bookings.push({ personId, weekKey, day, slot, state: 'confirmed', backendId: null })
    if (person?.isLoggedUser) {
      try {
        const iso = weekKeyDayToISO(weekKey, day)
        const created = await apiCreatePresence(iso, slot, 'confirmed', officeId.value)
        const newIdx = bookings.findIndex(
          b => b.personId === personId && b.weekKey === weekKey && b.day === day && b.slot === slot
        )
        if (newIdx !== -1) bookings[newIdx].backendId = created.id
      } catch (e) {
        console.error('Failed to create presence:', e)
        _removeBookingLocal(personId, weekKey, day, slot) // rollback
      }
    }
  }
}

export async function setBooking(personId, weekKey, day, slot) {
  const existing = bookings.find(
    b => b.personId === personId && b.weekKey === weekKey && b.day === day && b.slot === slot
  )
  if (existing) {
    existing.state = 'confirmed'
    return
  }
  const person = persons.find(p => p.id === personId)
  bookings.push({ personId, weekKey, day, slot, state: 'confirmed', backendId: null })
  if (person?.isLoggedUser) {
    try {
      const iso = weekKeyDayToISO(weekKey, day)
      const created = await apiCreatePresence(iso, slot, 'confirmed', officeId.value)
      const newIdx = bookings.findIndex(
        b => b.personId === personId && b.weekKey === weekKey && b.day === day && b.slot === slot
      )
      if (newIdx !== -1) bookings[newIdx].backendId = created.id
    } catch (e) {
      console.error('Failed to create presence (setBooking):', e)
      _removeBookingLocal(personId, weekKey, day, slot) // rollback
    }
  }
}

export async function removeBooking(personId, weekKey, day, slot) {
  const idx = bookings.findIndex(
    b => b.personId === personId && b.weekKey === weekKey && b.day === day && b.slot === slot
  )
  if (idx === -1) return
  const person = persons.find(p => p.id === personId)
  const savedBooking = { ...bookings[idx] }
  bookings.splice(idx, 1)
  if (person?.isLoggedUser && savedBooking.backendId) {
    try {
      await apiDeletePresence(savedBooking.backendId)
    } catch (e) {
      console.error('Failed to delete presence (removeBooking):', e)
      bookings.push(savedBooking) // rollback
    }
  }
}

export function getSlotDesk(personId, weekKey, day, slot) {
  const b = bookings.find(
    b => b.personId === personId && b.weekKey === weekKey && b.day === day && b.slot === slot
  )
  return b ? b.seatId : null
}

export async function setSlotDesk(personId, weekKey, day, slot, seatId) {
  const idx = bookings.findIndex(
    b => b.personId === personId && b.weekKey === weekKey && b.day === day && b.slot === slot
  )
  if (idx === -1) return
  const booking = bookings[idx]
  const prevSeatId = booking.seatId
  booking.seatId = seatId
  const person = persons.find(p => p.id === personId)
  if (person?.isLoggedUser && booking.backendId) {
    try {
      const iso = weekKeyDayToISO(weekKey, day)
      const backendSeatId = seatId ? (deskToSeatId[seatId] ?? null) : null
      await apiUpdatePresence(booking.backendId, iso, slot, booking.state, officeId.value, backendSeatId)
    } catch (e) {
      console.error('Failed to update seat:', e)
      booking.seatId = prevSeatId
    }
  }
}

// ─── Load presences from API ──────────────────────────────────────────────────

const loadedWeekKeys = new Set()

export async function loadPresenceRange(fromOffset, toOffset) {
  const fromISO = weekKeyDayToISO(getWeekKey(fromOffset), 0)
  const toISO = weekKeyDayToISO(getWeekKey(toOffset), 4)
  const presences = await apiListPresences(fromISO, toISO)
  // Mark all week keys in range as loaded
  for (let o = fromOffset; o <= toOffset; o++) {
    loadedWeekKeys.add(getWeekKey(o))
  }
  for (const p of presences) {
    const person = persons.find(pe => pe.backendId === p.user.id)
    if (!person) continue
    const { weekKey, day } = isoToWeekKeyDay(p.date)
    const deskId = p.seat_id ? (seatToDeskId[p.seat_id] ?? null) : null
    _applyBookingLocal(person.id, weekKey, day, p.slot, p.state, p.id, deskId)
  }
}

// ─── Navigation ───────────────────────────────────────────────────────────────

export async function navigateWeek(delta) {
  currentWeekOffset.value += delta
  const offset = currentWeekOffset.value
  const weekKeys = [getWeekKey(offset), getWeekKey(offset + 1)]
  const missing = weekKeys.filter(wk => !loadedWeekKeys.has(wk))
  if (missing.length === 0) return

  // Find the contiguous range of missing offsets
  const missingOffsets = []
  for (let o = offset; o <= offset + 1; o++) {
    if (!loadedWeekKeys.has(getWeekKey(o))) missingOffsets.push(o)
  }
  const minOffset = Math.min(...missingOffsets)
  const maxOffset = Math.max(...missingOffsets)
  await loadPresenceRange(minOffset, maxOffset)
}

// ─── App initialization ───────────────────────────────────────────────────────

export async function initApp() {
  isLoading.value = true
  try {
    // 1. Auth config + logged user
    const config = await apiGetAuthConfig()
    ssoEnabled.value = config.sso_enabled
    const me = await apiGetMe()
    loggedUser.value = me

    // 2. Get or create office
    const offices = await apiListOffices()
    let office = offices.find(o => o.name === 'Wojo Paris')
    if (!office) {
      office = await apiCreateOffice('Wojo Paris', 'Paris')
    }
    officeId.value = office.id

    // 3. Load or create seats (desk1-desk6 ↔ backend seat IDs)
    try {
      const seats = await apiListSeats()
      const officeSeats = seats.filter(s => s.office_id === officeId.value)
      for (const desk of DESKS) {
        let seat = officeSeats.find(s => s.name === desk.id)
        if (!seat) seat = await apiCreateSeat(desk.id, officeId.value)
        deskToSeatId[desk.id] = seat.id
        seatToDeskId[seat.id] = desk.id
      }
    } catch (e) {
      console.error('Failed to load/create seats:', e)
    }

    // 4. Load all users
    persons.splice(0)
    bookings.splice(0)
    loadedWeekKeys.clear()
    selectedPersonId.value = null

    const users = await apiListUsers()
    for (const u of users) {
      const isMe = u.id === me.id
      addPerson(u, { select: isMe, isLoggedUser: isMe })
    }

    // 5. Load presences for a broad range
    await loadPresenceRange(-4, 9)
  } finally {
    isLoading.value = false
  }
}

// ─── Internal helpers ─────────────────────────────────────────────────────────

function getMonday(date) {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  d.setDate(diff)
  d.setHours(0, 0, 0, 0)
  return d
}

function getISOWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
  const dayNum = d.getUTCDay() || 7
  d.setUTCDate(d.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
  return Math.ceil(((d - yearStart) / 86400000 + 1) / 7)
}
