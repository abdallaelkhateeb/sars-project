import { useEffect } from 'react'
import { X } from 'lucide-react'
import { useAtmsStore } from '../store/atmsSlice'
import { atmColor } from './AtmMap'
import { getAtm } from '../services/api'
import { timeAgo, formatTime } from '../utils/format'
import { useT } from '../utils/i18n'

export default function AtmSlideOver() {
  const { atms, selectedAtmId, selectedAtmDetail, selectAtm, setAtmDetail } = useAtmsStore()
  const { t, lang, dict } = useT()
  const atm = atms.find((a) => a.id === selectedAtmId)

  useEffect(() => {
    if (selectedAtmId) getAtm(selectedAtmId).then(setAtmDetail).catch(console.error)
  }, [selectedAtmId, setAtmDetail])

  if (!atm) return null
  const heartbeats = selectedAtmDetail?.recentHeartbeats || []

  return (
    <div className="fixed inset-0 z-40" onClick={() => selectAtm(null)}>
      <aside onClick={(e) => e.stopPropagation()} className="absolute top-0 left-0 h-full w-96 max-w-full bg-white shadow-2xl p-6 overflow-y-auto">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold">{atm.name}</h2>
            <p className="text-sm text-slate-400" dir="ltr">{atm.id}</p>
          </div>
          <button onClick={() => selectAtm(null)} className="text-slate-400 hover:text-slate-700"><X size={20} /></button>
        </div>

        <dl className="space-y-4 text-sm">
          <Row label={t('status')}>
            <span className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full" style={{ background: atmColor(atm) }} />
              {t(atm.status)}
            </span>
          </Row>
          <Row label={t('cashStatus')}>{t(atm.cashStatus)}</Row>
          <Row label={t('services')}>{atm.services.map((s) => t(s)).join(lang === 'ar' ? '، ' : ', ') || '—'}</Row>
          <Row label={t('lastHeartbeat')}>{atm.lastHeartbeat ? timeAgo(atm.lastHeartbeat, dict) : '—'}</Row>
          <Row label={t('coords')}><span dir="ltr">{atm.latitude}, {atm.longitude}</span></Row>
        </dl>

        <h3 className="font-bold mt-8 mb-3 text-sm">{t('recentHeartbeats')}</h3>
        <ul className="space-y-2 text-xs text-slate-600">
          {heartbeats.length === 0 && <li className="text-slate-400">{t('loading')}</li>}
          {heartbeats.map((h, i) => (
            <li key={i} className="flex justify-between border-b border-slate-50 pb-2">
              <span>{t(h.status)} · {t(h.cashStatus)}</span>
              <span className="text-slate-400" dir="ltr">{formatTime(h.receivedAt, lang)}</span>
            </li>
          ))}
        </ul>
      </aside>
    </div>
  )
}

function Row({ label, children }) {
  return (
    <div className="flex justify-between border-b border-slate-100 pb-3">
      <dt className="text-slate-500">{label}</dt>
      <dd className="font-medium">{children}</dd>
    </div>
  )
}
