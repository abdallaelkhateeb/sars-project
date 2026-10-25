import { useLangStore } from '../store/langSlice'

export default function LangSwitch() {
  const { lang, setLang } = useLangStore()
  return (
    <button
      onClick={() => setLang(lang === 'ar' ? 'en' : 'ar')}
      className="px-3 py-1.5 rounded-full text-xs font-medium bg-white/80 border border-slate-200 text-slate-700 hover:bg-white"
    >
      {lang === 'ar' ? 'English' : 'عربي'}
    </button>
  )
}
