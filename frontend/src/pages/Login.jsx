import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Landmark } from 'lucide-react'
import { login } from '../services/api'
import { useAuthStore } from '../store/authSlice'
import { useT } from '../utils/i18n'
import LangSwitch from '../components/LangSwitch'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const setSession = useAuthStore((s) => s.setSession)
  const navigate = useNavigate()
  const { t } = useT()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await login(username, password)
      setSession(data)
      navigate('/live')
    } catch (err) {
      setError(err.message || t('badCredentials'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative">
      <div className="absolute top-4 end-4"><LangSwitch /></div>
      <form onSubmit={handleSubmit} className="bg-white rounded-3xl shadow-xl p-8 w-full max-w-sm">
        <div className="w-14 h-14 rounded-2xl bg-emerald-500 flex items-center justify-center text-white mx-auto mb-4">
          <Landmark size={26} />
        </div>
        <h1 className="text-xl font-bold text-center">{t('loginTitle')}</h1>
        <p className="text-sm text-slate-500 text-center mt-1 mb-6">{t('loginSub')}</p>

        <label className="block text-xs text-slate-500 mb-1">{t('username')}</label>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          dir="ltr"
          placeholder="admin.ops@sars.bank"
          className="w-full rounded-xl border border-slate-200 px-4 py-3 mb-4 outline-none focus:border-emerald-500"
        />

        <label className="block text-xs text-slate-500 mb-1">{t('password')}</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          dir="ltr"
          className="w-full rounded-xl border border-slate-200 px-4 py-3 mb-4 outline-none focus:border-emerald-500"
        />

        {error && <p className="text-sm text-rose-600 mb-3">{error}</p>}

        <button
          disabled={loading}
          className="w-full bg-slate-900 text-white rounded-2xl py-3 font-medium hover:bg-slate-800 disabled:opacity-60"
        >
          {loading ? t('loggingIn') : t('login')}
        </button>
      </form>
    </div>
  )
}
