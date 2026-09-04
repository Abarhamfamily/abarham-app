import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchTrip } from '../api/trips'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import React from 'react'

export default function TripDetailsPage() {
  const { id } = useParams<{ id: string }>()

  const { data: trip, isLoading, isError, refetch } = useQuery({
    queryKey: ['trip', id],
    queryFn: () => fetchTrip(id as string),
    enabled: Boolean(id),
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const formatTime = (timeString: string) => {
    const date = new Date(timeString)

    if (Number.isNaN(date.getTime())) {
      return timeString
    }

    return date.toLocaleTimeString('fa-IR', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12 bg-gradient-to-b from-primary/5 to-transparent">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-6" />

        <Typography as="h2" variant="h2" className="mb-3 text-foreground">
          در حال بارگذاری...
        </Typography>

        <Typography as="p" variant="lead" className="text-center">
          اطلاعات تور در حال دریافت است.
        </Typography>
      </div>
    )
  }

  if (isError || !trip) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12 bg-gradient-to-b from-primary/5 to-transparent">
        <div className="w-20 h-20 mb-6 flex items-center justify-center bg-destructive/10 rounded-full">
          <svg
            className="w-10 h-10 text-destructive"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>

        <Typography as="h2" variant="h2" className="mb-3 text-foreground">
          تور یافت نشد
        </Typography>

        <Typography as="p" variant="lead" className="text-center max-w-md">
          تور مورد نظر پیدا نشد یا ممکن است حذف شده باشد.
        </Typography>

        <div className="flex flex-col sm:flex-row gap-3 mt-6">
          <Button variant="outline" onClick={() => refetch()} className="w-full sm:w-auto">
            تلاش مجدد
          </Button>

          <Link to="/trips" className="w-full sm:w-auto">
            <Button variant="default" className="w-full">
              بازگشت به تورها
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  const capacityPercentage =
    trip.capacity > 0
      ? ((trip.capacity - trip.remaining_capacity) / trip.capacity) * 100
      : 0

  const isFull = trip.remaining_capacity <= 0

  return (
    <div className="min-h-screen pb-20 bg-gradient-to-b from-primary/5 to-transparent">
      {/* Top Bar */}
      <header className="border-b border-border/50 bg-card/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <Link
            to="/trips"
            className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:text-primary/80 transition-colors"
          >
            <svg
              className="w-5 h-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M19 12H5" />
              <path d="M12 19l-7-7 7-7" />
            </svg>
            بازگشت به تورها
          </Link>
        </div>
      </header>

      <main className="container mx-auto max-w-4xl px-4 py-8">
        {/* Hero */}
        <section className="mb-8">
          <div className="rounded-3xl bg-gradient-to-br from-primary/10 to-amber/10 p-6 md:p-8 shadow-sm ring-1 ring-border/50">
            <div className="flex flex-col gap-6">
              <div>
                <div className="flex flex-wrap items-center gap-2 mb-3">
                  {trip.difficulty_level && (
                    <span className="inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                      {trip.difficulty_level}
                    </span>
                  )}

                  <span
                    className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                      isFull
                        ? 'bg-destructive/10 text-destructive'
                        : 'bg-primary/10 text-primary'
                    }`}
                  >
                    {isFull ? 'ظرفیت تکمیل شده' : 'ظرفیت موجود'}
                  </span>
                </div>

                <h1 className="text-3xl md:text-4xl font-bold text-foreground leading-tight">
                  {trip.title}
                </h1>

                <div className="flex items-center gap-2 mt-3 text-muted-foreground">
                  <svg
                    className="w-5 h-5 text-primary"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z" />
                    <circle cx="12" cy="10" r="2.5" />
                  </svg>

                  <span>{trip.destination}</span>
                </div>
              </div>

              {/* Capacity */}
              <div className="rounded-2xl bg-card/70 p-4 ring-1 ring-border/50">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-muted-foreground">
                    ظرفیت تور
                  </span>

                  <span className="font-bold text-foreground">
                    {trip.remaining_capacity} از {trip.capacity} نفر
                  </span>
                </div>

                <div className="h-2.5 w-full overflow-hidden rounded-full bg-primary/10">
                  <div
                    className="h-full rounded-full bg-primary transition-all duration-500"
                    style={{
                      width: `${Math.min(100, Math.max(0, capacityPercentage))}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Price */}
        <section className="mb-8">
          <div className="rounded-3xl bg-card p-6 shadow-sm ring-1 ring-border/50">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-muted-foreground mb-2">قیمت تور</p>

                <p className="text-2xl font-bold text-amber-600">
                  {Number(trip.price).toLocaleString('fa-IR')}
                  <span className="mr-1 text-sm font-normal text-muted-foreground">
                    تومان
                  </span>
                </p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground mb-2">
                  مبلغ بیعانه
                </p>

                <p className="text-2xl font-bold text-amber-600">
                  {Number(trip.deposit_amount).toLocaleString('fa-IR')}
                  <span className="mr-1 text-sm font-normal text-muted-foreground">
                    تومان
                  </span>
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Trip Information */}
        <section className="mb-8">
          <div className="rounded-3xl bg-card p-6 md:p-8 shadow-sm ring-1 ring-border/50">
            <h2 className="text-xl font-bold text-foreground mb-6">
              اطلاعات تور
            </h2>

            <div className="grid gap-5 sm:grid-cols-2">
              <InfoItem
                label="تاریخ شروع"
                value={formatDate(trip.start_date)}
                icon={
                  <svg
                    className="w-5 h-5"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <rect x="3" y="4" width="18" height="18" rx="2" />
                    <line x1="16" y1="2" x2="16" y2="6" />
                    <line x1="8" y1="2" x2="8" y2="6" />
                    <line x1="3" y1="10" x2="21" y2="10" />
                  </svg>
                }
              />

              <InfoItem
                label="تاریخ پایان"
                value={formatDate(trip.end_date)}
                icon={
                  <svg
                    className="w-5 h-5"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <rect x="3" y="4" width="18" height="18" rx="2" />
                    <line x1="16" y1="2" x2="16" y2="6" />
                    <line x1="8" y1="2" x2="8" y2="6" />
                    <line x1="3" y1="10" x2="21" y2="10" />
                  </svg>
                }
              />

              {trip.departure_time && (
                <InfoItem
                  label="ساعت حرکت"
                  value={formatTime(trip.departure_time)}
                  icon={
                    <svg
                      className="w-5 h-5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <circle cx="12" cy="12" r="9" />
                      <polyline points="12 7 12 12 15 14" />
                    </svg>
                  }
                />
              )}

              {trip.meeting_point && (
                <InfoItem
                  label="محل تجمع"
                  value={trip.meeting_point}
                  icon={
                    <svg
                      className="w-5 h-5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z" />
                      <circle cx="12" cy="10" r="2.5" />
                    </svg>
                  }
                />
              )}

              {trip.transportation_type && (
                <InfoItem
                  label="وسیله نقلیه"
                  value={trip.transportation_type}
                  icon={
                    <svg
                      className="w-5 h-5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M5 17h14" />
                      <path d="M6 17a2 2 0 1 0 4 0" />
                      <path d="M14 17a2 2 0 1 0 4 0" />
                      <path d="M4 17V9l2-4h12l2 4v8" />
                      <path d="M4 10h16" />
                    </svg>
                  }
                />
              )}

              {trip.difficulty_level && (
                <InfoItem
                  label="سطح سختی"
                  value={trip.difficulty_level}
                  icon={
                    <svg
                      className="w-5 h-5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="m3 20 6-9 4 5 3-4 5 8" />
                      <path d="M3 20h18" />
                    </svg>
                  }
                />
              )}
            </div>
          </div>
        </section>

        {/* Description */}
        {trip.description && (
          <section className="mb-8">
            <div className="rounded-3xl bg-card p-6 md:p-8 shadow-sm ring-1 ring-border/50">
              <h2 className="text-xl font-bold text-foreground mb-4">
                درباره این سفر
              </h2>

              <p className="text-sm leading-8 text-muted-foreground whitespace-pre-line">
                {trip.description}
              </p>
            </div>
          </section>
        )}

        {/* Registration CTA */}
        <section>
          <div className="rounded-3xl bg-gradient-to-br from-primary/10 to-amber/10 p-6 md:p-8 text-center ring-1 ring-border/50">
            <h2 className="text-xl font-bold text-foreground mb-3">
              آماده سفر هستید؟
            </h2>

            <p className="text-sm text-muted-foreground mb-6">
              {isFull
                ? 'ظرفیت این تور تکمیل شده است.'
                : 'برای ثبت‌نام و ادامه فرایند، جزئیات تور را بررسی کنید.'}
            </p>

            <button
              disabled
              className="btn btn-primary w-full max-w-xs mx-auto disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isFull ? 'ظرفیت تکمیل است' : 'ثبت‌نام در تور'}
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}

function InfoItem({
  label,
  value,
  icon,
}: {
  label: string
  value: string
  icon: React.ReactNode
}) {
  return (
    <div className="flex items-start gap-3 rounded-2xl bg-muted/30 p-4">
      <div className="shrink-0 text-primary">{icon}</div>

      <div className="min-w-0">
        <p className="text-xs text-muted-foreground mb-1">{label}</p>
        <p className="text-sm font-medium text-foreground break-words">
          {value}
        </p>
      </div>
    </div>
  )
}