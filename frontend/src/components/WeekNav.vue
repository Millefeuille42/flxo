<script setup>
import { computed } from 'vue'
import { currentWeekOffset, getWeekKey, navigateWeek } from '../state.js'

const label = computed(() => {
  const wk1 = getWeekKey(currentWeekOffset.value).split('-W')[1]
  const wk2 = getWeekKey(currentWeekOffset.value + 1).split('-W')[1]
  return `Sem. ${wk1}–${wk2}`
})

const isCurrentWeek = computed(() => currentWeekOffset.value === 0)

function prev() { navigateWeek(-1) }
function next() { navigateWeek(+1) }
function goToday() { navigateWeek(-currentWeekOffset.value) }
</script>

<template>
  <div class="week-nav">
    <button @click="goToday" class="today-btn" :class="{ active: isCurrentWeek }" title="Semaine en cours">
      <svg viewBox="0 0 23 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs><clipPath id="cal"><rect x="1" y="1" width="21" height="18" rx="2.5"/></clipPath></defs>
        <rect x="1" y="1" width="21" height="18" rx="2.5" fill="white"/>
        <g clip-path="url(#cal)">
          <line x1="8" y1="1" x2="8" y2="19" stroke="#777" stroke-width="1"/>
          <line x1="15" y1="1" x2="15" y2="19" stroke="#777" stroke-width="1"/>
          <line x1="1" y1="13" x2="22" y2="13" stroke="#777" stroke-width="1"/>
          <rect x="1" y="1" width="21" height="6" fill="#444"/>
          <rect x="8" y="13" width="7" height="6" fill="#444"/>
        </g>
        <rect x="1" y="1" width="21" height="18" rx="2.5" stroke="#444" stroke-width="1.5" fill="none"/>
      </svg>
    </button>
    <button @click="prev" class="nav-btn"><svg viewBox="0 0 10 16" fill="none" xmlns="http://www.w3.org/2000/svg"><polyline points="8,2 2,8 8,14" stroke="#444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
    <span class="week-label">{{ label }}</span>
    <button @click="next" class="nav-btn"><svg viewBox="0 0 10 16" fill="none" xmlns="http://www.w3.org/2000/svg"><polyline points="2,2 8,8 2,14" stroke="#444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
  </div>
</template>

<style scoped>
.week-nav {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nav-btn {
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 4px 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.nav-btn svg {
  width: 10px;
  height: 16px;
}
.nav-btn:hover {
  background: #f0f0f0;
}
.today-btn {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  height: 30px;
  width: 30px;
}
.today-btn svg {
  width: 100%;
  height: 100%;
}
.today-btn:hover {
  opacity: 0.7;
}
.today-btn.active {
  opacity: 0.4;
  cursor: default;
}
.week-label {
  font-weight: 600;
  font-size: 14px;
  min-width: 120px;
  text-align: center;
}
</style>
