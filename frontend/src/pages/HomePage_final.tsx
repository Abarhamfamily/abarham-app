import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchTrips } from '../api/trips'
import type { TripListResponse } from '../types'

// Static categories data (no API endpoint for categories)
const categories = [
  { icon: '🌲', label: 'جنگل', color: 'bg-green-50 text-green-700' },
  { icon: '🏕️', label: 'کمپ', color: 'bg-amber-50 text-amber-700' },
  { icon: '🏔️', label: 'دره‌نوردی', color: 'bg-blue-50 text-blue-700' },
  { icon: '⛰️', label: 'کوهنوردی', color: 'bg-purple-50 text-purple-700' },
]
    export default function HomePage() {
  const { data: tripsData, isLoading, error } = useQuery<TripListResponse, Error>({
    queryKey: ['trips'],
    queryFn: () => fetchTrips(),
  })

  const trips = tripsData?.data ?? []
  const featuredTrip = trips[0]
  const otherTrips = trips.slice(1, 6)

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4">
        <h2 className="text-2xl font-bold mb-4">خطا در بارگذاری اطلاعات</h2>
        <p className="text-muted-foreground mb-6">لطفاً اتصال اینترنت خود را بررسی کنید</p>
        <Link to="/trips" className="btn btn-primary">مشاهده تورها</Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen pb-20">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-primary/10 to-transparent pb-16">
        <div className="container mx-auto px-4 pt-8 pb-12">
          <h1 className="text-4xl font-bold mb-4 text-foreground">آبرهام سفر</h1>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl">
            سفر به قلب طبیعت. تورهای هیجان‌انگیز و خاطره‌ساز در دسترس شماست
          </p>
          <Link to="/trips" className="btn btn-primary text-lg px-8 py-3">
            جستجوی تورها
          </Link>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-8 bg-card/50">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl font-bold mb-6 text-foreground">دسته‌بندی‌ها</h2>
          <div className="flex gap-3 overflow-x-auto pb-4 no-scrollbar">
            {categories.map((category, index) => (
              <div
                key={index}
                className={`flex-shrink-0 px-5 py-3 rounded-full ${category.color} font-medium cursor-pointer hover:scale-105 transition-transform`}
              >
                <span className="text-xl ml-2">{category.icon}</span>
                <span>{category.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
{/* Featured Hero Trip */}
      {featuredTrip && (
        <section className="py-8">
          <div className="container mx-auto px-4">
            <h2 className="text-2xl font-bold mb-6 text-foreground">تور ویژه</h2>
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
{/* Featured Trips Grid */}
      {otherTrips.length > 0 && (
        <section className="py-8 bg-card/30">
          <div className="container mx-auto px-4">
            <h2 className="text-2xl font-bold mb-6 text-foreground">تورهای برگزیده</h2>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {otherTrips.map((trip) => (
                <Link
                  key={trip.id}
                  to={`/trips/${trip.id}`}
                  className="block bg-card rounded-xl overflow-hidden shadow hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
                >
                  <div className="p-5">
                    <h3 className="font-semibold text-foreground mb-2 line-clamp-1">
                      {trip.title}
                    </h3>
                    <p className="text-sm text-muted-foreground mb-4 flex items-center gap-2">
                      <span>📍</span>
                      <span className="line-clamp-1">{trip.destination}</span>
                    </p>
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-lg font-bold text-amber-600">
                        {trip.price} تومان
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {trip.remaining_capacity}/{trip.capacity} نفر
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      {trip.difficulty_level && (
                        <span className="badge badge-primary text-xs">
                          {trip.difficulty_level}
                        </span>
                      )}
                      <span className="text-xs text-muted-foreground">
                        شروع:{' '}
                        {new Date(trip.start_date).toLocaleDateString('fa-IR', {
                          month: 'short',
                          day: 'numeric'
                        })}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Community Section */}
      <section className="py-12">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="bg-gradient-to-r from-primary/5 to-amber/5 rounded-2xl p-8 md:p-12 text-center">
            <h2 className="text-3xl font-bold mb-4 text-foreground">عضو جامعه ابرهام شوید</h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
              به صدها مسافر کنجکاو برای ماجراجویی بپیوندید. نکات، قصه‌ها و تریلرهای انحصاری دریافت کنید و در سفرهای بعدی به عنوان اولین کسی که خبر دار می‌شوید، ثبت‌نام کنید.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register" className="btn btn-primary px-8">
                ثبت‌نام در حالا
              </Link>
              <Link to="/trips" className="btn btn-outline px-8">
                مشاهده تورها
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
