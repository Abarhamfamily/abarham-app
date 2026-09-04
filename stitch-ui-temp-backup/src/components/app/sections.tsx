import { Link } from "@tanstack/react-router";
import { Icon } from "./icon";
import {
  categories,
  featuredTrips,
  upcomingTrip,
  heroImage,
} from "./data";
import type { Trip } from "./data";

/* ---------- Top bar with greeting ---------- */
export function TopBar() {
  return (
    <header className="px-5 pt-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="grid h-11 w-11 place-items-center rounded-full bg-gradient-to-br from-primary to-accent text-primary-foreground font-bold">
              آ
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 grid h-4 w-4 place-items-center rounded-full bg-amber text-amber-foreground ring-2 ring-card">
              <Icon name="verified" size={12} filled />
            </span>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">سلام، آرش</p>
            <h1 className="text-lg font-bold leading-tight text-foreground">
              آماده‌ای برای ماجراجویی؟
            </h1>
          </div>
        </div>
        <button className="relative grid h-11 w-11 place-items-center rounded-full bg-card text-secondary-foreground shadow-sm ring-1 ring-border/60">
          <Icon name="notifications" size={22} />
          <span className="absolute right-2.5 top-2.5 h-2 w-2 rounded-full bg-amber ring-2 ring-card" />
        </button>
      </div>
    </header>
  );
}

