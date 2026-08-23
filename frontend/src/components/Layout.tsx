import { Link, Outlet } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function Layout() {
  const { user, clearAuth } = useAuthStore()

  return (
    <div>
      <nav
        style={{
          display: 'flex',
          gap: 16,
          padding: 16,
          borderBottom: '1px solid #eee',
          marginBottom: 16,
        }}
      >
        <Link to="/">خانه</Link>
        <Link to="/trips">تورها</Link>
        {user ? (
          <>
            <Link to="/profile">پروفایل</Link>
            <Link to="/wallet">کیف پول</Link>
            <button onClick={clearAuth}>خروج</button>
          </>
        ) : (
          <>
            <Link to="/login">ورود</Link>
            <Link to="/register">ثبت‌نام</Link>
          </>
        )}
      </nav>
      <main style={{ padding: '0 16px' }}>
        <Outlet />
      </main>
    </div>
  )
}
