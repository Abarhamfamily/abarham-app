import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import { useAuthStore } from '../store/authStore'

export default function WalletPage() {
  const user = useAuthStore((s) => s.user)

  const { data: wallet, isLoading } = useQuery({
    queryKey: ['wallet'],
    queryFn: async () => (await apiClient.get('/wallet')).data,
    enabled: Boolean(user),
  })

  if (!user) return <p>برای مشاهده‌ی کیف پول ابتدا وارد شوید.</p>
  if (isLoading) return <p>در حال بارگذاری...</p>

  return (
    <div>
      <h1>کیف پول</h1>
      <p>موجودی: {wallet ? Number(wallet.balance).toLocaleString('fa-IR') : 0} تومان</p>
      {/* TODO (Phase 5): دکمه‌های واریز/برداشت، به‌محض پیاده‌سازی
          WalletService.deposit / withdraw در بک‌اند */}
    </div>
  )
}
