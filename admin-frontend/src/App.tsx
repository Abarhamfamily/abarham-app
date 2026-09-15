import { Routes, Route } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import AdminLayout from './layouts/AdminLayout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UsersPage from './pages/UsersPage'
import UserDetailPage from './pages/UserDetailPage'
import TripsPage from './pages/TripsPage'
import TripFormPage from './pages/TripFormPage'
import RegistrationsPage from './pages/RegistrationsPage'
import PaymentsPage from './pages/PaymentsPage'
import WalletPage from './pages/WalletPage'
import WithdrawalsPage from './pages/WithdrawalsPage'
import NotificationsPage from './pages/NotificationsPage'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AdminLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/users/:id" element={<UserDetailPage />} />
          <Route path="/trips" element={<TripsPage />} />
          <Route path="/trips/new" element={<TripFormPage />} />
          <Route path="/trips/:id" element={<TripFormPage />} />
          <Route path="/registrations" element={<RegistrationsPage />} />
          <Route path="/payments" element={<PaymentsPage />} />
          <Route path="/wallet" element={<WalletPage />} />
          <Route path="/withdrawals" element={<WithdrawalsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
