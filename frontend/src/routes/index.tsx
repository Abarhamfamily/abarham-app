import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AppShell } from "@/components/AppShell";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "ثبت‌نام سفر اکوتوریسم | ABARHAM" },
      {
        name: "description",
        content:
          "ثبت‌نام در سفر اکوتوریسم ابرهام: نام، کد ملی و شماره موبایل خود را وارد کنید و وضعیت ثبت‌نام و کد پیگیری را ببینید.",
      },
      { property: "og:title", content: "ثبت‌نام سفر اکوتوریسم | ABARHAM" },
      {
        property: "og:description",
        content: "جای خود را برای سفر اکوتوریسم آینده ابرهام رزرو کنید.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

const fields = [
  { id: "fullName", label: "نام و نام خانوادگی", icon: "person", placeholder: "نام خود را وارد کنید", type: "text" },
  { id: "nationalId", label: "کد ملی", icon: "badge", placeholder: "فقط اعداد", type: "text", inputMode: "numeric" as const },
  { id: "mobileNumber", label: "شماره موبایل", icon: "smartphone", placeholder: "۰۹۱۲۰۰۰۰۰۰۰", type: "tel", dir: "ltr" },
];

function Index() {
  const [values, setValues] = useState<Record<string, string>>({});

  return (
    <AppShell>
      <main className="mx-auto mt-6 flex w-full max-w-7xl flex-grow flex-col gap-6 px-4 py-6 md:mt-12 md:flex-row md:px-16 md:py-12">
        <section className="order-2 flex flex-1 flex-col gap-3 md:order-1">
          <div className="mb-1">
            <h1 className="mb-1 font-display text-2xl font-semibold text-on-surface">ثبت‌نام در برنامه</h1>
            <p className="text-base text-on-surface-variant">جای خود را برای سفر اکوتوریسم آینده رزرو کنید.</p>
          </div>

          <form
            className="glass-panel flex flex-col gap-3 rounded-lg p-3"
            onSubmit={(e) => {
              e.preventDefault();
            }}
          >
            {fields.map((f) => (
              <div key={f.id} className="flex flex-col gap-1">
                <label className="text-xs font-semibold tracking-wider text-on-surface-variant uppercase" htmlFor={f.id}>
                  {f.label}
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute top-1/2 right-3 -translate-y-1/2 text-on-surface-variant">
                    {f.icon}
                  </span>
                  <input
                    id={f.id}
                    type={f.type}
                    dir={f.dir}
                    inputMode={f.inputMode}
                    placeholder={f.placeholder}
                    value={values[f.id] ?? ""}
                    onChange={(e) => setValues((v) => ({ ...v, [f.id]: e.target.value }))}
                    className="w-full rounded-md border border-outline-variant bg-transparent py-2 pr-10 pl-4 text-base text-on-surface transition-colors placeholder:text-on-surface-variant/50 focus:border-brand focus:ring-1 focus:ring-brand focus:outline-none"
                  />
                </div>
              </div>
            ))}

            <button
              type="submit"
              className="mt-1 flex items-center justify-center gap-1 rounded-md bg-brand px-4 py-2.5 text-xs font-semibold tracking-wider text-on-brand uppercase shadow-[0_0_10px_rgba(78,222,163,0.2)] transition-colors hover:bg-brand-fixed active:scale-[0.98]"
            >
              <span>ثبت‌نام در برنامه</span>
              <span className="material-symbols-outlined text-sm">arrow_back</span>
            </button>
          </form>
        </section>

        <aside className="order-1 flex w-full flex-col gap-3 md:order-2 md:w-1/3">
          <div className="glass-panel group relative flex flex-col gap-1 overflow-hidden rounded-lg p-3">
            <div className="absolute inset-0 bg-accent2/5 opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
            <h2 className="text-xs font-semibold tracking-wider text-on-surface-variant uppercase">وضعیت ثبت‌نام شما</h2>
            <div className="mt-1 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full border border-accent2/30 bg-accent2-container/20">
                <span className="material-symbols-outlined text-xl text-accent2" style={{ fontVariationSettings: "'FILL' 1" }}>
                  hourglass_empty
                </span>
              </div>
              <div>
                <div className="text-lg font-semibold text-accent2">در انتظار تایید</div>
                <div className="mt-0.5 flex items-center gap-1 text-xs font-semibold tracking-[0.05em] text-on-surface-variant">
                  <span className="material-symbols-outlined text-xs">tag</span> کد پیگیری: AB-1024
                </div>
              </div>
            </div>
          </div>

          <div className="glass-panel relative hidden h-32 overflow-hidden rounded-lg border-outline-variant/30 md:block">
            <img
              className="h-full w-full object-cover opacity-80 mix-blend-luminosity transition-all duration-700 hover:mix-blend-normal"
              alt="جنگل مه‌گرفته در غروب، فضای سفر اکوتوریسم"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuBnILXpeEQt15oXFPzcVfV7vN6Mm2QRyzJ5-athP5k1ZCm1cQdw8bcdenZz46akArwSS3zamZDo5Ktau-af8IxzYShK_88eobsKIWIbMUqbDpxpXnJ6CJ-qwt6fuzXD-OpCh_bu-7280C9-6N0IJJu3kqoRdAQBMU33H6_VzZCXrnRaR7ppFABrE_BOwO3XcqFWRsemMNFvTV5RQDIFes0lXT1EphZUgDN-FtL1ShXiUg-az1I_xMWoOQ"
              loading="lazy"
            />
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-surface-dim to-transparent" />
          </div>
        </aside>
      </main>
    </AppShell>
  );
}
