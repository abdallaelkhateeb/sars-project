import { NavLink, useNavigate } from 'react-router-dom'
import { LogOut, Map, Bell, Landmark } from 'lucide-react'
import { useAuthStore } from '../store/authSlice'
import { useT } from '../utils/i18n'
import LangSwitch from './LangSwitch'

export default function Navbar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const { t } = useT()
  const link = ({ isActive }) =>
    `flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition ${
      isActive ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-white'
    }`

  return (
    <header className="flex items-center justify-between bg-white/70 backdrop-blur rounded-2xl px-5 py-3 shadow-sm mb-6">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-emerald-500 flex items-center justify-center text-white">
          <Landmark size={18} />
        </div>
        <span className="font-bold">SARS</span>
        <nav className="flex gap-2 ms-6">
          <NavLink to="/live" className={link}><Map size={16} />{t('liveMap')}</NavLink>
          <NavLink to="/notifications" className={link}><Bell size={16} />{t('notifications')}</NavLink>
        </nav>
      </div>
      <div className="flex items-center gap-4">
        <LangSwitch />
        <span className="text-sm text-slate-500">{user?.username} · {user?.role}</span>
        <button
          onClick={() => { logout(); navigate('/login') }}
          className="flex items-center gap-2 text-sm text-slate-600 hover:text-rose-600"
        >
          <LogOut size={16} />{t('logout')}
        </button>
      </div>
    </header>
  )
}
