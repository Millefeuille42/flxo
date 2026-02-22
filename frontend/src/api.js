const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8080'

export function getToken() {
  return localStorage.getItem('flxo_token')
}

export function setToken(token) {
  if (token === null) {
    localStorage.removeItem('flxo_token')
  } else {
    localStorage.setItem('flxo_token', token)
  }
}

async function apiFetch(path, options = {}) {
  const token = getToken()
  const headers = { ...(options.headers ?? {}) }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  if (!res.ok) {
    const err = new Error(`API error ${res.status}`)
    err.status = res.status
    try {
      const data = await res.json()
      err.detail = data.detail
    } catch {}
    if (res.status === 401) {
      setToken(null)
      window.location.reload()
    }
    throw err
  }
  return res
}

export async function apiGetAuthConfig() {
  const res = await fetch(`${BASE_URL}/auth/config`)
  return res.json()
}

export async function apiLogin(username, password) {
  const body = new URLSearchParams({ username, password })
  const res = await fetch(`${BASE_URL}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  })
  if (!res.ok) {
    const err = new Error(`Login failed: ${res.status}`)
    err.status = res.status
    throw err
  }
  return res.json()
}

export async function apiGetMe() {
  const res = await apiFetch('/user/me')
  return res.json()
}

export async function apiListUsers() {
  const res = await apiFetch('/user/?limit=200')
  return res.json()
}

export async function apiUpdateMe(comment) {
  const res = await apiFetch('/user/me', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ comment }),
  })
  return res.json()
}

export async function apiCreateUser(username, password) {
  const res = await apiFetch('/user/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, hashed_password: '' }),
  })
  return res.json()
}

export async function apiListOffices() {
  const res = await apiFetch('/office/')
  return res.json()
}

export async function apiCreateOffice(name, address) {
  const res = await apiFetch('/office/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, address }),
  })
  return res.json()
}

export async function apiListPresences(dateFrom, dateTo) {
  const params = new URLSearchParams({ limit: '500' })
  if (dateFrom) params.set('date_from', dateFrom)
  if (dateTo) params.set('date_to', dateTo)
  const res = await apiFetch(`/presence/?${params}`)
  return res.json()
}

export async function apiCreatePresence(date, slot, state, officeId) {
  const res = await apiFetch('/presence/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ date, slot, state, office_id: officeId, seat_id: null }),
  })
  return res.json()
}

export async function apiUpdatePresence(id, date, slot, state, officeId) {
  const res = await apiFetch(`/presence/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ date, slot, state, office_id: officeId, seat_id: null }),
  })
  return res.json()
}

export async function apiDeletePresence(id) {
  await apiFetch(`/presence/${id}`, { method: 'DELETE' })
}

export async function apiDeleteUser(id) {
  await apiFetch(`/user/${id}`, { method: 'DELETE' })
}
