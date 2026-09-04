import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import { useAuthStore } from '../store/authStore'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'

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
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Typography as="h1" variant="h1" className="mb-6 text-foreground">کیف پول</Typography>
        
        <Card className="bg-card border-border shadow-lg">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl font-bold text-foreground">موجودی حساب</CardTitle>
            <CardDescription className="text-muted-foreground">
              موجودی فعلی کیف پول شما
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <div className="flex items-center justify-between p-6 bg-muted/50 rounded-lg">
              <Typography as="span" className="text-lg text-muted-foreground">موجودی:</Typography>
              <Typography as="span" className="text-3xl font-bold text-primary">
                {wallet ? Number(wallet.balance).toLocaleString('fa-IR') : 0} تومان
              </Typography>
            </div>
            
            {/* TODO (Phase 5): دکمه‌های واریز/برداشت، به‌محض پیاده‌سازی
                WalletService.deposit / withdraw در بک‌اند */}
            <div className="mt-6 flex flex-col sm:flex-row gap-4">
              <Button variant="default" className="flex-1">
                واریز وجه
              </Button>
              <Button variant="outline" className="flex-1">
                برداشت وجه
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
