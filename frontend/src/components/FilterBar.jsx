import { useAtmsStore } from '../store/atmsSlice'
import { useT } from '../utils/i18n'

const FILTERS = [
  { key: 'ALL', label: 'fAll' },
  { key: 'ONLINE', label: 'fOnline' },
  { key: 'LOW_CASH', label: 'fLowCash' },
  { key: 'OFFLINE', label: 'fOffline' },
]

export default function FilterBar() {
  const { filter, setFilter } = useAtmsStore()
  const { t } = useT()
  return (
    <div className="bg-white/80 rounded-3xl p-5 shadow-sm">
      <h3 className="font-bold mb-3">{t('filter')}</h3>
      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-4 py-2 rounded-full text-sm transition ${
              filter === f.key ? 'bg-slate-900 text-white' : 'bg-slate-50 text-slate-500 hover:bg-slate-100'
            }`}
          >
            {t(f.label)}
          </button>
        ))}
      </div>
    </div>
  )
}
