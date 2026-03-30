import { reactive, ref, computed, watch, triggerRef } from 'vue'
import { colorForUser } from './colors.js'
import {
  getToken, setToken,
  apiGetAuthConfig, apiGetMe, apiListUsers, apiUpdateMe,
  apiListSeats, apiListOfficeSeatsPaginated, apiCreateSeat,
  apiListPresences,
  apiCreatePresence, apiUpdatePresence, apiDeletePresence,
} from './api.js'

// ─── Auth state ───────────────────────────────────────────────────────────────
export const authToken = ref(getToken())
export const loggedUser = ref(null)   // UserPublic from backend
export const isLoading = ref(false)
export const ssoEnabled = ref(false)

// ─── Multi-office state ──────────────────────────────────────────────────────
export const offices = reactive([])     // Array of { id, name, address, logo_url, floor_plan_url, desk_count }
export const activeOfficeId = ref(null) // int, persisted in localStorage

export const activeOffice = computed(() =>
  offices.find(o => o.id === activeOfficeId.value) || null
)
export const logoUrl = computed(() => activeOffice.value?.logo_url || '')
export const floorPlanUrl = computed(() => activeOffice.value?.floor_plan_url || '')
export const deskCount = computed(() => activeOffice.value?.desk_count || 0)
export const DESK_IDS = computed(() => Array.from({ length: deskCount.value }, (_, i) => 'desk' + (i + 1)))

// ─── Persons & bookings ───────────────────────────────────────────────────────
export const persons = reactive([])
export const selectedPersonId = ref(null)
export const currentWeekOffset = ref(0)
export const hoveredSlot = ref(null) // { weekKey, day, slot } or null

export const isPastWeek = computed(() => currentWeekOffset.value < 0)

// ─── Booking index (Map-based for O(1) lookups) ─────────────────────────────
// Key: "personId|weekKey|day|slot" → booking object (unique per person+slot, cross-office)
const _bookingMap = new Map()
// Reactive version counter — triggers reactivity when bookings change
const _bookingVersion = ref(0)
function _notifyBookings() { _bookingVersion.value++ }

function _bkey(personId, weekKey, day, slot) {
  return `${personId}|${weekKey}|${day}|${slot}`
}

// Derived reactive array for consumers that need to iterate (WeekGrid)
export const bookings = computed(() => {
  _bookingVersion.value // track reactivity
  return Array.from(_bookingMap.values())
})

// Per-office seat maps: { [officeId]: { 'desk1': seatId, ... } }
const deskToSeatIdByOffice = reactive({})
const seatToDeskIdByOffice = reactive({})

// Convenience accessors for active office
function deskToSeatId(deskId) {
  const map = deskToSeatIdByOffice[activeOfficeId.value]
  return map ? map[deskId] : undefined
}
function seatToDeskId(seatId) {
  const map = seatToDeskIdByOffice[activeOfficeId.value]
  return map ? map[seatId] : undefined
}
// Lookup across all offices
function seatToDeskIdGlobal(seatId) {
  for (const map of Object.values(seatToDeskIdByOffice)) {
    if (map[seatId] !== undefined) return map[seatId]
  }
  return undefined
}
function seatToOfficeId(seatId) {
  for (const [oid, map] of Object.entries(seatToDeskIdByOffice)) {
    if (map[seatId] !== undefined) return Number(oid)
  }
  return undefined
}

