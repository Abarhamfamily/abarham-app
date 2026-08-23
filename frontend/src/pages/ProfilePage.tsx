import { useAuthStore } from '../store/authStore'

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user)

  if (!user) {
    return <p>برای مشاهده‌ی پروفایل ابتدا وارد شوید.</p>
  }

  return (
    <div>
      <h1>پروفایل</h1>
      <p>نام: {user.full_name}</p>
      <p>شماره تماس: {user.phone_number}</p>
      {/* TODO (Phase 2/7): فرم ویرایش پروفایل + آپلود عکس، متصل به
          UserProfile در بک‌اند */}
    </div>
  )
}
