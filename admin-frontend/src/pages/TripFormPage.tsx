import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createTrip, fetchTrip, updateTrip, type TripFormValues } from '../api/trips'

const emptyForm: TripFormValues = {
  title: '',
  destination: '',
  description: '',
  start_date: '',
  end_date: '',
  price: '',
  deposit_amount: '',
  capacity: 10,
  status: 'draft',
  transportation_type: '',
  difficulty_level: '',
  accommodation_info: '',
  meeting_point: '',
  departure_time: '',
  cancellation_policy: '',
}

// datetime-local نیاز به فرمت YYYY-MM-DDTHH:mm دارد (بدون timezone)
function toDatetimeLocal(iso: string) {
  if (!iso) return ''
  return iso.slice(0, 16)
}

export default function TripFormPage() {
  const { id } = useParams<{ id: string }>()
  const isEdit = Boolean(id) && id !== 'new'
  const navigate = useNavigate()

  const [form, setForm] = useState<TripFormValues>(emptyForm)
  const [loading, setLoading] = useState(isEdit)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isEdit) return
    fetchTrip(id as string).then((trip) => {
      setForm({
        title: trip.title,
        destination: trip.destination,
        description: trip.description || '',
        start_date: toDatetimeLocal(trip.start_date),
        end_date: toDatetimeLocal(trip.end_date),
        price: trip.price,
        deposit_amount: trip.deposit_amount,
        capacity: trip.capacity,
        status: trip.status,
        transportation_type: trip.transportation_type || '',
        difficulty_level: trip.difficulty_level || '',
        accommodation_info: trip.accommodation_info || '',
        meeting_point: trip.meeting_point || '',
        departure_time: trip.departure_time || '',
        cancellation_policy: trip.cancellation_policy || '',
      })
      setLoading(false)
    })
  }, [id, isEdit])

  const update = (key: keyof TripFormValues, value: string | number) =>
    setForm((f) => ({ ...f, [key]: value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSaving(true)
    try {
      const payload = {
        ...form,
        start_date: new Date(form.start_date).toISOString(),
        end_date: new Date(form.end_date).toISOString(),
      }
      if (isEdit) {
        await updateTrip(id as string, payload)
      } else {
        await createTrip(payload)
      }
      navigate('/trips')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'ذخیره‌سازی با خطا مواجه شد')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <p>در حال بارگذاری...</p>

  return (
    <div style={{ maxWidth: 640 }}>
      <h1 style={{ marginBottom: 16 }}>{isEdit ? 'ویرایش تور' : 'تور جدید'}</h1>

      <form onSubmit={handleSubmit} className="card">
        <div className="form-row">
          <label>عنوان</label>
          <input required value={form.title} onChange={(e) => update('title', e.target.value)} />
        </div>

        <div className="form-row">
          <label>مقصد</label>
          <input required value={form.destination} onChange={(e) => update('destination', e.target.value)} />
        </div>

        <div className="form-row">
          <label>توضیحات</label>
          <textarea rows={3} value={form.description} onChange={(e) => update('description', e.target.value)} />
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          <div className="form-row" style={{ flex: 1 }}>
            <label>تاریخ شروع</label>
            <input
              required
              type="datetime-local"
              value={form.start_date}
              onChange={(e) => update('start_date', e.target.value)}
            />
          </div>
          <div className="form-row" style={{ flex: 1 }}>
            <label>تاریخ پایان</label>
            <input
              required
              type="datetime-local"
              value={form.end_date}
              onChange={(e) => update('end_date', e.target.value)}
            />
          </div>
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          <div className="form-row" style={{ flex: 1 }}>
            <label>قیمت (تومان)</label>
            <input required type="number" value={form.price} onChange={(e) => update('price', e.target.value)} />
          </div>
          <div className="form-row" style={{ flex: 1 }}>
            <label>مبلغ بیعانه (تومان)</label>
            <input
              required
              type="number"
              value={form.deposit_amount}
              onChange={(e) => update('deposit_amount', e.target.value)}
            />
          </div>
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          <div className="form-row" style={{ flex: 1 }}>
            <label>ظرفیت</label>
            <input
              required
              type="number"
              min={1}
              value={form.capacity}
              onChange={(e) => update('capacity', Number(e.target.value))}
            />
          </div>
          <div className="form-row" style={{ flex: 1 }}>
            <label>وضعیت</label>
            <select value={form.status} onChange={(e) => update('status', e.target.value)}>
              <option value="draft">پیش‌نویس</option>
              <option value="published">منتشرشده</option>
              <option value="ongoing">در حال برگزاری</option>
              <option value="completed">برگزارشده</option>
              <option value="cancelled">لغوشده</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <label>نوع وسیله نقلیه</label>
          <input
            value={form.transportation_type}
            onChange={(e) => update('transportation_type', e.target.value)}
            placeholder="مثلاً: personal_vehicle یا bus"
          />
        </div>

        <div className="form-row">
          <label>نقطه‌ی تجمع</label>
          <input value={form.meeting_point} onChange={(e) => update('meeting_point', e.target.value)} />
        </div>

        <div className="form-row">
          <label>زمان حرکت</label>
          <input value={form.departure_time} onChange={(e) => update('departure_time', e.target.value)} />
        </div>

        <div className="form-row">
          <label>قوانین لغو</label>
          <textarea
            rows={2}
            value={form.cancellation_policy}
            onChange={(e) => update('cancellation_policy', e.target.value)}
          />
        </div>

        {error && <p className="error-text">{error}</p>}

        <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
          <button type="submit" disabled={saving}>
            {saving ? 'در حال ذخیره...' : 'ذخیره'}
          </button>
          <button type="button" className="secondary" onClick={() => navigate('/trips')}>
            انصراف
          </button>
        </div>
      </form>
    </div>
  )
}
