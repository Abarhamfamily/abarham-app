import { useAuthStore } from '../store/authStore'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user)

  if (!user) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12 bg-gradient-to-b from-primary/5 to-transparent">
        <Typography as="h2" variant="h2" className="mb-3 text-foreground">
          برای مشاهده‌ی پروفایل ابتدا وارد شوید.
        </Typography>
        <Link to="/login">
          <Button variant="default" className="w-full max-w-xs">
            ورود
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen pb-20 bg-gradient-to-b from-primary/5 to-transparent">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="bg-card border-border shadow-sm">
          <CardHeader className="pb-4">
            <CardTitle>
              <Typography as="h2" variant="h2" className="text-foreground">
                پروفایل
              </Typography>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Avatar and Name */}
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-muted/50 flex items-center justify-center">
                <Typography as="span" variant="h3" className="text-muted-foreground">
                  {user.full_name.charAt(0)}
                </Typography>
              </div>
              <div className="space-y-2">
                <Typography as="p" variant="small" className="text-muted-foreground mb-1">
                  نام:
                </Typography>
                <Typography as="p" variant="small" className="font-medium text-foreground">
                  {user.full_name}
                </Typography>
              </div>
            </div>

            {/* Phone Number */}
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-muted/50 flex items-center justify-center">
                <Typography as="span" variant="h3" className="text-muted-foreground">📞</Typography>
              </div>
              <div className="space-y-2">
                <Typography as="p" variant="small" className="text-muted-foreground mb-1">
                  شماره تماس:
                </Typography>
                <Typography as="p" variant="small" className="font-medium text-foreground">
                  {user.phone_number}
                </Typography>
              </div>
            </div>

            {/* Placeholder for future fields */}
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-muted/50 flex items-center justify-center">
                <Typography as="span" variant="h3" className="text-muted-foreground">📧</Typography>
              </div>
              <div className="space-y-2">
                <Typography as="p" variant="small" className="text-muted-foreground mb-1">
                  ایمیل:
                </Typography>
                <Typography as="p" variant="small" className="font-medium text-foreground">
                  {user.email || 'ثبت نشده'}
                </Typography>
              </div>
            </div>

            {/* Edit Profile Button */}
            <div className="flex justify-center">
              <Button variant="outline" onClick={() => alert('ویرایش پروفایل در حال پیاده‌سازی است...')}>
                ویرایش پروفایل
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
