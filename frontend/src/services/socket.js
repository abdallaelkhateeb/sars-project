import { useAuthStore } from '../store/authSlice'
import { useAtmsStore } from '../store/atmsSlice'
import { getAtms, getNetworkStats } from './api'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/dashboard'

let socket = null
let pollTimer = null

async function refresh() {
  const s = useAtmsStore.getState()
  s.setAtms(await getAtms())
  s.setStats(await getNetworkStats())
}

// Until the backend WebSocket is ready, fall back to refreshing every 10 seconds.
function startPolling() {
  if (pollTimer) return
  pollTimer = setInterval(() => refresh().catch(console.error), 10000)
}

export function connectSocket() {
  const token = useAuthStore.getState().accessToken
  try {
    socket = new WebSocket(`${WS_URL}?token=${token}`)
    socket.onmessage = () => refresh().catch(console.error)
    socket.onerror = startPolling
    socket.onclose = startPolling
  } catch (e) {
    startPolling()
  }
}

export function disconnectSocket() {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = null
  if (socket) socket.close()
  socket = null
}
