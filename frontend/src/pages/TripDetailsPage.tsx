import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchTrip } from '../api/trips'

export default function TripDetailsPage() {
  const { id } = useParams<{ id: string }>()

  const { data: trip, isLoading, isError } = useQuery({
    queryKey: ['trip', id],
    queryFn: () => fetchTrip(id as string),
    enabled: Boolean(id),
  })

  if (isLoading) return <p>در حال بارگذاری...</p>
  if (isError || !trip) return <p>تور یافت نشد.</p>

  return (
    <div>
      <h1>{trip.title}</h1>
      <p>{trip.destination}</p>
      {trip.description && <p>{trip.description}</p>}
      <p>قیمت: {Number(trip.price).toLocaleString('fa-IR')} تومان</p>
      <p>بیعانه: {Number(trip.deposit_amount).toLocaleString('fa-IR')} تومان</p>
      <p>
        ظرفیت باقی‌مانده: {trip.remaining_capacity} از {trip.capacity}
      </p>
      {/* TODO (Phase 4): دکمه‌ی ثبت‌نام که به /registrations POST می‌زند،
          به‌محض پیاده‌سازی RegistrationService در بک‌اند */}
    </div>
  )
}
