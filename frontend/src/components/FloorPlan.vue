<script setup>
import { ref, onMounted, watch } from 'vue'
import { persons, selectedPersonId, selectedPerson, setDeskPreference } from '../state.js'
import { DESKS } from '../desks.js'

const svgContainer = ref(null)
const svgContent = ref('')
const tooltip = ref({ show: false, text: '', x: 0, y: 0 })
const showScreens = ref(false)

onMounted(async () => {
  const resp = await fetch(import.meta.env.BASE_URL + 'wojo-paris.svg')
  svgContent.value = await resp.text()
  await nextTickUpdate()
})

async function nextTickUpdate() {
  await new Promise(r => setTimeout(r, 50))
  updateDeskColors()
  bindDeskEvents()
}

function bindDeskEvents() {
  if (!svgContainer.value) return
  for (const desk of DESKS) {
    const el = svgContainer.value.querySelector(`#${desk.id}`)
    if (!el) continue
    el.style.cursor = 'pointer'
    el.addEventListener('click', () => onDeskClick(desk.id))
    el.addEventListener('mouseenter', (e) => onDeskHover(desk, e))
    el.addEventListener('mouseleave', () => { tooltip.value.show = false })
  }
}

function onDeskClick(deskId) {
  if (!selectedPersonId.value) return
  setDeskPreference(selectedPersonId.value, deskId)
}

function onDeskHover(desk, event) {
  const tags = desk.tags.length ? desk.tags.join(', ') : 'aucun tag'
  const occupants = persons
    .filter(p => p.deskPreference === desk.id)
    .map(p => p.name)
  let text = `${desk.label} — ${tags}`
  if (occupants.length) text += `\n${occupants.join(', ')}`
  const rect = svgContainer.value.getBoundingClientRect()
  tooltip.value = {
    show: true,
    text,
    x: event.clientX - rect.left + 10,
    y: event.clientY - rect.top - 10,
  }
}

function updateDeskColors() {
  if (!svgContainer.value) return
  for (const desk of DESKS) {
    const el = svgContainer.value.querySelector(`#${desk.id}`)
    if (!el) continue
    const occupants = persons.filter(p => p.deskPreference === desk.id)
    if (occupants.length === 1) {
      el.style.fill = occupants[0].color
      el.style.fillOpacity = '0.7'
    } else if (occupants.length > 1) {
      el.style.fill = occupants[0].color
      el.style.fillOpacity = '0.5'
    } else {
      el.style.fill = '#95bdd1'
      el.style.fillOpacity = '1'
    }
  }
}

watch(
  () => persons.map(p => `${p.id}:${p.deskPreference}:${p.color}`).join(','),
  () => updateDeskColors()
)

watch(svgContent, () => nextTickUpdate())
</script>

<template>
  <div class="floor-plan" ref="svgContainer">
    <div v-html="svgContent" :class="['svg-wrapper', { 'hide-screens': !showScreens }]"></div>
    <button class="toggle-screens" :class="{ active: showScreens }" @click="showScreens = !showScreens" title="Afficher/masquer les écrans">
      <svg viewBox="0 0 16 14" fill="none" xmlns="http://www.w3.org/2000/svg" width="14" height="14">
        <rect x="0.5" y="0.5" width="15" height="10" rx="1.5" stroke="currentColor"/>
        <path d="M5 13.5h6M8 10.5v3" stroke="currentColor" stroke-linecap="round"/>
      </svg>
    </button>
    <div
      v-if="tooltip.show"
      class="tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <div v-for="line in tooltip.text.split('\n')" :key="line">{{ line }}</div>
    </div>
    <div v-if="!selectedPersonId" class="hint">
      Sélectionnez une personne pour attribuer un bureau
    </div>
    <div v-else class="hint">
      Cliquez un bureau pour l'attribuer à <strong>{{ selectedPerson?.name }}</strong>
    </div>
  </div>
</template>

<style scoped>
.floor-plan {
  position: relative;
}
.svg-wrapper {
  background: white;
}
.svg-wrapper :deep(svg) {
  width: 100%;
  height: auto;
  max-height: 300px;
}
.svg-wrapper.hide-screens :deep([id^="screen"]) {
  display: none !important;
}
.toggle-screens {
  position: absolute;
  top: 6px;
  right: 6px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 3px 4px;
  cursor: pointer;
  color: #aaa;
  line-height: 0;
  transition: color 0.15s, border-color 0.15s;
}
.toggle-screens:hover {
  color: #555;
  border-color: #aaa;
}
.toggle-screens.active {
  color: #4A90D9;
  border-color: #4A90D9;
}
.tooltip {
  position: absolute;
  background: #333;
  color: white;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  white-space: pre-line;
  z-index: 10;
}
.hint {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
  text-align: center;
}
</style>
