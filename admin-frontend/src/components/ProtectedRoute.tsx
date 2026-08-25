import { Navigate, Outlet } from 'react-router-dom'
import { useAdminAuthStore } from '../store/adminAuthStore'

export default function ProtectedRoute() {
  const accessToken = useAdminAuthStore((s) => s.accessToken)

  if (!accessToken) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