// Set of "weekKey-day-slot" keys where confirmed count exceeds seat capacity (active office only)
export const overbookedSlots = computed(() => {
  _bookingVersion.value // track
  const oid = activeOfficeId.value
  const counts = {}
  for (const b of _bookingMap.values()) {
    if (b.officeId !== oid || b.state !== 'confirmed') continue
    const key = `${b.weekKey}-${b.day}-${b.slot}`
    counts[key] = (counts[key] || 0) + 1
  }
  const result = new Set()
  for (const [key, count] of Object.entries(counts)) {
    if (count > deskCount.value) result.add(key)
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
  // Resolve desk preference: find which office this seat belongs to
  let deskPref = null
  if (userData.favorite_seat_id) {
    const prefOffice = seatToOfficeId(userData.favorite_seat_id)
    if (prefOffice === activeOfficeId.value) {
      deskPref = seatToDeskId(userData.favorite_seat_id) ?? null
    }
  }
  const person = {
    id: `p${personIdCounter}`,
    backendId: userData.id,
    name: userData.properties?.display_name || userData.username,
    color: colorForUser(userData.id),
    deskPreference: deskPref,
    favoriteSeatId: userData.favorite_seat_id ?? null,
    isLoggedUser,
  }
  persons.push(person)
  if (select) selectedPersonId.value = person.id
  return person
}

export function removePerson(id) {
  const idx = persons.findIndex(p => p.id === id)
  if (idx !== -1) persons.splice(idx, 1)
  for (const [key, b] of _bookingMap) {
    if (b.personId === id) _bookingMap.delete(key)
  }
  _notifyBookings()
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
      const backendSeatId = person.deskPreference ? (deskToSeatId(person.deskPreference) ?? null) : null
      await apiUpdateMe({ username: loggedUser.value.username, favorite_seat_id: backendSeatId })
      person.favoriteSeatId = backendSeatId
    } catch (e) {
      console.error('Failed to save desk preference:', e)
      person.deskPreference = prev // rollback
    }
  }
}

// ─── Booking local helpers ────────────────────────────────────────────────────

function _applyBookingLocal(personId, weekKey, day, slot, state, backendId, seatId = null, officeId = null) {
  const key = _bkey(personId, weekKey, day, slot)
  const existing = _bookingMap.get(key)
  if (existing) {
    existing.state = state
    existing.backendId = backendId
    existing.seatId = seatId
    existing.officeId = officeId
  } else {
    _bookingMap.set(key, { personId, weekKey, day, slot, state, backendId, seatId, officeId })
  }
  _notifyBookings()
}

function _removeBookingLocal(personId, weekKey, day, slot) {
  _bookingMap.delete(_bkey(personId, weekKey, day, slot))
  _notifyBookings()
}

export function getBookingState(personId, weekKey, day, slot) {
  _bookingVersion.value // track
  const b = _bookingMap.get(_bkey(personId, weekKey, day, slot))
  if (!b) return null
  return b.officeId === activeOfficeId.value ? b.state : null
}

export function getConflictingOfficeName(personId, weekKey, day, slot) {
  const office = _getConflictingOffice(personId, weekKey, day, slot)
  return office ? office.name : null
}

export function hasBooking(personId, weekKey, day, slot) {
  _bookingVersion.value // track
  const b = _bookingMap.get(_bkey(personId, weekKey, day, slot))
  return b ? b.officeId === activeOfficeId.value : false
}

export const bookingError = ref(null) // { message: string } or null

function _getConflictingOffice(personId, weekKey, day, slot) {
  _bookingVersion.value // track
  const b = _bookingMap.get(_bkey(personId, weekKey, day, slot))
  if (!b || b.officeId === activeOfficeId.value) return null
  return offices.find(o => o.id === b.officeId) || null
}

// ─── Async booking operations ─────────────────────────────────────────────────

