<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { floorPlanUrl, DESK_IDS } from '../state.js'

const props = defineProps({
  person: Object,
  initialDesk: { default: undefined },
  subtitle: { type: String, default: null },
  takenDesks: { type: Array, default: () => [] }, // [{ deskId, name, color }]
})
const emit = defineEmits(['close', 'confirm'])

const svgContainer = ref(null)
const svgContent = ref('')
const tooltip = ref({ show: false, text: '', x: 0, y: 0 })
const pendingDesk = ref(props.initialDesk !== undefined ? props.initialDesk : props.person.deskPreference)
const canConfirm = computed(() => pendingDesk.value !== null || props.initialDesk != null)
const applyToAll = ref(false)

function onKeyDown(e) {
  if (e.key === 'Escape') emit('close')
}

onMounted(async () => {
  window.addEventListener('keydown', onKeyDown)
  if (!floorPlanUrl.value) return
  const resp = await fetch(floorPlanUrl.value)
  svgContent.value = await resp.text()
})

onUnmounted(() => window.removeEventListener('keydown', onKeyDown))

watch(svgContent, async () => {
  await new Promise(r => setTimeout(r, 50))
  bindDesks()
  updateColors()
})

watch(pendingDesk, () => updateColors())

function isTaken(deskId) {
  return props.takenDesks.some(t => t.deskId === deskId)
}

function deskLabel(deskId) {
  const num = deskId.replace('desk', '')
  return `Bureau ${num}`
}

function bindDesks() {
  if (!svgContainer.value) return
  for (const deskId of DESK_IDS.value) {
    const el = svgContainer.value.querySelector(`#${deskId}`)
    if (!el) continue
    el.style.transition = 'filter 0.15s'
    el.addEventListener('mouseenter', (e) => onHover(deskId, el, e))
    el.addEventListener('mouseleave', () => onLeave(el))
    el.addEventListener('click', () => onPick(deskId))
  }
}

function updateColors() {
  if (!svgContainer.value) return
  for (const deskId of DESK_IDS.value) {
    const el = svgContainer.value.querySelector(`#${deskId}`)
    if (!el) continue
    const isPending = pendingDesk.value === deskId
    const taken = props.takenDesks.find(t => t.deskId === deskId)
    if (isPending) {
      el.style.fill = props.person.color
      el.style.fillOpacity = '0.9'
      el.style.cursor = 'pointer'
    } else if (taken) {
      el.style.fill = taken.color
      el.style.fillOpacity = '0.7'
      el.style.cursor = 'not-allowed'
    } else {
      el.style.fill = '#95bdd1'
      el.style.fillOpacity = '1'
      el.style.cursor = 'pointer'
    }
  }
}

function onHover(deskId, el, event) {
  if (!isTaken(deskId)) {
    el.style.filter = 'brightness(1.25) drop-shadow(0 0 6px rgba(0,0,0,0.28))'
  }
  const taken = props.takenDesks.find(t => t.deskId === deskId)
  let text = deskLabel(deskId)
  if (taken) text += '\n' + taken.name
  const rect = svgContainer.value.getBoundingClientRect()
  tooltip.value = {
    show: true, text,
    x: event.clientX - rect.left + 12,
    y: event.clientY - rect.top - 10,
  }
}

function onLeave(el) {
  el.style.filter = ''
  tooltip.value.show = false
}

function onPick(deskId) {
  if (isTaken(deskId)) return
  pendingDesk.value = pendingDesk.value === deskId ? null : deskId
}

function confirm() {
  emit('confirm', pendingDesk.value, applyToAll.value)
  emit('close')
}
</script>

<template>
  <div class="desk-modal-overlay" @click.self="$emit('close')">
    <div class="desk-modal">
      <div class="desk-modal-header">
        <span>Bureau de <strong>{{ person.name }}</strong><span v-if="subtitle" class="header-subtitle"> — {{ subtitle }}</span></span>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      <div class="desk-modal-body" ref="svgContainer">
        <div v-html="svgContent" class="svg-wrapper"></div>
        <div
          v-if="tooltip.show"
          class="tooltip"
          :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
        >
          <div v-for="line in tooltip.text.split('\n')" :key="line">{{ line }}</div>
        </div>
      </div>
      <div class="desk-modal-footer">
        <span class="desk-hint">
          {{ pendingDesk ? `${deskLabel(pendingDesk)} sélectionné` : 'Aucun bureau sélectionné' }}
        </span>
        <label class="apply-all-label">
          <input type="checkbox" v-model="applyToAll" />
          Appliquer à toutes mes réservations futures
        </label>
        <div class="desk-actions">
          <button class="btn-cancel" @click="$emit('close')">Annuler</button>
          <button class="btn-confirm" @click="confirm" :disabled="!canConfirm">Valider</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.desk-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.desk-modal {
  background: white;
  border-radius: 10px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.22);
  width: 700px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.desk-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid #eee;
  font-size: 14px;
  flex-shrink: 0;
}
.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #aaa;
  line-height: 1;
  padding: 0 4px;
}
.close-btn:hover {
  color: #333;
}
.header-subtitle {
  font-weight: 400;
  color: #888;
}
.desk-modal-body {
  position: relative;
  padding: 16px;
}
.svg-wrapper :deep(svg) {
  width: 100%;
  height: auto;
  max-height: 60vh;
  display: block;
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
.desk-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  border-top: 1px solid #eee;
  flex-shrink: 0;
  gap: 12px;
}
.desk-hint {
  font-size: 12px;
  color: #999;
}
.apply-all-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  white-space: nowrap;
}
.desk-actions {
  display: flex;
  gap: 8px;
}
.btn-cancel {
  background: none;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 6px 16px;
  font-size: 13px;
  cursor: pointer;
}
.btn-cancel:hover {
  background: #f5f5f5;
}
.btn-confirm {
  background: #4A90D9;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 6px 16px;
  font-size: 13px;
  cursor: pointer;
}
.btn-confirm:hover:not(:disabled) {
  background: #3a7bc8;
}
.btn-confirm:disabled {
  background: #b0c8e8;
  cursor: default;
}
</style>
