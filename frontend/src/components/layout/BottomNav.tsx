import { Link } from 'react-router-dom';

type Route = 
  | "home"
  | "trips"
  | "wallet"
  | "profile";

type NavItem = {
  icon: string;
  label: string;
  route: Route;
};

const items: NavItem[] = [
  { icon: "🏠", label: "خانه", route: "home" },
  { icon: "🧭", label: "سفرها", route: "trips" },
  { icon: "💰", label: "کیف سفر", route: "wallet" },
  { icon: "👤", label: "پروفایل", route: "profile" },
];

const routePaths: Record<Route, string> = {
  home: "/",
  trips: "/trips",
  wallet: "/wallet",
  profile: "/profile",
};

export function BottomNav({
  active,
  onChange,
}: {
  active: Route;
  onChange: (route: Route) => void;
}) {
  return (
    <nav className="sticky bottom-0 z-20 border-t border-border/70 bg-card/85 backdrop-blur-lg">
      <div className="flex items-stretch justify-around px-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] pt-2">
        {items.map((item) => {
          const isActive = item.route === active;
          return (
            <Link
              key={item.route}
              to={routePaths[item.route]}
              onClick={() => onChange(item.route)}
              className="flex flex-1 flex-col items-center gap-1 py-1"
            >
              <span
                className={`grid h-9 w-12 place-items-center rounded-full transition ${
                  isActive
                    ? "bg-primary/12 text-primary"
                    : "text-muted-foreground"
                }`}
              >
                <span className="text-[22px]">{item.icon}</span>
              </span>
              <span
                className={`text-[11px] transition ${
                  isActive
                    ? "font-bold text-primary"
                    : "font-medium text-muted-foreground"
                }`}
              >
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}