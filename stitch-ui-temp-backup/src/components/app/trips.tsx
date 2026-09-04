import { useState } from "react";
import { Icon } from "./icon";
import tripShovi from "@/assets/trip-shovi.jpg";
import tripBadab from "@/assets/trip-badab.jpg";

type TripItem = {
  id: string;
  title: string;
  image: string;
  price: string;
  duration: string;
  dates: string;
  difficulty: "آسان" | "متوسط" | "سخت";
  seatsLeft?: string;
  full?: boolean;
};

const trips: TripItem[] = [
  {
    id: "shovi",
    title: "آبشار شوی و دزفول",
    image: tripShovi,
    price: "۱,۵۰۰,۰۰۰",
    duration: "۳ روز",
    dates: "۱۲ تا ۱۴ اردیبهشت",
    difficulty: "متوسط",
    seatsLeft: "۴ صندلی باقی‌مانده",
  },
  {
    id: "badab",
    title: "چشمه‌های باداب سورت",
    image: tripBadab,
    price: "۲,۲۰۰,۰۰۰",
    duration: "۲ روز",
    dates: "۲۰ تا ۲۱ اردیبهشت",
    difficulty: "متوسط",
    full: true,
  },
];

const activeFilters = ["سختی: متوسط", "نوع: طبیعت‌گردی"];
const filterButtons = ["تاریخ", "قیمت"];

export function TripsScreen() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState(activeFilters);
  const [favorites, setFavorites] = useState<Set<string>>(new Set());

  const toggleFavorite = (id: string) =>
    setFavorites((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const visible = trips.filter((t) => t.title.includes(query.trim()));

  return (
    <>
      {/* Top app bar */}
      <header className="flex items-center justify-between px-5 pt-6">
        <h1 className="text-xl font-bold text-foreground">سفرها</h1>
        <button
          aria-label="نقشه"
          className="grid h-11 w-11 place-items-center rounded-full bg-card text-secondary-foreground shadow-sm ring-1 ring-border/60 transition active:scale-90"
        >
          <Icon name="map" size={22} />
        </button>
      </header>

      {/* Search */}
      <div className="flex gap-2 px-5 pt-4">
        <label className="flex flex-1 items-center gap-2 rounded-2xl bg-card px-4 py-3 shadow-sm ring-1 ring-border/60 focus-within:ring-2 focus-within:ring-primary">
          <Icon name="search" size={20} className="text-muted-foreground" />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="جستجوی مقصد، شهر یا سفر..."
            className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
          />
        </label>
        <button
          aria-label="فیلترها"
          className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-primary text-primary-foreground shadow-md shadow-primary/25 transition active:scale-90"
        >
          <Icon name="tune" size={22} />
        </button>
      </div>

      {/* Filter chips */}
      <div className="no-scrollbar flex gap-2 overflow-x-auto px-5 pt-4 pb-1">
        {filters.map((f) => (
          <span
            key={f}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-primary/10 py-1.5 pr-3 pl-2 text-xs font-semibold text-primary"
          >
            {f}
            <button
              aria-label={`حذف فیلتر ${f}`}
              onClick={() => setFilters(filters.filter((x) => x !== f))}
              className="grid h-4 w-4 place-items-center rounded-full transition hover:bg-primary/15"
            >
              <Icon name="close" size={14} />
            </button>
          </span>
        ))}
        {filterButtons.map((f) => (
          <button
            key={f}
            className="inline-flex shrink-0 items-center gap-1 rounded-full bg-card px-3 py-1.5 text-xs font-semibold text-secondary-foreground shadow-sm ring-1 ring-border/60 transition active:scale-95"
          >
            {f}
            <Icon name="keyboard_arrow_down" size={16} />
          </button>
        ))}
      </div>

      {/* Trip cards */}
      <section className="space-y-4 px-5 pt-5">
        {visible.length === 0 && (
          <p className="pt-16 text-center text-sm text-muted-foreground">
            سفری مطابق جستجوی شما پیدا نشد
          </p>
        )}
        {visible.map((trip) => (
          <TripListCard
            key={trip.id}
            trip={trip}
            favorite={favorites.has(trip.id)}
            onToggleFavorite={() => toggleFavorite(trip.id)}
          />
        ))}
      </section>
    </>
  );
}

function TripListCard({
  trip,
  favorite,
  onToggleFavorite,
}: {
  trip: TripItem;
  favorite: boolean;
  onToggleFavorite: () => void;
}) {
  return (
    <article className="overflow-hidden rounded-3xl bg-card shadow-md shadow-primary/10 ring-1 ring-border/50">
      <div className="relative h-44 w-full overflow-hidden">
        <img
          src={trip.image}
          alt={trip.title}
          width={1024}
          height={1024}
          loading="lazy"
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent" />
        <span className="absolute right-3 top-3 inline-flex items-center rounded-full bg-card/90 px-3 py-1.5 text-xs font-extrabold text-foreground backdrop-blur">
          {trip.price}
          <span className="mr-1 text-[10px] font-normal text-muted-foreground">
            تومان
          </span>
        </span>
        <button
          aria-label="علاقه‌مندی"
          onClick={onToggleFavorite}
          className={`absolute left-3 top-3 grid h-9 w-9 place-items-center rounded-full backdrop-blur transition active:scale-90 ${
            favorite
              ? "bg-amber text-amber-foreground"
              : "bg-card/90 text-muted-foreground"
          }`}
        >
          <Icon name="favorite" size={18} filled={favorite} />
        </button>
        <span className="absolute bottom-3 right-3 inline-flex items-center gap-1 rounded-full bg-black/40 px-2.5 py-1 text-[11px] font-semibold text-white backdrop-blur">
          <Icon name="schedule" size={14} />
          {trip.duration}
        </span>
      </div>

      <div className="space-y-3 p-4">
        <div className="flex items-start justify-between gap-2">
          <h2 className="text-base font-bold leading-tight text-foreground">
            {trip.title}
          </h2>
          <span className="inline-flex shrink-0 items-center rounded-md bg-amber/15 px-1.5 py-0.5 text-[11px] font-semibold text-amber">
            {trip.difficulty}
          </span>
        </div>
        <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Icon name="calendar_today" size={16} />
          {trip.dates}
        </p>
        <div className="flex items-center justify-between border-t border-border/60 pt-3">
          {trip.full ? (
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-destructive">
              <Icon name="block" size={14} />
              تکمیل ظرفیت
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-primary">
              <Icon name="group_add" size={14} />
              {trip.seatsLeft}
            </span>
          )}
          <button
            disabled={trip.full}
            className={`inline-flex items-center gap-1 rounded-full px-4 py-2 text-xs font-bold transition active:scale-95 ${
              trip.full
                ? "cursor-not-allowed bg-muted text-muted-foreground"
                : "bg-primary text-primary-foreground shadow-sm shadow-primary/25"
            }`}
          >
            جزئیات
            <Icon name="arrow_forward" size={16} />
          </button>
        </div>
      </div>
    </article>
  );
}
