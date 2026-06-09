<script setup>
import { ref, computed } from 'vue'
import SlotCell from './SlotCell.vue'
import { selectedPersonId, toggleBooking, setBooking, removeBooking, getBookingState, getSlotDesk } from '../state.js'

const props = defineProps({
  person: Object,
  weeks: Array,
})

const DAYS = [0, 1, 2, 3, 4]
const SLOTS = ['morning', 'afternoon']

const isSelected = computed(() => selectedPersonId.value === props.person.id)

function select() {
  selectedPersonId.value = props.person.id
}

// Drag-select state
const isDragging = ref(false)
const dragMode = ref(null) // 'add' or 'remove'

function onToggle({ weekKey, day, slot, pastDay }) {
  if (pastDay) return
  if (!props.person.isLoggedUser) return
  const state = getBookingState(props.person.id, weekKey, day, slot)
  dragMode.value = state !== null ? 'remove' : 'add'
  isDragging.value = true
  toggleBooking(props.person.id, weekKey, day, slot)
  select()
  window.addEventListener('mouseup', onMouseUp, { once: true })
}

function onDragEnter({ weekKey, day, slot, pastDay }) {
  if (!isDragging.value) return
  if (pastDay) return
  if (!props.person.isLoggedUser) return
  const state = getBookingState(props.person.id, weekKey, day, slot)
  if (dragMode.value === 'add' && state === null) {
    setBooking(props.person.id, weekKey, day, slot)
  } else if (dragMode.value === 'remove' && state !== null) {
    removeBooking(props.person.id, weekKey, day, slot)
  }
}

function onMouseUp() {
  isDragging.value = false
  dragMode.value = null
}
</script>

<template>
  <tr :class="['person-row', { selected: isSelected }]" @click="select">
    <td class="person-info">
      <div class="person-cell">
        <span class="color-dot" :style="{ background: person.color }"></span>
        <span class="person-name">{{ person.name }}</span>
      </div>
    </td>
    <template v-for="(week, wi) in weeks" :key="week.weekKey">
      <template v-for="day in DAYS" :key="`${week.weekKey}-${day}`">
        <SlotCell
          v-for="slot in SLOTS"
          :key="`${week.weekKey}-${day}-${slot}`"
          :personId="person.id"
          :personColor="person.color"
          :weekKey="week.weekKey"
          :day="day"
          :slot="slot"
          :pastDay="day < week.todayDayIndex"
          :week2Start="wi > 0 && day === 0 && slot === 'morning'"
          :hasDeskIndicator="!person.isLoggedUser && !!getSlotDesk(person.id, week.weekKey, day, slot)"
          @toggle="onToggle"
          @dragenter="onDragEnter"
        />
      </template>
    </template>
  </tr>
</template>

<style scoped>
.person-row {
  border-bottom: 1px solid #eee;
}
.person-row.selected {
  background: #f8f9ff;
}
.person-info {
  min-width: 180px;
  white-space: nowrap;
  vertical-align: middle;
  padding: 0;
}
.person-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 33px;
  padding: 0 8px;
}
.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}
.person-name {
  font-weight: 500;
  font-size: 14px;
}
</style>
