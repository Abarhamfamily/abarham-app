import type { ReactNode } from "react";

const navItems = [
  { icon: "explore", label: "اطلاعات سفر" },
  { icon: "app_registration", label: "ثبت‌نام" },
  { icon: "account_balance_wallet", label: "کیف پول" },
];

export function AppShell({ children, active = "app_registration" }: { children: ReactNode; active?: string }) {
  return (
    <div dir="rtl" className="relative flex min-h-screen flex-col overflow-x-hidden pt-16 pb-24 md:pb-0">
      <div className="pointer-events-none fixed inset-0 z-[-1]">
        <div className="absolute inset-0 bg-gradient-to-b from-surface-dim/50 to-surface-dim" />
        <div className="absolute top-[20%] left-[10%] h-96 w-96 rounded-full bg-brand/5 blur-3xl mix-blend-screen" />
      </div>

      {/* Desktop bar */}
      <header className="fixed top-0 z-50 hidden w-full items-center justify-between border-b border-outline-variant/30 bg-surface-dim/60 px-16 py-1 shadow-sm shadow-brand/10 backdrop-blur-xl md:flex">
        <div className="flex items-center gap-6">
          <button aria-label="منو" className="rounded-full p-2 text-brand-fixed transition-colors hover:bg-brand/10 active:scale-95">
            <span className="material-symbols-outlined text-3xl">menu</span>
          </button>
          <span className="font-display text-3xl font-bold tracking-tighter text-brand-fixed">ABARHAM</span>
        </div>
        <nav className="flex gap-12">
          {navItems.map((item) => (
            <a
              key={item.icon}
              href="#"
              className={`flex items-center gap-1 text-xs font-semibold tracking-[0.05em] transition-colors hover:text-brand ${
                item.icon === active ? "text-brand-fixed" : "text-on-surface-variant"
              }`}
            >
              <span className="material-symbols-outlined">{item.icon}</span> {item.label}
            </a>
          ))}
        </nav>
        <button aria-label="حساب کاربری" className="rounded-full p-2 text-brand-fixed transition-colors hover:bg-brand/10 active:scale-95">
          <span className="material-symbols-outlined text-3xl">account_circle</span>
        </button>
      </header>

      {/* Mobile bar */}
      <header className="fixed top-0 z-50 flex w-full items-center justify-between border-b border-outline-variant/30 bg-surface-dim/60 px-4 py-1 shadow-sm shadow-brand/10 backdrop-blur-xl md:hidden">
        <button aria-label="منو" className="rounded-full p-2 text-brand-fixed transition-colors hover:bg-brand/10 active:scale-95">
          <span className="material-symbols-outlined">menu</span>
        </button>
        <span className="font-display text-2xl font-bold tracking-tighter text-brand-fixed">ABARHAM</span>
        <button aria-label="حساب کاربری" className="rounded-full p-2 text-brand-fixed transition-colors hover:bg-brand/10 active:scale-95">
          <span className="material-symbols-outlined">account_circle</span>
        </button>
      </header>

      {children}

      <nav className="fixed bottom-0 z-50 flex h-12 w-full items-center justify-around rounded-t-xl border-t border-outline-variant/20 bg-surface-container-lowest/80 px-4 shadow-[0_-4px_20px_rgba(78,222,163,0.1)] backdrop-blur-lg md:hidden">
        {navItems.map((item) => (
          <a
            key={item.icon}
            href="#"
            className={`flex flex-col items-center justify-center transition-all duration-200 active:scale-90 ${
              item.icon === active
                ? "min-w-[80px] rounded-full bg-brand-container/20 px-2 py-1 text-brand-fixed"
                : "w-16 text-on-surface-variant/70 hover:text-brand"
            }`}
          >
            <span
              className="material-symbols-outlined mb-1"
              style={item.icon === active ? { fontVariationSettings: "'FILL' 1" } : undefined}
            >
              {item.icon}
            </span>
            <span className="text-[10px] font-semibold tracking-[0.05em]">{item.label}</span>
          </a>
        ))}
      </nav>
    </div>
  );
}
