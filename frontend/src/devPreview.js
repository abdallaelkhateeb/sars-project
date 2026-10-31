// DEMO MODE ONLY (VITE_DEMO=true): fake API responses so the dashboard can be
// previewed without the backend. Never loaded when VITE_DEMO is not 'true'.
const now = Date.now()
const iso = (ms = 0) => new Date(now - ms).toISOString()

const atms = [
  { atmId: 'ATM-001', branchName: 'فرع التحرير', status: 'ONLINE', cashStatus: 'AVAILABLE', services: ['WITHDRAWAL', 'DEPOSIT'], latitude: 30.0444, longitude: 31.2357, lastHeartbeatAt: iso(10e3) },
  { atmId: 'ATM-002', branchName: 'فرع الزمالك', status: 'ONLINE', cashStatus: 'LOW', services: ['WITHDRAWAL'], latitude: 30.0626, longitude: 31.2197, lastHeartbeatAt: iso(20e3) },
  { atmId: 'ATM-003', branchName: 'فرع المعادي', status: 'OFFLINE', cashStatus: 'EMPTY', services: ['WITHDRAWAL', 'DEPOSIT'], latitude: 29.9602, longitude: 31.2569, lastHeartbeatAt: iso(3600e3) },
  { atmId: 'ATM-004', branchName: 'فرع مدينة نصر', status: 'ONLINE', cashStatus: 'AVAILABLE', services: ['WITHDRAWAL', 'DEPOSIT', 'CURRENCY_EXCHANGE'], latitude: 30.0561, longitude: 31.3301, lastHeartbeatAt: iso(15e3) },
  { atmId: 'ATM-005', branchName: 'فرع مصر الجديدة', status: 'MAINTENANCE', cashStatus: 'AVAILABLE', services: ['WITHDRAWAL'], latitude: 30.0866, longitude: 31.3225, lastHeartbeatAt: iso(600e3) },
  { atmId: 'ATM-006', branchName: 'فرع الدقي', status: 'ONLINE', cashStatus: 'AVAILABLE', services: ['WITHDRAWAL', 'DEPOSIT'], latitude: 30.0381, longitude: 31.2112, lastHeartbeatAt: iso(5e3) },
]

const notifications = [
  { id: 4, atmName: 'فرع المعادي', requestedService: 'WITHDRAWAL', reason: 'OFFLINE', status: 'PENDING', createdAt: iso(2 * 60e3) },
  { id: 3, atmName: 'فرع الزمالك', requestedService: 'WITHDRAWAL', reason: 'INSUFFICIENT_CASH', status: 'DELIVERED', createdAt: iso(14 * 60e3) },
  { id: 2, atmName: 'فرع مصر الجديدة', requestedService: 'DEPOSIT', reason: 'MAINTENANCE', status: 'FAILED', createdAt: iso(32 * 60e3) },
  { id: 1, atmName: 'فرع الدقي', requestedService: 'WITHDRAWAL', reason: 'OFFLINE', status: 'DELIVERED', createdAt: iso(95 * 60e3) },
]

const json = (body) =>
  Promise.resolve(new Response(JSON.stringify(body), { status: 200, headers: { 'Content-Type': 'application/json' } }))

const realFetch = window.fetch.bind(window)
window.fetch = (url, opts) => {
  const u = String(url)
  if (u.includes('/auth/login')) return json({ access: 'demo', refresh: 'demo', user: { username: 'admin.ops', role: 'ADMIN' } })
  if (u.includes('/atms/network-stats')) return json({ totalAtms: 6, online: 4, offline: 1, maintenance: 1, lowCash: 1, emptyCash: 1, uptimePercentage: 99.98 })
  const one = u.match(/\/atms\/([^/?]+)$/)
  if (one) {
    const a = atms.find((x) => x.atmId === one[1])
    return json({ ...a, recentHeartbeats: [
      { status: a.status, cashStatus: a.cashStatus, receivedAt: iso(10e3) },
      { status: 'ONLINE', cashStatus: 'AVAILABLE', receivedAt: iso(70e3) },
    ] })
  }
  if (u.endsWith('/atms')) return json({ data: atms })
  if (u.includes('/notifications')) return json({ data: notifications })
  return realFetch(url, opts)
}