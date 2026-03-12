const PALETTE = [
  '#4A90D9', // bleu
  '#E85D75', // rose
  '#2ECC71', // vert
  '#F39C12', // orange
  '#9B59B6', // violet
  '#1ABC9C', // turquoise
  '#E74C3C', // rouge
  '#3498DB', // bleu clair
  '#E67E22', // orange foncé
  '#16A085', // vert foncé
]

let index = 0

export function nextColor() {
  const color = PALETTE[index % PALETTE.length]
  index++
  return color
}

export function resetColors() {
  index = 0
}

const STORAGE_KEY = 'flxo_colors'

function loadColorMap() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
  } catch {
    return {}
  }
}

function saveColorMap(map) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(map))
}

// Returns a stable color for a given backend user ID.
// Assigns and persists a new one if not seen before.
export function colorForUser(backendId) {
  const map = loadColorMap()
  const key = String(backendId)
  if (map[key]) return map[key]
  const color = nextColor()
  map[key] = color
  saveColorMap(map)
  return color
}
