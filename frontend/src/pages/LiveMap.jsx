import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import KpiCard from '../components/KpiCard'
import FilterBar from '../components/FilterBar'
import AtmMap from '../components/AtmMap'
import AtmSlideOver from '../components/AtmSlideOver'
import { getAtms, getNetworkStats, getNotifications } from '../services/api'
import { connectSocket, disconnectSocket } from '../services/socket'
import { useAtmsStore } from '../store/atmsSlice'
import { timeAgo } from '../utils/format'
import { useT } from '../utils/i18n'

export default function LiveMap() {
  const { stats, setAtms, setStats } = useAtmsStore()
  const [alerts, setAlerts] = useState([])
  const [error, setError] = useState('')
  const { t, dict } = useT()

  useEffect(() => {
    getAtms().then(setAtms).catch((e) => setError(e.message))
    getNetworkStats().then(setStats).catch((e) => setError(e.message))
    getNotifications().then((n) => setAlerts(n.slice(0, 3))).catch(() => {})
    connectSocket()
    return () => disconnectSocket()
  }, [setAtms, setStats])

  return (
    <div className="max-w-6xl mx-auto p-4">
      <Navbar />

      {error && <p className="bg-rose-50 text-rose-700 text-sm rounded-xl p-3 mb-4">{t('loadFailed')} {error}</p>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <KpiCard value={stats.online} label={t('kpiOnline')} color="text-emerald-700" />
        <KpiCard value={stats.lowCash + stats.emptyCash} label={t('kpiLowCash')} color="text-amber-600" />
        <KpiCard value={stats.offline + stats.maintenance} label={t('kpiOffline')} color="text-rose-600" />
        <KpiCard value={stats.uptimePercentage == null ? '—' : `${stats.uptimePercentage}%`} label={t('kpiUptime')} color="text-slate-900" />
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="space-y-4">
          <FilterBar />
          <div className="bg-white/80 rounded-3xl p-5 shadow-sm">
            <h3 className="font-bold mb-3">{t('latestAlerts')}</h3>
            <ul className="space-y-3">
              {alerts.length === 0 && <li className="text-sm text-slate-400">{t('noAlerts')}</li>}
              {alerts.map((n) => (
                <li key={n.id}>
                  <div className="text-sm font-medium">{n.atmName} — {t(n.reason)}</div>
                  <div className="text-xs text-slate-400">{timeAgo(n.createdAt, dict)}</div>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="md:col-span-2">
          <AtmMap />
        </div>
      </div>

      <AtmSlideOver />
    </div>
  )
}
