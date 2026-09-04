import { Icon } from "./icon";

export type Route =
  | "home"
  | "trips"
  | "wallet"
  | "notifications"
  | "profile";

type NavItem = {
  icon: string;
  label: string;
  route: Route;
};

const items: NavItem[] = [
  { icon: "home", label: "خانه", route: "home" },
  { icon: "explore", label: "سفرها", route: "trips" },
  { icon: "account_balance_wallet", label: "کیف سفر", route: "wallet" },
  { icon: "notifications", label: "اعلان‌ها", route: "notifications" },
  { icon: "person", label: "پروفایل", route: "profile" },
];

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
            <button
              key={item.route}
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
                <Icon
                  name={item.icon}
                  size={24}
                  filled={isActive}
                />
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
            </button>
          );
        })}
      </div>
    </nav>
  );
}
