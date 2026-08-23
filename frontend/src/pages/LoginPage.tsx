import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate, Link } from 'react-router-dom'
import { useState } from 'react'
import { login } from '../api/auth'
import { useAuthStore } from '../store/authStore'

const schema = z.object({
  phone_number: z.string().min(10, 'شماره تماس معتبر وارد کنید'),
  password: z.string().min(8, 'رمز عبور باید حداقل ۸ کاراکتر باشد'),
})

type FormValues = z.infer<typeof schema>

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })
  const [serverError, setServerError] = useState<string | null>(null)
  const setAuth = useAuthStore((s) => s.setAuth)
  const navigate = useNavigate()

  const onSubmit = async (values: FormValues) => {
    setServerError(null)
    try {
      const data = await login(values.phone_number, values.password)
      setAuth(data.access_token, data.refresh_token, data.user)
      navigate('/trips')
    } catch (err: any) {
      setServerError(err?.response?.data?.detail || 'ورود ناموفق بود')
    }
  }

  return (
    <div style={{ maxWidth: 360 }}>
      <h1>ورود</h1>
      <form onSubmit={handleSubmit(onSubmit)}>
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
        <button type="submit">ورود</button>
      </form>
      <p>
        حساب کاربری ندارید؟ <Link to="/register">ثبت‌نام کنید</Link>
      </p>
    </div>
  )
}
