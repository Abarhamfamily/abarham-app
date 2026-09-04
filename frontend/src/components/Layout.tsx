import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { BottomNav } from './layout/BottomNav'

export default function Layout() {
  const location = useLocation()
  const { user, clearAuth } = useAuthStore()
  
  const path = location.pathname
  let activeRoute: 'home' | 'trips' | 'wallet' | 'profile' = 'home'
  if (path.startsWith('/trips')) activeRoute = 'trips'
  else if (path.startsWith('/wallet')) activeRoute = 'wallet'
  else if (path.startsWith('/profile')) activeRoute = 'profile'

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-card/85 backdrop-blur-lg border-b border-border/70">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="avatar">
              آ
            </div>
            <div>
              {user ? (
                <>
                  <p className="text-sm text-muted-foreground">سلام، {user.full_name}</p>
                  <h1 className="text-lg font-bold text-foreground">آبرهام</h1>
                </>
              ) : (
                <h1 className="text-lg font-bold text-foreground">آبرهام</h1>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <Link to="/profile" className="btn btn-outline">
                  پروفایل
                </Link>
                <button onClick={clearAuth} className="btn btn-secondary">
                  خروج
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn-primary">ورود</Link>
                <Link to="/register" className="btn btn-outline">ثبت‌نام</Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 pb-20">
        <div className="container mx-auto py-6">
          <Outlet />
        </div>
      </main>

      {/* Bottom navigation */}
      <BottomNav
        active={activeRoute}
        onChange={() => {
          // Navigation is handled by Link components
        }}
      />
    </div>
  )
}