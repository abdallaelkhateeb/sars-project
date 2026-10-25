import { create } from 'zustand'

export const useAtmsStore = create((set) => ({
  atms: [],
  stats: { online: 0, offline: 0, maintenance: 0, lowCash: 0, emptyCash: 0, uptimePercentage: null },
  selectedAtmId: null,
  selectedAtmDetail: null,
  filter: 'ALL',

  setAtms: (atms) => set({ atms }),
  setStats: (stats) => set({ stats }),
  updateAtm: (updated) =>
    set((state) => ({
      atms: state.atms.some((a) => a.id === updated.id)
        ? state.atms.map((a) => (a.id === updated.id ? { ...a, ...updated } : a))
        : [...state.atms, updated],
    })),
  selectAtm: (id) => set({ selectedAtmId: id, selectedAtmDetail: null }),
  setAtmDetail: (detail) => set({ selectedAtmDetail: detail }),
  setFilter: (filter) => set({ filter }),
}))
