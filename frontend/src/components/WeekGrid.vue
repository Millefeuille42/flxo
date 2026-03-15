<script setup>
import { computed, ref } from 'vue'
import PersonRow from './PersonRow.vue'
import DeskPickerModal from './DeskPickerModal.vue'
import { sortedPersons, bookings, currentWeekOffset, getWeekKey, getWeekDates, getTodayDayIndex, setSlotDesk, weekKeyDayToISO, deskCount } from '../state.js'

const DAY_NAMES = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven']
const DAYS = [0, 1, 2, 3, 4]
const SLOTS = ['morning', 'afternoon']

const visiblePersons = computed(() => {
  const currentKey = getWeekKey(0)
  return sortedPersons.value.filter(person =>
    person.isLoggedUser ||
    bookings.some(b => b.personId === person.id && b.weekKey >= currentKey)
  )
})

const emptyRowCount = computed(() => Math.max(0, deskCount.value - visiblePersons.value.length))

const loggedPerson = computed(() => sortedPersons.value.find(p => p.isLoggedUser) || null)

// Desk picker for the slot row
const openPickerSlot = ref(null) // { weekKey, day, slot, subtitle }

function getLoggedBooking(weekKey, day, slot) {
  if (!loggedPerson.value) return null
  return bookings.find(
    b => b.personId === loggedPerson.value.id && b.weekKey === weekKey && b.day === day && b.slot === slot
  ) || null
}

function canPickDesk(week, dayIndex, slot) {
  if (week.isPast || week.days[dayIndex].past) return false
  const booking = getLoggedBooking(week.weekKey, dayIndex, slot)
  return booking?.state === 'confirmed'
}

function deskCellStyle(week, dayIndex, slot) {
  const booking = getLoggedBooking(week.weekKey, dayIndex, slot)
  const color = loggedPerson.value?.color ?? '#aaa'
  if (!booking) return { background: '#f0f0f0' }
  if (booking.seatId) return { background: color, '--icon-color': 'white' }
  if (booking.state === 'confirmed') return { background: '#e8e8e8', '--icon-color': color }
  return { background: '#e8e8e8', '--icon-color': '#aaa' }
}

function openDeskPicker(week, dayIndex, slot) {
  const booking = getLoggedBooking(week.weekKey, dayIndex, slot)
  const slotLabel = slot === 'morning' ? 'AM' : 'PM'
  const takenDesks = bookings
    .filter(b => b.weekKey === week.weekKey && b.day === dayIndex && b.slot === slot && b.seatId && b.personId !== loggedPerson.value?.id)
    .map(b => {
      const person = sortedPersons.value.find(p => p.id === b.personId)
      return { deskId: b.seatId, name: person?.name ?? '?', color: person?.color ?? '#888' }
    })
  openPickerSlot.value = {
    weekKey: week.weekKey,
    day: dayIndex,
    slot,
    initialDesk: booking?.seatId ?? null,
    subtitle: `${week.days[dayIndex].name} ${week.days[dayIndex].date} — ${slotLabel}`,
    takenDesks,
  }
}

async function onSlotDeskConfirm(deskId, applyToAll) {
  if (!openPickerSlot.value || !loggedPerson.value) return
  const { weekKey, day, slot } = openPickerSlot.value
  await setSlotDesk(loggedPerson.value.id, weekKey, day, slot, deskId)
  if (applyToAll) {
    const todayISO = new Date().toISOString().slice(0, 10)
    const currentSlotISO = weekKeyDayToISO(weekKey, day)
    const futurBookings = bookings.filter(b =>
      b.personId === loggedPerson.value.id &&
      b.state === 'confirmed' &&
      !(b.weekKey === weekKey && b.day === day && b.slot === slot) &&
      weekKeyDayToISO(b.weekKey, b.day) >= (currentSlotISO > todayISO ? currentSlotISO : todayISO)
    )
    for (const b of futurBookings) {
      await setSlotDesk(loggedPerson.value.id, b.weekKey, b.day, b.slot, deskId)
    }
  }
}

