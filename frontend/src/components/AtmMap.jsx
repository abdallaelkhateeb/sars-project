import { useAtmsStore } from '../store/atmsSlice'
import { useT } from '../utils/i18n'

export function atmColor(atm) {
  if (atm.status === 'OFFLINE' || atm.status === 'MAINTENANCE') return '#e11d48'
  if (atm.cashStatus === 'LOW' || atm.cashStatus === 'EMPTY') return '#d97706'
  return '#10b981'
}

export function matchesFilter(atm, filter) {
  if (filter === 'ALL') return true
  if (filter === 'OFFLINE') return atm.status === 'OFFLINE' || atm.status === 'MAINTENANCE'
  if (filter === 'LOW_CASH') return atm.cashStatus === 'LOW' || atm.cashStatus === 'EMPTY'
  if (filter === 'ONLINE') return atm.status === 'ONLINE' && atm.cashStatus === 'AVAILABLE'
  return true
}

export default function AtmMap() {
  const { atms, filter, selectedAtmId, selectAtm } = useAtmsStore()
  const { t } = useT()
  const visible = atms.filter((a) => matchesFilter(a, filter))

  const lats = atms.map((a) => a.latitude)
  const lngs = atms.map((a) => a.longitude)
  const minLat = Math.min(...lats), maxLat = Math.max(...lats)
  const minLng = Math.min(...lngs), maxLng = Math.max(...lngs)
  const pad = 40, W = 800, H = 420
  const x = (lng) => pad + ((lng - minLng) / (maxLng - minLng || 1)) * (W - pad * 2)
  const y = (lat) => H - pad - ((lat - minLat) / (maxLat - minLat || 1)) * (H - pad * 2)

  return (
    <div className="bg-white/80 rounded-3xl p-5 shadow-sm h-full">
      <div className="flex items-center gap-2 font-bold mb-3">
        <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
        {t('mapTitle')}
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" dir="ltr">
        {visible.map((a) => (
          <g key={a.id} onClick={() => selectAtm(a.id)} className="cursor-pointer">
            <circle cx={x(a.longitude)} cy={y(a.latitude)} r={selectedAtmId === a.id ? 22 : 16} fill={atmColor(a)} opacity="0.18" />
            <circle cx={x(a.longitude)} cy={y(a.latitude)} r="8" fill="#fff" stroke={atmColor(a)} strokeWidth="4" />
            <text x={x(a.longitude)} y={y(a.latitude) - 24} textAnchor="middle" fontSize="12" fill="#475569">{a.name}</text>
          </g>
        ))}
      </svg>
      {atms.length === 0 && <p className="text-center text-sm text-slate-400 py-8">{t('noAtms')}</p>}
      <div className="flex gap-4 text-xs text-slate-500 mt-2">
        <Legend color="#10b981" label={t('fOnline')} />
        <Legend color="#d97706" label={t('fLowCash')} />
        <Legend color="#e11d48" label={t('fOffline')} />
      </div>
    </div>
  )
}

function Legend({ color, label }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className="w-2.5 h-2.5 rounded-full" style={{ background: color }} />
      {label}
    </span>
  )
}
