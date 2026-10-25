import { create } from 'zustand'

const saved = (() => {
  try { return JSON.parse(sessionStorage.getItem('sars_session')) } catch { return null }
})()

const persist = (s) => {
  try { sessionStorage.setItem('sars_session', JSON.stringify(s)) } catch {}
}

export const useAuthStore = create((set) => ({
  accessToken: saved?.accessToken ?? null,
  refreshToken: saved?.refreshToken ?? null,
  user: saved?.user ?? null,

  setSession: ({ access, refresh, user }) => {
    persist({ accessToken: access, refreshToken: refresh, user })
    set({ accessToken: access, refreshToken: refresh, user })
  },
  setAccessToken: (access) => set({ accessToken: access }),
  logout: () => {
    try { sessionStorage.removeItem('sars_session') } catch {}
    set({ accessToken: null, refreshToken: null, user: null })
  },
}))