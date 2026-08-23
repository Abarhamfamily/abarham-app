import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { register as registerUser } from '../api/auth'

const schema = z.object({
  phone_number: z.string().min(10, 'شماره تماس معتبر وارد کنید'),
  full_name: z.string().min(3, 'نام و نام خانوادگی معتبر وارد کنید'),
  password: z.string().min(8, 'رمز عبور باید حداقل ۸ کاراکتر باشد'),
})

type FormValues = z.infer<typeof schema>

export default function RegisterPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })
  const [message, setMessage] = useState<string | null>(null)
  const [serverError, setServerError] = useState<string | null>(null)

  const onSubmit = async (values: FormValues) => {
    setServerError(null)
    setMessage(null)
    try {
      const data = await registerUser(values.phone_number, values.full_name, values.password)
      // نکته: تایید OTP هنوز در بک‌اند پیاده‌سازی نشده (Phase 2)، بنابراین
      // فعلاً فقط پیام سرور نمایش داده می‌شود.
      setMessage(data.message)
    } catch (err: any) {
      setServerError(err?.response?.data?.detail || 'ثبت‌نام ناموفق بود')
    }
  }

  return (
    <div style={{ maxWidth: 360 }}>
      <h1>ثبت‌نام</h1>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div>
          <label>نام و نام خانوادگی</label>
          <input {...register('full_name')} />
          {errors.full_name && <p style={{ color: 'red' }}>{errors.full_name.message}</p>}
        </div>
        <div>
          <label>شماره تماس</label>
          <input {...register('phone_number')} placeholder="09xxxxxxxxx" />
          {errors.phone_number && <p style={{ color: 'red' }}>{errors.phone_number.message}</p>}
        </div>
        <div>
          <label>رمز عبور</label>
          <input type="password" {...register('password')} />
          {errors.password && <p style={{ color: 'red' }}>{errors.password.message}</p>}
        </div>
        {serverError && <p style={{ color: 'red' }}>{serverError}</p>}
        {message && <p style={{ color: 'green' }}>{message}</p>}
        <button type="submit">ثبت‌نام</button>
      </form>
      <p>
        حساب کاربری دارید؟ <Link to="/login">وارد شوید</Link>
      </p>
    </div>
  )
}
