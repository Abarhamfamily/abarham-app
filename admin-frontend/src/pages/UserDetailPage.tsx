import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchUser } from '../api/users'
import { fetchRegistrations } from '../api/registrations'

export default function UserDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: user, isLoading } = useQuery({
    queryKey: ['admin-user', id],
    queryFn: () => fetchUser(id as string),
    enabled: Boolean(id),
  })

  const { data: registrations } = useQuery({
    queryKey: ['admin-user-registrations', id],
    queryFn: () => fetchRegistrations({ user_id: id, limit: 50, offset: 0 }),
    enabled: Boolean(id),
  })

  if (isLoading) return <p>در حال بارگذاری...</p>
  if (!user) return <p>کاربر یافت نشد.</p>

  return (
    <div>
      <Link to="/users">&larr; بازگشت به لیست کاربران</Link>
      <h1 style={{ margin: '12px 0' }}>{user.full_name}</h1>

      <div className="card" style={{ marginBottom: 16 }}>
        <p>شماره تماس: {user.phone_number}</p>
        <p>ایمیل: {user.email || '—'}</p>
        <p>کد ملی: {user.national_id || '—'}</p>
        <p>وضعیت: {user.is_active ? 'فعال' : 'غیرفعال'}</p>
        <p>تاریخ عضویت: {new Date(user.created_at).toLocaleDateString('fa-IR')}</p>
      </div>

      {user.profile && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginBottom: 8 }}>پروفایل تکمیلی</h3>
          <p>تاریخ تولد: {user.profile.birth_date || '—'}</p>
          <p>مخاطب اضطراری: {user.profile.emergency_contact_name || '—'} ({user.profile.emergency_contact_phone || '—'})</p>
          <p>یادداشت پزشکی: {user.profile.medical_notes || '—'}</p>
          <p>ظرفیت خودرو: {user.profile.vehicle_has_capacity ? `بله (${user.profile.empty_seats} صندلی)` : 'خیر'}</p>
        </div>
      )}

      <div className="card">
        <h3 style={{ marginBottom: 8 }}>ثبت‌نام‌های این کاربر</h3>
        <table>
          <thead>
            <tr>
              <th>تور</th>
              <th>وضعیت</th>
              <th>مبلغ کل</th>
              <th>پرداخت‌شده</th>
            </tr>
          </thead>
          <tbody>
            {registrations?.data.map((r) => (
              <tr key={r.id}>
                <td>{r.trip_title}</td>
                <td>{r.status}</td>
                <td>{Number(r.total_price).toLocaleString('fa-IR')}</td>
                <td>{Number(r.deposit_paid).toLocaleString('fa-IR')}</td>
              </tr>
            ))}
            {(!registrations || registrations.data.length === 0) && (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center', color: '#888' }}>
                  ثبت‌نامی یافت نشد
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
