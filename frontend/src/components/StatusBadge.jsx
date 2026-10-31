import { useT } from '../utils/i18n'

const CLS = {
  DELIVERED: 'bg-emerald-50 text-emerald-700',
  PENDING: 'bg-amber-50 text-amber-700',
  FAILED: 'bg-rose-50 text-rose-700',
}

export default function StatusBadge({ status }) {
  const { t } = useT()
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${CLS[status] || 'bg-slate-100 text-slate-600'}`}>
      {t(status)}
    </span>
  )
}
