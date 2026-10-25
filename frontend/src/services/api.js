import { useAuthStore } from '../store/authSlice'

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

async function request(path, options = {}) {
  const token = useAuthStore.getState().accessToken
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.error?.message || err?.detail || `Request failed (${res.status})`)
  }
  return res.json()
}

// Converts the API's field names to the names the screens use.
export function mapAtm(a) {
  return {
    id: a.atmId,
    name: a.branchName,
    status: a.status,
    cashStatus: a.cashStatus,
    services: a.services || [],
    latitude: a.latitude,
    longitude: a.longitude,
    lastHeartbeat: a.lastHeartbeatAt,
    recentHeartbeats: a.recentHeartbeats,
  }
}

export async function login(username, password) {
  const data = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  return { access: data.access, refresh: data.refresh, user: data.user || { username, role: 'ADMIN' } }
}

export async function getAtms() {
  const res = await request('/atms')
  const list = res.data ?? res.results ?? res
  return list.map(mapAtm)
}

export async function getAtm(id) {
  return mapAtm(await request(`/atms/${id}`))
}

export async function getNetworkStats() {
  return request('/atms/network-stats')
}

export async function getNotifications() {
  const res = await request('/notifications')
  return res.data ?? res.results ?? res
}
