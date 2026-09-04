import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import { fetchTrips } from '../api/trips'
import { Card, CardContent } from '../components/ui/Card'

export default function TripsPage() {
  const [searchTerm, setSearchTerm] = useState('')

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['trips'],
    queryFn: () => fetchTrips({ status: 'published', limit: 20, offset: 0 }),
  })

  const trips = data?.data ?? []

  const filteredTrips = trips.filter((trip) => {
    const searchLower = searchTerm.toLowerCase()
    return (
      trip.title.toLowerCase().includes(searchLower) ||
      trip.destination.toLowerCase().includes(searchLower) ||
      (trip.description && trip.description.toLowerCase().includes(searchLower))
    )
  })

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
        <div className="w-20 h-20 mb-4 flex items-center justify-center bg-destructive/10 rounded-full">
          <svg className="w-10 h-10 text-destructive" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <h2 className="text-2xl font-bold mb-4 text-foreground">خطا در بارگذاری تورها</h2>
        <p className="text-muted-foreground mb-6">لطفاً اتصال اینترنت خود را بررسی کنید</p>
        <button onClick={() => refetch()} className="btn btn-primary w-full max-w-xs">
          تلاش مجدد
        </button>
      </div>
    )
  }

  if (filteredTrips.length === 0) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
        <div className="w-24 h-24 mb-6 flex items-center justify-center bg-muted/50 rounded-full">
          <svg className="w-12 h-12 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
        </div>
        <h2 className="text-2xl font-bold mb-4 text-foreground">
          {searchTerm ? 'نتیجهٔ جستجو یافت نشد' : 'هیچ تور فعالی یافت نشد'}
        </h2>
        {searchTerm ? (
          <p className="text-muted-foreground mb-6 text-center">
            عبارت «{searchTerm}» یافت نشد. لطفاً عبارت جستجو را تغییر دهید.
          </p>
        ) : (
          <p className="text-muted-foreground mb-6 text-center">
            در حال حاضر هیچ تور فعالی برای نمایش وجود ندارد.
          </p>
        )}
        <Link to="/" className="btn btn-primary w-full max-w-xs">
          بازگشت به خانه
        </Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen pb-20">
      {/* Header */}
      <section className="bg-gradient-to-b from-primary/5 to-transparent pb-8">
        <div className="container mx-auto px-4 pt-8 pb-6">
          <h1 className="text-3xl font-bold mb-2 text-foreground">تورهای ابرهام</h1>
          <p className="text-muted-foreground mb-6 text-center">
            انتخاب بهترین تورهای سفر برای مقاصد داخلی و خارجی
          </p>
        </div>
      </section>

      {/* Search */}
      <section className="px-4 mb-6">
        <div className="relative max-w-md mx-auto">
          <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
            <span className="text-muted-foreground">🔍</span>
          </div>
          <input
            type="search"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="جستجوی تور یا مقصد..."
            className="w-full px-4 py-3 pr-12 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary text-left bg-card/90 backdrop-blur"
          />
        </div>
      </section>

      {/* Trip Cards */}
      <section className="px-4">
        <div className="container mx-auto">
          <div className="grid gap-5">
            {filteredTrips.map((trip) => (
              <Link
                key={trip.id}
                to={`/trips/${trip.id}`}
                className="block"
              >
                <Card className="group overflow-hidden shadow hover:shadow-lg transition-all duration-200 hover:-translate-y-1">
                <div className="flex flex-col md:flex-row">
                  {/* Image Area (placeholder since no image field) */}
                  <div className="relative h-48 md:h-56 w-full md:w-48 overflow-hidden">
                    {/* Since we don't have image_url, we show a gradient placeholder */}
                    <div className="w-full h-full bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center">
                      <div className="text-5xl text-muted-foreground/50">🏔️</div>
                    </div>
                    {/* Price Badge */}
                    <div className="absolute top-4 start-4 z-10 flex items-center gap-1 rounded-xl bg-amber/90 px-2 py-1 text-xs font-semibold">
                      <span className="text-amber-foreground">{Number(trip.price).toLocaleString('fa-IR')}</span>
                      <span className="text-amber-foreground text-[10px]">تومان</span>
                    </div>
                    {/* Status Badge */}
                    <div className="absolute top-4 end-4 z-10">
                      {trip.remaining_capacity > 0 ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-1 text-xs font-semibold text-primary">
                          ✅ موجود
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 rounded-full bg-destructive/10 px-2 py-1 text-xs font-semibold text-destructive">
                          ❌ تمام
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                  {/* Content */}
                  <CardContent className="p-5">
                    <h2 className="font-bold text-lg text-foreground line-clamp-1 mb-3">
                      {trip.title}
                    </h2>

                    <div className="flex items-center gap-4 mb-4 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                          <circle cx="12" cy="10" r="3"></circle>
                        </svg>
                        {trip.destination}
                      </span>
                    </div>

                    {trip.description && (
                      <p className="text-sm text-muted-foreground line-clamp-3 mb-6">
                        {trip.description}
                      </p>
                    )}

                    <div className="grid grid-cols-2 gap-4 mb-5 text-sm">
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">ظرفیت</div>
                        <div className="font-medium text-foreground">
                          {trip.remaining_capacity}/{trip.capacity} نفر
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">وضعیت</div>
                        <div className={`font-medium ${trip.remaining_capacity > 0 ? 'text-primary' : 'text-muted-foreground'}`}>
                          {trip.remaining_capacity > 0 ? 'موجود' : 'ناموجود'}
                        </div>
                      </div>
                    </div>

                    <div className="pt-4 border-t border-border">
                      <span className="text-primary font-medium">
                        مشاهده جزئیات →
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
