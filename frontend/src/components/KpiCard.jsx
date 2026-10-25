export default function KpiCard({ value, label, color }) {
  return (
    <div className="bg-white/80 rounded-3xl p-6 shadow-sm">
      <div className={`text-4xl font-bold ${color}`} dir="ltr" style={{ textAlign: 'right' }}>{value}</div>
      <div className="text-sm text-slate-500 mt-2">{label}</div>
    </div>
  )
}