/* ---------- Hero card ---------- */
export function HeroCard() {
  return (
    <section className="px-5 pt-6">
      <div className="relative overflow-hidden rounded-3xl shadow-lg shadow-primary/20">
        <img
          src={heroImage}
          alt="جنگل ماسوله"
          width={1200}
          height={900}
          className="h-56 w-full object-cover sm:h-64"
          fetchPriority="high"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-primary/90 via-primary/45 to-primary/10" />
        <div className="absolute inset-0 flex flex-col justify-end gap-4 p-5">
          <div>
            <p className="flex items-center gap-1.5 text-sm font-medium text-primary-foreground/85">
              <Icon name="explore" size={18} />
              سفر بعدی‌ات کجاست؟
            </p>
            <p className="mt-1 max-w-[18rem] text-balance text-base font-semibold leading-relaxed text-primary-foreground">
              طبیعت بکر ایران در انتظار توست. با راهنمایان مجرب ما همراه شو.
            </p>
          </div>
          <div>
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 rounded-full bg-amber px-5 py-2.5 text-sm font-bold text-amber-foreground shadow-md shadow-amber/30 transition active:scale-95"
            >
              کشف سفرها
              <Icon name="arrow_left_alt" size={20} />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ---------- Category rail ---------- */
export function CategoryRail() {
  return (
    <nav className="pt-6" aria-label="دسته‌بندی سفرها">
      <div className="no-scrollbar flex gap-3 overflow-x-auto px-5 pb-1">
        {categories.map((c) => (
          <button
            key={c.label}
            className="group flex shrink-0 flex-col items-center gap-2"
          >
            <span
              className="grid h-16 w-16 place-items-center rounded-2xl bg-card shadow-sm ring-1 ring-border/60 transition group-active:scale-90"
              style={{ color: c.tint }}
            >
              <Icon name={c.icon} size={28} filled />
            </span>
            <span className="text-xs font-medium text-muted-foreground">
              {c.label}
            </span>
          </button>
        ))}
      </div>
    </nav>
  );
}

/* ---------- Section heading ---------- */
function SectionHead({
  title,
  action,
}: {
  title: string;
  action?: string;
}) {
  return (
    <div className="mb-3 flex items-center justify-between px-5">
      <h2 className="text-base font-bold text-foreground">{title}</h2>
      {action && (
        <button className="flex items-center gap-0.5 text-xs font-semibold text-primary">
          {action}
          <Icon name="arrow_back_ios" size={14} />
        </button>
      )}
    </div>
  );
}

/* ---------- Upcoming trip card ---------- */
export function UpcomingTrip() {
  return (
    <section className="pt-7">
      <SectionHead title="سفر پیش رو" />
      <div className="mx-5 overflow-hidden rounded-3xl bg-card shadow-md shadow-primary/10 ring-1 ring-border/50">
        <div className="relative h-40 w-full overflow-hidden">
          <img
            src={upcomingTrip.image}
            alt={upcomingTrip.title}
            width={800}
            height={600}
            loading="lazy"
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-card via-card/10 to-transparent" />
          <span className="absolute right-4 top-4 inline-flex items-center gap-1 rounded-full bg-amber px-2.5 py-1 text-[11px] font-bold text-amber-foreground shadow">
            <Icon name="verified" size={14} filled />
            ثبت‌نام قطعی
          </span>
        </div>
        <div className="space-y-3 p-5">
          <h3 className="text-lg font-bold text-foreground">
            {upcomingTrip.title}
          </h3>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1 text-amber">
              <Icon name="schedule" size={16} />
              {upcomingTrip.startsIn}
            </span>
            <span className="inline-flex items-center gap-1">
              <Icon name="calendar_month" size={16} />
              {upcomingTrip.dates}
            </span>
            <span className="inline-flex items-center gap-1">
              <Icon name="group" size={16} />
              {upcomingTrip.companions}
            </span>
          </div>
          <p className="text-sm leading-relaxed text-muted-foreground">
            {upcomingTrip.description}
          </p>
          <div className="flex gap-2 pt-1">
            <Link
              to="/"
              className="flex flex-1 items-center justify-center gap-1.5 rounded-2xl bg-primary px-4 py-2.5 text-sm font-bold text-primary-foreground transition active:scale-[0.98]"
            >
              <Icon name="list_alt" size={18} />
              مشاهده بلیت و جزئیات
            </Link>
            <button className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-secondary text-secondary-foreground transition active:scale-90">
              <Icon name="backpack" size={22} />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ---------- Featured trips ---------- */
export function FeaturedRail() {
  return (
    <section className="pt-7">
      <SectionHead title="پیشنهادهای ویژه" action="مشاهده همه" />
      <div className="no-scrollbar flex gap-4 overflow-x-auto px-5 pb-1">
        {featuredTrips.map((trip) => (
          <TripCard key={trip.id} trip={trip} />
        ))}
      </div>
    </section>
  );
}

function TripCard({ trip }: { trip: Trip }) {
  return (
    <article className="flex w-64 shrink-0 flex-col overflow-hidden rounded-3xl bg-card shadow-md shadow-primary/10 ring-1 ring-border/50">
      <div className="relative h-36 w-full overflow-hidden">
        <img
          src={trip.image}
          alt={trip.title}
          width={800}
          height={600}
          loading="lazy"
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/55 to-transparent" />
        <span className="absolute right-3 top-3 inline-flex items-center gap-1 rounded-full bg-card/90 px-2.5 py-1 text-[11px] font-bold text-amber backdrop-blur">
          <Icon name="timer" size={14} />
          {trip.duration}
        </span>
      </div>
      <div className="flex flex-1 flex-col gap-3 p-4">
        <div>
          <h3 className="text-base font-bold leading-tight text-foreground">
            {trip.title}
          </h3>
          <div className="mt-1.5 flex items-center gap-2 text-[11px]">
            <DifficultyBadge level={trip.difficulty} />
            <span className="text-muted-foreground">{trip.activity}</span>
          </div>
        </div>
        <div className="mt-auto flex items-center justify-between">
          <span className="text-sm font-extrabold text-foreground">
            {trip.price}
            <span className="mr-1 text-[10px] font-normal text-muted-foreground">
              تومان
            </span>
          </span>
          {trip.full ? (
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-destructive">
              <Icon name="block" size={14} />
              تکمیل ظرفیت
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-primary">
              <Icon name="group_add" size={14} />
              {trip.capacity}
            </span>
          )}
        </div>
      </div>
    </article>
  );
}

function DifficultyBadge({
  level,
}: {
  level: Trip["difficulty"];
}) {
  const tone =
    level === "آسان"
      ? "text-primary bg-primary/10"
      : level === "متوسط"
        ? "text-amber bg-amber/15"
        : "text-destructive bg-destructive/10";
  return (
    <span
      className={`inline-flex items-center rounded-md px-1.5 py-0.5 text-[11px] font-semibold ${tone}`}
    >
      {level}
    </span>
  );
}

/* ---------- Community section ---------- */
export function Community() {
  return (
    <section className="px-5 pt-8">
      <div className="overflow-hidden rounded-3xl bg-gradient-to-br from-primary to-accent p-6 text-primary-foreground shadow-lg shadow-primary/25">
        <span className="grid h-12 w-12 place-items-center rounded-2xl bg-primary-foreground/15">
          <Icon name="diversity_3" size={26} filled />
        </span>
        <h2 className="mt-4 text-lg font-bold leading-tight">
          آبرهام فراتر از یک آژانس، یک جامعه است
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-primary-foreground/85">
          ما فقط سفر نمی‌رویم؛ ما در کنار هم زندگی در طبیعت را تجربه می‌کنیم. به
          جامعه هزاران طبیعت‌گرد ایرانی بپیوندید، داستان‌هایتان را به اشتراک
          بگذارید و همسفران جدید پیدا کنید.
        </p>
        <Link
          to="/"
          className="mt-4 inline-flex items-center gap-1.5 rounded-full bg-primary-foreground px-5 py-2.5 text-sm font-bold text-primary transition active:scale-95"
        >
          مشاهده داستان‌های جامعه
          <Icon name="arrow_back_ios" size={14} />
        </Link>
      </div>
    </section>
  );
}
