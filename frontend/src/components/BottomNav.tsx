import { Link, useLocation } from 'react-router-dom';

export default function BottomNav() {
  const location = useLocation();
  const pathname = location.pathname;

  const routes = [
    { path: '/', label: 'خانه', icon: '🏠' },
    { path: '/trips', label: 'سفرها', icon: '🗺️' },
    { path: '/wallet', label: 'کیف پول', icon: '💰' },
    { path: '/profile', label: 'پروفایل', icon: '👤' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-card/95 backdrop-blur-lg border-t border-border/70">
      <div className="flex items-stretch justify-around px-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] pt-2">
        {routes.map((route) => {
          const isActive = pathname === route.path ||
            (route.path === '/' && pathname === '/') ||
            (route.path !== '/' && pathname.startsWith(route.path));
          return (
            <Link
              key={route.path}
              to={route.path}
              className="flex flex-1 flex-col items-center gap-1 py-1"
            >
              <span
                className={`grid h-9 w-12 place-items-center rounded-full transition ${isActive ? 'bg-primary/12 text-primary' : 'text-muted-foreground'}`}
              >
                <span className="text-[22px]">{route.icon}</span>
              </span>
              <span
                className={`text-[11px] transition ${isActive ? 'font-bold text-primary' : 'font-medium text-muted-foreground'}`}
              >
                {route.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}