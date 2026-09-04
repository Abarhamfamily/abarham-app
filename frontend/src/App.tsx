import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import TripsPage from './pages/TripsPage'
import TripDetailsPage from './pages/TripDetailsPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import WalletPage from './pages/WalletPage'

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/trips" element={<TripsPage />} />
          <Route path="/trips/:id" element={<TripDetailsPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/wallet" element={<WalletPage />} />
        </Route>
      </Routes>
    </div>
  )
}

export default App
