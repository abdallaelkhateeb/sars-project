export function formatTime(iso, lang = 'en') {
  return new Date(iso).toLocaleString(lang === 'ar' ? 'ar-EG' : 'en-GB', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit',
  })
}

export function timeAgo(iso, dict) {
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000)
  if (mins < 1) return dict.now
  if (mins < 60) return dict.minAgo(mins)
  const hrs = Math.round(mins / 60)
  return hrs < 24 ? dict.hrAgo(hrs) : dict.dayAgo(Math.round(hrs / 24))
}
