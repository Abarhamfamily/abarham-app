import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchTrips } from '../api/trips'

export default function TripsPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['trips'],
    queryFn: () => fetchTrips({ status: 'published', limit: 20, offset: 0 }),
  })

  if (isLoading) return <p>در حال بارگذاری تورها...</p>
  if (isError) return <p>خطا در دریافت لیست تورها.</p>

  const trips = data?.data ?? []

  if (trips.length === 0) {
    return <p>در حال حاضر توری برای نمایش وجود ندارد.</p>
  }

  return (
    <div>
      <h1>تورهای فعال</h1>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {trips.map((trip) => (
          <li key={trip.id} style={{ border: '1px solid #eee', borderRadius: 8, padding: 16, marginBottom: 12 }}>
            <Link to={`/trips/${trip.id}`}>
              <h3 style={{ margin: 0 }}>{trip.title}</h3>
            </Link>
            <p style={{ margin: '4px 0' }}>{trip.destination}</p>
            <p style={{ margin: '4px 0' }}>
              ظرفیت باقی‌مانده: {trip.remaining_capacity} از {trip.capacity}
            </p>
            <p style={{ margin: '4px 0' }}>قیمت: {Number(trip.price).toLocaleString('fa-IR')} تومان</p>
          </li>
        ))}
      </ul>
    </div>
  )
}