export async function toggleBooking(personId, weekKey, day, slot) {
  const oid = activeOfficeId.value
  const key = _bkey(personId, weekKey, day, slot)
  const booking = _bookingMap.get(key)
  const person = persons.find(p => p.id === personId)

  if (booking && booking.officeId === oid) {
    const current = booking.state
    if (current === 'confirmed') {
      // confirmed → maybe
      booking.state = 'maybe'
      _notifyBookings()
      if (person?.isLoggedUser && booking.backendId) {
        try {
          const iso = weekKeyDayToISO(weekKey, day)
          const backendSeatId = booking.seatId ? (deskToSeatId(booking.seatId) ?? null) : null
          await apiUpdatePresence(booking.backendId, iso, slot, 'maybe', oid, backendSeatId)
        } catch (e) {
          console.error('Failed to update presence (confirmed→maybe):', e)
          booking.state = 'confirmed' // rollback
          _notifyBookings()
        }
      }
    } else {
      // maybe → null
      const savedBooking = { ...booking }
      _bookingMap.delete(key)
      _notifyBookings()
      if (person?.isLoggedUser && savedBooking.backendId) {
        try {
          await apiDeletePresence(savedBooking.backendId)
        } catch (e) {
          console.error('Failed to delete presence:', e)
          _bookingMap.set(key, savedBooking) // rollback
          _notifyBookings()
        }
      }
    }
  } else {
    // null → confirmed — check cross-office conflict
    const conflict = _getConflictingOffice(personId, weekKey, day, slot)
    if (conflict) {
      const slotLabel = slot === 'morning' ? 'matin' : 'après-midi'
      const iso = weekKeyDayToISO(weekKey, day)
      const [, m, d] = iso.split('-')
      bookingError.value = { message: `Vous êtes déjà réservé(e) à ${conflict.name} le ${d}/${m} (${slotLabel})` }
      return
    }
    const newBooking = { personId, weekKey, day, slot, state: 'confirmed', backendId: null, seatId: null, officeId: oid }
    _bookingMap.set(key, newBooking)
    _notifyBookings()
    if (person?.isLoggedUser) {
      try {
        const iso = weekKeyDayToISO(weekKey, day)
        const created = await apiCreatePresence(iso, slot, 'confirmed', oid)
        newBooking.backendId = created.id
      } catch (e) {
        console.error('Failed to create presence:', e)
        _bookingMap.delete(key) // rollback
        _notifyBookings()
      }
    }
  }
}

export async function setBooking(personId, weekKey, day, slot) {
  const oid = activeOfficeId.value
  const key = _bkey(personId, weekKey, day, slot)
  const existing = _bookingMap.get(key)
  if (existing && existing.officeId === oid) {
    existing.state = 'confirmed'
    _notifyBookings()
    return
  }
  const conflict = _getConflictingOffice(personId, weekKey, day, slot)
  if (conflict) {
    const slotLabel = slot === 'morning' ? 'matin' : 'après-midi'
    const iso = weekKeyDayToISO(weekKey, day)
    const [, m, d] = iso.split('-')
    bookingError.value = { message: `Vous êtes déjà réservé(e) à ${conflict.name} le ${d}/${m} (${slotLabel})` }
    return
  }
  const person = persons.find(p => p.id === personId)
  const newBooking = { personId, weekKey, day, slot, state: 'confirmed', backendId: null, seatId: null, officeId: oid }
  _bookingMap.set(key, newBooking)
  _notifyBookings()
  if (person?.isLoggedUser) {
    try {
      const iso = weekKeyDayToISO(weekKey, day)
      const created = await apiCreatePresence(iso, slot, 'confirmed', oid)
      newBooking.backendId = created.id
    } catch (e) {
      console.error('Failed to create presence (setBooking):', e)
      _bookingMap.delete(key) // rollback
      _notifyBookings()
    }
  }
}

export async function removeBooking(personId, weekKey, day, slot) {
  const key = _bkey(personId, weekKey, day, slot)
  const booking = _bookingMap.get(key)
  if (!booking) return
  const person = persons.find(p => p.id === personId)
  const savedBooking = { ...booking }
  _bookingMap.delete(key)
  _notifyBookings()
  if (person?.isLoggedUser && savedBooking.backendId) {
    try {
      await apiDeletePresence(savedBooking.backendId)
    } catch (e) {
      console.error('Failed to delete presence (removeBooking):', e)
      _bookingMap.set(key, savedBooking) // rollback
      _notifyBookings()
    }
  }
}

export function getSlotDesk(personId, weekKey, day, slot) {
  _bookingVersion.value // track
  const b = _bookingMap.get(_bkey(personId, weekKey, day, slot))
  return (b && b.officeId === activeOfficeId.value) ? b.seatId : null
}

