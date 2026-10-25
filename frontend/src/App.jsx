import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from './store/authSlice'
import Login from './pages/Login'
import LiveMap from './pages/LiveMap'
import Notifications from './pages/Notifications'

function ProtectedRoute({ children }) {
  const token = useAuthStore((s) => s.accessToken)
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/live" element={<ProtectedRoute><LiveMap /></ProtectedRoute>} />
      <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/live" replace />} />
    </Routes>
  )
}
