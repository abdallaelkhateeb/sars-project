import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import StatusBadge from '../components/StatusBadge'
import { getNotifications } from '../services/api'
import { useT } from '../utils/i18n'

export default function Notifications() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { t, lang } = useT()

  useEffect(() => {
    getNotifications()
      .then(setRows)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-6xl mx-auto p-4">
      <Navbar />
      <h1 className="text-xl font-bold mb-4">{t('notifLog')}</h1>

      {error && <p className="bg-rose-50 text-rose-700 text-sm rounded-xl p-3 mb-4">{t('loadFailed')} {error}</p>}

      <div className="bg-white/80 rounded-3xl shadow-sm overflow-x-auto">
        <table className="w-full text-sm text-start">
          <thead>
            <tr className="text-slate-500 border-b border-slate-100">
              <th className="p-4 font-medium text-start">{t('colAtm')}</th>
              <th className="p-4 font-medium text-start">{t('colService')}</th>
              <th className="p-4 font-medium text-start">{t('colStatus')}</th>
              <th className="p-4 font-medium text-start">{t('colTime')}</th>
              <th className="p-4 font-medium text-start">{t('colId')}</th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan="5" className="p-6 text-center text-slate-400">{t('loading')}</td></tr>}
            {!loading && rows.length === 0 && <tr><td colSpan="5" className="p-6 text-center text-slate-400">{t('noNotifs')}</td></tr>}
            {rows.map((n) => (
              <tr key={n.id} className="border-b border-slate-50 last:border-0">
                <td className="p-4">{n.atmName}</td>
                <td className="p-4">{t(n.requestedService)}</td>
                <td className="p-4"><StatusBadge status={n.status} /></td>
                <td className="p-4 text-slate-500" dir="ltr">
                  {new Date(n.createdAt).toLocaleTimeString(lang === 'ar' ? 'ar-EG' : 'en-GB', { hour: '2-digit', minute: '2-digit' })}
                </td>
                <td className="p-4 font-mono text-slate-400" dir="ltr">…ntf_{String(n.id).padStart(4, '0')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-slate-400 mt-4">{t('privacy')}</p>
    </div>
  )
}