export async function setSlotDesk(personId, weekKey, day, slot, seatId) {
  const oid = activeOfficeId.value
  const key = _bkey(personId, weekKey, day, slot)
  const booking = _bookingMap.get(key)
  if (!booking || booking.officeId !== oid) return
  const prevSeatId = booking.seatId
  booking.seatId = seatId
  _notifyBookings()
  const person = persons.find(p => p.id === personId)
  if (person?.isLoggedUser && booking.backendId) {
    try {
      const iso = weekKeyDayToISO(weekKey, day)
      const backendSeatId = seatId ? (deskToSeatId(seatId) ?? null) : null
      await apiUpdatePresence(booking.backendId, iso, slot, booking.state, oid, backendSeatId)
    } catch (e) {
      console.error('Failed to update seat:', e)
      booking.seatId = prevSeatId
      _notifyBookings()
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
    const deskId = p.seat_id ? (seatToDeskIdGlobal(p.seat_id) ?? null) : null
    // Batch: don't notify per item
    const key = _bkey(person.id, weekKey, day, p.slot)
    const existing = _bookingMap.get(key)
    if (existing) {
      existing.state = p.state
      existing.backendId = p.id
      existing.seatId = deskId
      existing.officeId = p.office_id
    } else {
      _bookingMap.set(key, { personId: person.id, weekKey, day, slot: p.slot, state: p.state, backendId: p.id, seatId: deskId, officeId: p.office_id })
    }
  }
  _notifyBookings() // single notification after batch
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

// ─── Office switching ─────────────────────────────────────────────────────────

export function switchOffice(newOfficeId) {
  activeOfficeId.value = newOfficeId
  localStorage.setItem('flxo_office_id', String(newOfficeId))

  // Update desk preferences for all persons based on new office context
  for (const person of persons) {
    if (person.favoriteSeatId) {
      const prefOffice = seatToOfficeId(person.favoriteSeatId)
      person.deskPreference = prefOffice === newOfficeId
        ? (seatToDeskIdByOffice[newOfficeId]?.[person.favoriteSeatId] ?? null)
        : null
    } else {
      person.deskPreference = null
    }
  }
}

// ─── App initialization ───────────────────────────────────────────────────────

export async function initApp() {
  isLoading.value = true
  try {
    // 1. Auth config + logged user
    const config = await apiGetAuthConfig()
    ssoEnabled.value = config.sso_enabled
    offices.splice(0, offices.length, ...(config.offices || []))

    // Restore or default active office
    const savedOfficeId = Number(localStorage.getItem('flxo_office_id'))
    const validOffice = offices.find(o => o.id === savedOfficeId)
    activeOfficeId.value = validOffice ? savedOfficeId : (offices[0]?.id ?? null)
    localStorage.setItem('flxo_office_id', String(activeOfficeId.value))

    const me = await apiGetMe()
    loggedUser.value = me

    // 2. Load seats for all offices (paginated, per office)
    for (const office of offices) {
      try {
        const officeSeats = await apiListOfficeSeatsPaginated(office.id)
        deskToSeatIdByOffice[office.id] = {}
        seatToDeskIdByOffice[office.id] = {}
        const deskIds = Array.from({ length: office.desk_count }, (_, i) => 'desk' + (i + 1))
        for (const deskId of deskIds) {
          let seat = officeSeats.find(s => s.name === deskId)
          if (!seat) seat = await apiCreateSeat(deskId, office.id)
          deskToSeatIdByOffice[office.id][deskId] = seat.id
          seatToDeskIdByOffice[office.id][seat.id] = deskId
        }
      } catch (e) {
        console.error(`Failed to load/create seats for office ${office.name}:`, e)
      }
    }

    // 3. Load all users
    persons.splice(0)
    _bookingMap.clear()
    _notifyBookings()
    loadedWeekKeys.clear()
    selectedPersonId.value = null

    const users = await apiListUsers()
    for (const u of users) {
      const isMe = u.id === me.id
      addPerson(u, { select: isMe, isLoggedUser: isMe })
    }

    // 4. Load presences for a broad range
    await loadPresenceRange(-4, 9)
  } finally {
    isLoading.value = false
  }
}

// ─── Slot desk assignments (for FloorPlan hover preview) ─────────────────────

export function getSlotDeskAssignments(weekKey, day, slot) {
  _bookingVersion.value // track
  const oid = activeOfficeId.value
  const result = []
  for (const b of _bookingMap.values()) {
    if (b.officeId !== oid || b.weekKey !== weekKey || b.day !== day || b.slot !== slot || !b.seatId) continue
    const person = persons.find(p => p.id === b.personId)
    if (!person) continue
    result.push({ deskId: b.seatId, personName: person.name, personColor: person.color })
  }
  return result
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
