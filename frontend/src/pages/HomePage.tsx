import { Link } from 'react-router-dom'
import { useTrips } from '../api/trips'
import { Button } from '@/components/ui/Button'
import { Typography } from '@/components/ui/Typography'
import { useAuthStore } from '../store/authStore'

// Static categories data (no API endpoint for categories)
const categories = [
  { icon: '🌲', label: 'جنگل' },
  { icon: '🏕️', label: 'کمپ' },
  { icon: '🏔️', label: 'دره‌نوردی' },
  { icon: '⛰️', label: 'کوهنوردی' },
]

// ============================================
// 📌 Section Head Component
// ============================================
function SectionHead({ title, action }: { title: string; action?: string }) {
  return (
    <div className="mb-3 flex items-center justify-between px-5">
      <h2 className="text-base font-bold text-foreground">{title}</h2>
      {action && (
        <Link
          to="/trips"
          className="flex items-center gap-0.5 text-xs font-semibold text-primary hover:underline"
        >
          {action}
          <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 18l6-6-6-6" />
          </svg>
        </Link>
      )}
    </div>
  )
}

// ============================================
// 📌 Upcoming Trip Component
// ============================================
export function UpcomingTrip({ trip }: { trip: any }) {
  // محاسبه تاریخ‌ها از start_date و end_date
  const startDate = new Date(trip.start_date)
  const endDate = new Date(trip.end_date)
  const duration = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))
  
  const startDateStr = startDate.toLocaleDateString('fa-IR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
  const endDateStr = endDate.toLocaleDateString('fa-IR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })

  return (
    <section className="pt-7">
      <div className="relative h-40 w-full overflow-hidden rounded-3xl shadow-lg shadow-primary/20">
        <img
          src={trip.images?.[0] || ''}
          alt={trip.title}
          width={800}
          height={400}
          className="h-full w-full object-cover"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/55 to-transparent" />
        
        <div className="absolute right-3 top-3 inline-flex items-center gap-1 rounded-full bg-card/90 px-2.5 py-1 text-[11px] font-bold text-amber backdrop-blur">
          {/* Verified SVG Icon */}
          <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          ثبت‌نام قطعی
        </div>
      </div>
      
      <div className="bg-card border-border shadow-sm mt-3 rounded-2xl">
        <div className="p-5">
          <h3 className="text-lg font-bold text-foreground mb-3">
            {trip.title}
          </h3>
          
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-muted-foreground mb-4">
            <span className="inline-flex items-center gap-1 text-amber">
              {/* Clock SVG Icon */}
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              {duration} روز
            </span>
            <span className="inline-flex items-center gap-1">
              {/* Calendar SVG Icon */}
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              {startDateStr} تا {endDateStr}
            </span>
            <span className="inline-flex items-center gap-1">
              {/* Users SVG Icon */}
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
              {trip.remaining_capacity || 0} نفر
            </span>
          </div>
          
          <p className="text-sm leading-relaxed text-muted-foreground mb-4 line-clamp-2">
            {trip.description}
          </p>
          
          <div className="flex gap-2">
            <Link
              to={`/trips/${trip.id}`}
              className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-full bg-primary px-5 py-2.5 text-sm font-bold text-primary-foreground shadow-md shadow-primary/30 transition active:scale-95"
            >
              مشاهده بلیت و جزئیات
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 18l6-6-6-6"/>
              </svg>
            </Link>
            
            <button className="grid h-11 w-11 place-items-center rounded-full bg-muted/50 hover:bg-muted/70 transition-colors">
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4-4v2M12 11a4 4 0 1 1 0-8 4 4 0 0 1 0 8z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}

// ============================================
// 📌 TopBar Component
// ============================================
export function TopBar() {
  const { user } = useAuthStore()
  const userName = user?.full_name || 'کاربر'
  const firstLetter = userName.charAt(0)

  return (
    <header className="px-5 pt-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="grid h-11 w-11 place-items-center rounded-full bg-gradient-to-br from-primary to-accent text-primary-foreground font-bold">
              {firstLetter}
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 grid h-4 w-4 place-items-center rounded-full bg-amber text-amber-foreground ring-2 ring-card">
              <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </span>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">سلام، {userName}</p>
            <h1 className="text-lg font-bold leading-tight text-foreground">آماده‌ای برای ماجراجویی؟</h1>
          </div>
        </div>
        <button className="relative grid h-11 w-11 place-items-center rounded-full bg-card text-secondary-foreground shadow-sm ring-1 ring-border/60">
          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 8a6 6 0 0 0-12 0v4a5 5 0 0 0-5 5v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a5 5 0 0 0-5-5V8zm-4 8v-1a2 2 0 0 0-4 0v1"/>
          </svg>
          <span className="absolute right-2.5 top-2.5 h-2 w-2 rounded-full bg-amber ring-2 ring-card" />
        </button>
      </div>
    </header>
  )
}

// ============================================
// 📌 HomePage Main Component
// ============================================
export default function HomePage() {
  const { trips, loading, error } = useTrips()

  const featuredTrip = trips[0]
  const otherTrips = trips.slice(1, 6)

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4">
        <Typography as="h2" variant="h2" className="mb-4">
          خطا در بارگذاری اطلاعات
        </Typography>
        <Typography variant="p" className="text-muted-foreground mb-6">
          لطفاً اتصال اینترنت خود را بررسی کنید
        </Typography>
        <Button variant="default" asChild>
          <Link to="/trips">مشاهده تورها</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="min-h-screen pb-20">
      <TopBar />
      
      {/* ==========================================
          Hero Section
          ========================================== */}
      <section className="px-5 pt-6">
        <div className="relative overflow-hidden rounded-3xl shadow-lg shadow-primary/20">
          <img
            src={featuredTrip?.images?.[0] || ''}
            alt={featuredTrip?.title || 'طبیعت بکر ایران'}
            width={1200}
            height={900}
            className="h-56 w-full object-cover sm:h-64"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-primary/90 via-primary/45 to-primary/10" />
          <div className="absolute inset-0 flex flex-col justify-end gap-4 p-5">
            <div>
              <p className="flex items-center gap-1.5 text-sm font-medium text-primary-foreground/85">
                {/* Compass SVG Icon */}
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
                </svg>
                سفر بعدی‌ات کجاست؟
              </p>
              <p className="mt-1 max-w-[18rem] text-balance text-base font-semibold leading-relaxed text-primary-foreground">
                طبیعت بکر ایران در انتظار توست. با راهنمایان مجرب ما همراه شو.
              </p>
            </div>
            <div>
              <Link
                to="/trips"
                className="inline-flex items-center gap-1.5 rounded-full bg-amber px-5 py-2.5 text-sm font-bold text-amber-foreground shadow-md shadow-amber/30 transition active:scale-95"
              >
                کشف سفرها
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 18l6-6-6-6"/>
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ==========================================
          Upcoming Trip Section
          ========================================== */}
      {trips.length > 0 && (
        <section className="px-5 pt-6">
          <UpcomingTrip trip={trips[0]} />
        </section>
      )}

      {/* ==========================================
          Categories Section
          ========================================== */}
      <nav className="pt-6" aria-label="دسته‌بندی سفرها">
        <div className="no-scrollbar flex gap-3 overflow-x-auto px-5 pb-1">
          {categories.map((c: { icon: string; label: string }) => (
            <button
              key={c.label}
              className="group flex shrink-0 flex-col items-center gap-2"
            >
              <span className="grid h-16 w-16 place-items-center rounded-2xl bg-card text-3xl shadow-sm ring-1 ring-border/60 transition group-hover:scale-105">
                {c.icon}
              </span>
              <span className="text-xs font-medium text-muted-foreground">
                {c.label}
              </span>
            </button>
          ))}
        </div>
      </nav>

      {/* ==========================================
          Featured Hero Trip
          ========================================== */}
      {featuredTrip && (
        <section className="py-8">
          <div className="container mx-auto px-4">
            <SectionHead title="تور ویژه" action="مشاهده همه" />
            <Link
              to={`/trips/${featuredTrip.id}`}
              className="block bg-card rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow"
            >
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-2xl font-bold text-foreground">{featuredTrip.title}</h3>
                  <span className="badge badge-amber font-semibold text-sm">
                    {featuredTrip.difficulty_level || 'متوسط'}
                  </span>
                </div>
                <p className="text-muted-foreground mb-6">{featuredTrip.destination}</p>
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">شروع</p>
                    <p className="font-semibold">
                      {new Date(featuredTrip.start_date).toLocaleDateString('fa-IR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">قیمت</p>
                    <p className="font-semibold text-amber-600">
                      {featuredTrip.price} تومان
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">ظرفیت</p>
                    <p className="font-semibold">
                      {featuredTrip.remaining_capacity} / {featuredTrip.capacity}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">مدت</p>
                    <p className="font-semibold">
                      {Math.ceil(
                        (new Date(featuredTrip.end_date).getTime() - new Date(featuredTrip.start_date).getTime()) /
                        (1000 * 60 * 60 * 24)
                      )} روز
                    </p>
                  </div>
                </div>
                <div className="pt-4 border-t border-border">
                 <span className="text-primary font-medium">
                   مشاهده جزئیات →
                 </span>
                </div>
              </div>
            </Link>
          </div>
        </section>
      )}

      {/* ==========================================
          Featured Trips Grid
          ========================================== */}
      {otherTrips.length > 0 && (
        <section className="px-5 pt-6">
          <SectionHead title="تورهای برگزیده" action="مشاهده همه" />
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {otherTrips.map((trip) => (
              <Link
                key={trip.id}
                to={`/trips/${trip.id}`}
                className="block"
              >
                <article className="relative overflow-hidden rounded-3xl shadow-lg shadow-primary/20">
                  <img
                    src={trip.images?.[0] || ''}
                    alt={trip.title}
                    width={800}
                    height={600}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/55 to-transparent" />
                  <div className="absolute inset-0 flex flex-col justify-end gap-4 p-5">
                    <div>
                      <h3 className="text-base font-bold leading-tight text-foreground">
                        {trip.title}
                      </h3>
                      <div className="mt-1.5 flex items-center gap-2 text-[11px]">
                        <span className="badge badge-primary text-xs">
                          {trip.difficulty_level}
                        </span>
                        <span className="text-muted-foreground">📍 {trip.destination}</span>
                      </div>
                    </div>
                    <div className="mt-auto flex items-center justify-between">
                      <span className="text-sm font-extrabold text-foreground">
                        {trip.price}
                        <span className="mr-1 text-[10px] font-normal text-muted-foreground"> تومان </span>
                      </span>
                      {trip.remaining_capacity <= 0 ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-destructive">
                          <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                          </svg>
                          تکمیل ظرفیت
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-primary">
                          <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                            <circle cx="9" cy="7" r="4"/>
                            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                          </svg>
                          {trip.remaining_capacity}
                        </span>
                      )}
                    </div>
                  </div>
                </article>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* ==========================================
          Community Section
          ========================================== */}
      <section className="px-5 pt-8">
        <div className="overflow-hidden rounded-3xl bg-gradient-to-br from-primary to-accent p-6 text-primary-foreground shadow-lg shadow-primary/25">
          <span className="grid h-12 w-12 place-items-center rounded-2xl bg-primary-foreground/15">
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
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
            to="/trips"
            className="mt-4 inline-flex items-center gap-1.5 rounded-full bg-primary-foreground px-5 py-2.5 text-sm font-bold text-primary transition active:scale-95"
          >
            کشف سفرها
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </Link>
        </div>
      </section>
    </div>
  )
}