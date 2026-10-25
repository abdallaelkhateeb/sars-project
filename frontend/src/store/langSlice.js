import { create } from 'zustand'

const saved = (() => {
  try { return localStorage.getItem('sars_lang') } catch { return null }
})()

function apply(lang) {
  document.documentElement.lang = lang
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'
}

const initial = saved === 'en' ? 'en' : 'ar'
apply(initial)

export const useLangStore = create((set) => ({
  lang: initial,
  setLang: (lang) => {
    try { localStorage.setItem('sars_lang', lang) } catch {}
    apply(lang)
    set({ lang })
  },
}))
