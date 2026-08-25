import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { adminLogin } from '../api/auth'
import { useAdminAuthStore } from '../store/adminAuthStore'

const schema = z.object({
  username: z.string().min(1, 'نام کاربری را وارد کنید'),
  password: z.string().min(1, 'رمز عبور را وارد کنید'),
})

type FormValues = z.infer<typeof schema>

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })
  const [serverError, setServerError] = useState<string | null>(null)
  const setAuth = useAdminAuthStore((s) => s.setAuth)
  const navigate = useNavigate()

  const onSubmit = async (values: FormValues) => {
    setServerError(null)
    try {
      const data = await adminLogin(values.username, values.password)
      setAuth(data.access_token, data.refresh_token, data.admin)
      navigate('/')
    } catch (err: any) {
      setServerError(err?.response?.data?.detail || 'ورود ناموفق بود')
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div className="card" style={{ width: 360 }}>
        <h1 style={{ fontSize: 20, marginBottom: 4 }}>ورود به پنل مدیریت</h1>
        <p style={{ fontSize: 13, color: '#666', marginBottom: 20 }}>
          این پنل مستقل از اپلیکیشن کاربران است.
        </p>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="form-row">
            <label>نام کاربری</label>
            <input {...register('username')} autoFocus />
            {errors.username && <p className="error-text">{errors.username.message}</p>}
          </div>
          <div className="form-row">
            <label>رمز عبور</label>
            <input type="password" {...register('password')} />
            {errors.password && <p className="error-text">{errors.password.message}</p>}
          </div>
          {serverError && <p className="error-text">{serverError}</p>}
          <button type="submit" style={{ width: '100%', marginTop: 8 }}>
            ورود
          </button>
        </form>
      </div>
    </div>
  )
}
