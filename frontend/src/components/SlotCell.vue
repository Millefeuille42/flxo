<script setup>
import { computed } from 'vue'
import { getBookingState, overbookedSlots, hoveredSlot } from '../state.js'

const props = defineProps({
  personId: String,
  personColor: String,
  weekKey: String,
  day: Number,
  slot: String,
  pastDay: { type: Boolean, default: false },
  week2Start: { type: Boolean, default: false },
  hasDeskIndicator: { type: Boolean, default: false },
})

const emit = defineEmits(['toggle', 'dragenter'])

const bookingState = computed(() => getBookingState(props.personId, props.weekKey, props.day, props.slot))

const isOverbooked = computed(() =>
  bookingState.value === 'confirmed' &&
  overbookedSlots.value.has(`${props.weekKey}-${props.day}-${props.slot}`)
)

const cellStyle = computed(() => {
  if (props.pastDay) {
    const bg = bookingState.value === 'confirmed'
      ? props.personColor
      : bookingState.value === 'maybe'
        ? props.personColor + '44'
        : '#e0e0e0'
    return { background: bg, opacity: 0.5 }
  }
  if (bookingState.value === 'confirmed') {
    if (isOverbooked.value) {
      return {
        background: props.personColor,
        outline: '2px solid #e53e3e',
        outlineOffset: '-2px',
      }
    }
    return { background: props.personColor }
  }
  if (bookingState.value === 'maybe') {
    return {
      background: props.personColor + '28',
      outline: `2px solid ${props.personColor}`,
      outlineOffset: '-2px',
    }
  }
  return { background: '#f5f5f5', opacity: 0.6 }
})

function emitToggle() {
  emit('toggle', { weekKey: props.weekKey, day: props.day, slot: props.slot, pastDay: props.pastDay })
}
function onMouseEnter() {
  if (bookingState.value) {
    hoveredSlot.value = { weekKey: props.weekKey, day: props.day, slot: props.slot }
  }
  emitDragEnter()
}
function onMouseLeave() {
  hoveredSlot.value = null
}
function emitDragEnter() {
  emit('dragenter', { weekKey: props.weekKey, day: props.day, slot: props.slot, pastDay: props.pastDay })
}
</script>

<template>
  <td
    :class="['slot-cell', { 'past-day': pastDay, 'day-start': slot === 'morning', 'week2-start': week2Start }]"
    :style="cellStyle"
    @mousedown.prevent="emitToggle"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <span v-if="bookingState === 'confirmed' && isOverbooked" class="overbooked">&#9888;</span>
    <span v-else-if="bookingState === 'confirmed'" class="check">&#10003;</span>
    <span v-else-if="bookingState === 'maybe'" class="maybe" :style="{ color: personColor }">?</span>
    <span v-if="hasDeskIndicator" class="desk-dot" :style="{ borderBottomColor: `color-mix(in srgb, ${personColor} 60%, black)` }"></span>
  </td>
</template>

<style scoped>
.slot-cell {
  position: relative;
  width: 44px;
  height: 33px;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  text-align: center;
  vertical-align: middle;
  transition: background 0.15s;
  user-select: none;
}
.slot-cell.day-start {
  border-left: 2px solid #999;
}
.slot-cell.week2-start {
  border-left: 4px solid #333;
}
.slot-cell:not(.past-day):hover {
  outline: 2px solid #333;
  outline-offset: -2px;
}
.slot-cell.past-day {
  cursor: default;
}
.check {
  color: white;
  font-size: 14px;
  font-weight: bold;
}
.overbooked {
  color: #e53e3e;
  font-size: 13px;
}
.maybe {
  font-size: 15px;
  font-weight: 700;
}
.desk-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 0 11px 11px;
  border-color: transparent transparent currentColor transparent;
}
</style>
