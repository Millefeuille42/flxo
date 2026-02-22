<script setup>
import { ref, computed, watch } from 'vue'
import SlotCell from './SlotCell.vue'
import { selectedPersonId, toggleBooking, setBooking, removeBooking, getBookingState } from '../state.js'
import { apiUpdateMe } from '../api.js'
import { DESKS } from '../desks.js'

const props = defineProps({
  person: Object,
  weeks: Array,
})

const DAYS = [0, 1, 2, 3, 4]
const SLOTS = ['morning', 'afternoon']

const isSelected = computed(() => selectedPersonId.value === props.person.id)
const hasComment = computed(() => !!props.person.comment?.trim())
const editingComment = ref(false)

const deskLabel = computed(() => {
  if (!props.person.deskPreference) return null
  const desk = DESKS.find(d => d.id === props.person.deskPreference)
  return desk ? desk.label : null
})

function select() {
  selectedPersonId.value = props.person.id
}

// Debounced comment sync for logged user only
let commentDebounceTimer = null
watch(() => props.person.comment, (newVal) => {
  if (!props.person.isLoggedUser) return
  clearTimeout(commentDebounceTimer)
  commentDebounceTimer = setTimeout(() => {
    apiUpdateMe(newVal).catch(() => {})
  }, 800)
})

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
      <div class="person-header">
        <span class="color-dot" :style="{ background: person.color }"></span>
        <span class="person-name">{{ person.name }}</span>
        <span v-if="deskLabel" class="desk-badge">{{ deskLabel }}</span>
        <button @click.stop="editingComment = !editingComment" :class="['comment-btn', { 'has-comment': hasComment }]" title="Commentaire">
          &#x1f4ac;
        </button>
        <span class="spacer"></span>
      </div>
      <div v-if="editingComment" class="comment-area">
        <textarea
          v-model="person.comment"
          placeholder="Commentaire..."
          rows="2"
          class="comment-input"
        ></textarea>
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
  padding: 6px 10px;
  min-width: 180px;
  white-space: nowrap;
}
.person-header {
  display: flex;
  align-items: center;
  gap: 6px;
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
.desk-badge {
  font-size: 11px;
  background: #eee;
  padding: 1px 6px;
  border-radius: 8px;
  color: #666;
}
.comment-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 0 2px;
  opacity: 0.35;
  position: relative;
}
.comment-btn:hover {
  opacity: 1;
}
.comment-btn.has-comment {
  opacity: 1;
}
.comment-btn.has-comment::after {
  content: '';
  position: absolute;
  top: 0;
  right: -2px;
  width: 6px;
  height: 6px;
  background: #E85D75;
  border-radius: 50%;
}
.spacer {
  flex: 1;
}

.comment-area {
  margin-top: 4px;
}
.comment-input {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 4px 6px;
  font-size: 12px;
  resize: vertical;
  font-family: inherit;
}
</style>