const weeks = computed(() => {
  return [0, 1].map(i => {
    const offset = currentWeekOffset.value + i
    const dates = getWeekDates(offset)
    const weekKey = getWeekKey(offset)
    const weekNum = weekKey.split('-W')[1]
    const todayDayIndex = getTodayDayIndex(offset)
    const isPast = offset < 0
    return {
      offset,
      weekKey,
      weekNum,
      isPast,
      todayDayIndex,
      days: dates.map((d, di) => ({
        name: DAY_NAMES[di],
        date: `${d.getDate()}/${d.getMonth() + 1}`,
        index: di,
        past: di < todayDayIndex,
      })),
    }
  })
})
</script>

<template>
  <div class="week-grid-wrapper">
    <div class="legend">
      <span class="legend-item">
        <span class="legend-swatch confirmed">&#10003;</span>
        Présent
      </span>
      <span class="legend-item">
        <span class="legend-swatch maybe">?</span>
        Peut-être
      </span>
    </div>
    <table class="week-grid" v-if="visiblePersons.length || deskCount">
      <thead>
        <tr>
          <th class="corner" rowspan="2"></th>
          <template v-for="(week, wi) in weeks" :key="week.weekKey">
            <th
              v-for="(day, di) in week.days"
              :key="`${wi}-${di}`"
              colspan="2"
              :class="['day-header', { 'past-day': day.past, 'week2-start': wi > 0 && di === 0 }]"
            >
              <div class="day-name">{{ day.name }}</div>
              <div class="day-date">{{ day.date }}</div>
            </th>
          </template>
        </tr>
        <tr>
          <template v-for="(week, wi) in weeks" :key="'sl-' + week.weekKey">
            <template v-for="(day, di) in week.days" :key="`${wi}-${di}`">
              <th :class="['slot-header', 'am', { 'week2-start': wi > 0 && di === 0 }]">AM</th>
              <th class="slot-header pm">PM</th>
            </template>
          </template>
        </tr>
        <tr class="week-label-row">
          <th></th>
          <template v-for="week in weeks" :key="'lbl-' + week.weekKey">
            <th colspan="10" :class="['week-label', { 'past-week-label': week.isPast }]">
              Sem. {{ week.weekNum }}
            </th>
          </template>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loggedPerson" class="desk-row">
          <td class="corner desk-row-label">Mon poste</td>
          <template v-for="(week, wi) in weeks" :key="'dr-' + week.weekKey">
            <template v-for="(day, di) in DAYS" :key="di">
              <td
                v-for="slot in SLOTS"
                :key="slot"
                :class="['desk-slot', {
                  'day-start': slot === 'morning',
                  'week2-start': wi > 0 && di === 0 && slot === 'morning',
                  'pickable': canPickDesk(week, di, slot),
                  'has-desk': !!getLoggedBooking(week.weekKey, di, slot)?.seatId,
                }]"
                :style="deskCellStyle(week, di, slot)"
                @click="canPickDesk(week, di, slot) && openDeskPicker(week, di, slot)"
              >
                <div v-if="getLoggedBooking(week.weekKey, di, slot)" class="desk-slot-inner">
                  <svg viewBox="0 0 16 14" fill="none" xmlns="http://www.w3.org/2000/svg" class="desk-slot-icon">
                    <rect x="0.5" y="0.5" width="15" height="10" rx="1.5" stroke="currentColor" fill="currentColor" fill-opacity="0.25"/>
                    <path d="M5 13.5h6M8 10.5v3" stroke="currentColor" stroke-linecap="round"/>
                  </svg>
                </div>
              </td>
            </template>
          </template>
        </tr>
        <PersonRow
          v-for="person in visiblePersons"
          :key="person.id"
          :person="person"
          :weeks="weeks"
        />
        <tr v-for="i in emptyRowCount" :key="'empty-' + i" class="empty-row">
          <td class="corner empty-info"></td>
          <template v-for="(week, wi) in weeks" :key="week.weekKey">
            <template v-for="(day, di) in DAYS" :key="di">
              <td
                v-for="slot in SLOTS"
                :key="slot"
                :class="['empty-slot', { 'day-start': slot === 'morning', 'week2-start': wi > 0 && di === 0 && slot === 'morning' }]"
              ></td>
            </template>
          </template>
        </tr>
      </tbody>
    </table>
    <div v-else class="empty-msg">
      Ajoutez des personnes pour commencer
    </div>
  </div>

  <Teleport to="body">
    <DeskPickerModal
      v-if="openPickerSlot && loggedPerson"
      :person="loggedPerson"
      :initialDesk="openPickerSlot.initialDesk"
      :subtitle="openPickerSlot.subtitle"
      :takenDesks="openPickerSlot.takenDesks"
      @close="openPickerSlot = null"
      @confirm="(deskId, applyToAll) => onSlotDeskConfirm(deskId, applyToAll)"
    />
  </Teleport>
