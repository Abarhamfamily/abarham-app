import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAdminAuthStore } from '../store/adminAuthStore'
import { adminLogout } from '../api/auth'

const navItems = [
  { to: '/', label: 'داشبورد', end: true },
  { to: '/users', label: 'کاربران' },
  { to: '/trips', label: 'تورها' },
  { to: '/registrations', label: 'ثبت‌نام‌ها' },
  { to: '/payments', label: 'پرداخت‌ها' },
  { to: '/wallet', label: 'کیف پول' },
  { to: '/notifications', label: 'اعلان‌ها' },
]

export default function AdminLayout() {
  const { admin, clearAuth } = useAdminAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await adminLogout()
    } catch {
      // حتی اگر درخواست logout fail شود، سمت کلاینت خارج می‌شویم
    }
    clearAuth()
    navigate('/login')
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside
        style={{
          width: 220,
          background: '#111827',
          color: '#fff',
          padding: 16,
          flexShrink: 0,
        }}
      >
        <h2 style={{ fontSize: 18, marginBottom: 24 }}>پنل مدیریت ابرهام</h2>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              style={({ isActive }) => ({
                padding: '10px 12px',
                borderRadius: 6,
                color: '#fff',
                textDecoration: 'none',
                background: isActive ? '#2563eb' : 'transparent',
                fontSize: 14,
              })}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div style={{ marginTop: 32, borderTop: '1px solid #374151', paddingTop: 16 }}>
          <p style={{ fontSize: 13, color: '#9ca3af', marginBottom: 8 }}>
            {admin?.full_name} ({admin?.role})
          </p>
          <button className="secondary" onClick={handleLogout} style={{ width: '100%' }}>
            خروج
          </button>
        </div>
      </aside>

      <main style={{ flex: 1, padding: 24 }}>
        <Outlet />
      </main>
    </div>
  )
}
