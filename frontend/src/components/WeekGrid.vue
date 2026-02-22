<script setup>
import { computed } from 'vue'
import PersonRow from './PersonRow.vue'
import { sortedPersons, bookings, currentWeekOffset, getWeekKey, getWeekDates, getTodayDayIndex } from '../state.js'
import { DESKS } from '../desks.js'

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

const emptyRowCount = computed(() => Math.max(0, DESKS.length - visiblePersons.value.length))

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
    <table class="week-grid" v-if="visiblePersons.length || DESKS.length">
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
  height: 28px;
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
</style>
