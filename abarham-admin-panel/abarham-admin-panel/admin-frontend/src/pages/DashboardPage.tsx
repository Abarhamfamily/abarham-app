import { useQuery } from '@tanstack/react-query'
import { fetchDashboardStats } from '../api/dashboard'

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card" style={{ minWidth: 180 }}>
      <p style={{ fontSize: 13, color: '#666', marginBottom: 6 }}>{label}</p>
      <p style={{ fontSize: 24, fontWeight: 700 }}>{value}</p>
    </div>
  )
}

export default function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: fetchDashboardStats,
    refetchInterval: 30_000,
  })

  if (isLoading) return <p>در حال بارگذاری...</p>
  if (isError || !data) return <p>خطا در دریافت آمار داشبورد.</p>

  return (
    <div>
      <h1 style={{ marginBottom: 20 }}>داشبورد</h1>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
        <StatCard label="کل کاربران" value={data.total_users} />
        <StatCard label="کاربران فعال" value={data.active_users} />
        <StatCard label="کل تورها" value={data.total_trips} />
        <StatCard label="تورهای منتشرشده" value={data.published_trips} />
        <StatCard label="کل ثبت‌نام‌ها" value={data.total_registrations} />
        <StatCard label="در انتظار پرداخت" value={data.pending_payment_registrations} />
        <StatCard label="ثبت‌نام‌های تأییدشده" value={data.confirmed_registrations} />
        <StatCard label="پرداخت‌های در انتظار بررسی" value={data.pending_payments_count} />
        <StatCard
          label="مجموع پرداخت‌های تأییدشده"
          value={`${Number(data.confirmed_payments_total).toLocaleString('fa-IR')} تومان`}
        />
        <StatCard
          label="مجموع موجودی کیف‌پول‌ها"
          value={`${Number(data.total_wallet_balance).toLocaleString('fa-IR')} تومان`}
        />
        <StatCard label="اعلان‌های خوانده‌نشده" value={data.unread_notifications} />
      </div>
    </div>
  )
}