</template>

<style scoped>
.week-grid-wrapper {
  overflow-x: hidden;
}
.week-grid {
  border-collapse: collapse;
  font-size: 13px;
}
.corner {
  min-width: 180px;
}
.day-header {
  text-align: center;
  padding: 4px 0;
  border-bottom: 1px solid #ddd;
  border-left: 2px solid #999;
}
.day-header.week2-start {
  border-left: 4px solid #333;
}
.day-header.past-day {
  opacity: 0.5;
}
.day-name {
  font-weight: 600;
  font-size: 13px;
}
.day-date {
  font-weight: 400;
  font-size: 11px;
  color: #888;
}
.slot-header {
  font-weight: 400;
  font-size: 11px;
  color: #999;
  padding: 2px 8px;
  text-align: center;
}
.slot-header.am {
  border-left: 2px solid #999;
}
.slot-header.am.week2-start {
  border-left: 4px solid #333;
}
.week-label-row th {
  padding: 2px 0;
  font-size: 11px;
  font-weight: 600;
  color: #666;
  border-bottom: 1px solid #ddd;
}
.week-label {
  text-align: center;
}
.past-week-label {
  color: #bbb;
}
.empty-msg {
  color: #aaa;
  font-style: italic;
  padding: 40px;
  text-align: center;
}
.legend {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  margin-bottom: 8px;
  font-size: 12px;
  color: #888;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}
.legend-swatch {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 16px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: bold;
}
.legend-swatch.confirmed {
  background: #888;
  color: white;
}
.legend-swatch.maybe {
  background: #88888828;
  outline: 2px solid #888;
  outline-offset: -2px;
  color: #888;
}
.empty-row {
  border-bottom: 1px solid #eee;
}
.empty-info {
  min-width: 180px;
}
.empty-slot {
  width: 44px;
  height: 33px;
  background: #f5f5f5;
  opacity: 0.6;
  border: 1px solid #e0e0e0;
  cursor: default;
}
.empty-slot.day-start {
  border-left: 2px solid #999;
}
.empty-slot.week2-start {
  border-left: 4px solid #333;
}
.desk-row {
  border-bottom: 2px solid #ddd;
}
.desk-row-label {
  font-size: 11px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0 8px;
}
.desk-slot {
  width: 44px;
  height: 33px;
  border: 1px solid #e0e0e0;
  transition: filter 0.1s;
  padding: 0;
}
.desk-slot.day-start {
  border-left: 2px solid #999;
}
.desk-slot.week2-start {
  border-left: 4px solid #333;
}
.desk-slot.pickable {
  cursor: pointer;
}
.desk-slot.pickable:hover {
  filter: brightness(0.92);
}
.desk-slot-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.desk-slot-icon {
  width: 12px;
  height: 12px;
  display: block;
  color: var(--icon-color, rgba(0,0,0,0.2));
}
</style>
