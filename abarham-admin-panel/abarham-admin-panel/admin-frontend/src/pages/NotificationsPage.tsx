import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchNotifications, createNotification } from '../api/notifications'
import Pagination from '../components/Pagination'

const LIMIT = 20

export default function NotificationsPage() {
  const [offset, setOffset] = useState(0)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [userId, setUserId] = useState('')
  const [allActiveUsers, setAllActiveUsers] = useState(false)
  const [sending, setSending] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-notifications', offset],
    queryFn: () => fetchNotifications({ limit: LIMIT, offset }),
  })

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    setSending(true)
    setFeedback(null)
    try {
      const result = await createNotification({
        title,
        content,
        user_id: allActiveUsers ? undefined : userId || undefined,
        all_active_users: allActiveUsers,
      })
      setFeedback(`✅ برای ${result.created_count} کاربر ارسال شد.`)
      setTitle('')
      setContent('')
      setUserId('')
      queryClient.invalidateQueries({ queryKey: ['admin-notifications'] })
    } catch (err: any) {
      setFeedback(err?.response?.data?.detail || 'ارسال با خطا مواجه شد')
    } finally {
      setSending(false)
    }
  }

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>اعلان‌ها</h1>

      <form onSubmit={handleSend} className="card" style={{ maxWidth: 480, marginBottom: 24 }}>
        <h3 style={{ marginBottom: 12 }}>ارسال اعلان جدید</h3>
        <div className="form-row">
          <label>عنوان</label>
          <input required value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="form-row">
          <label>متن</label>
          <textarea required rows={3} value={content} onChange={(e) => setContent(e.target.value)} />
        </div>
        <div className="form-row">
          <label>
            <input
              type="checkbox"
              checked={allActiveUsers}
              onChange={(e) => setAllActiveUsers(e.target.checked)}
              style={{ width: 'auto', marginLeft: 6 }}
            />
            ارسال برای همه‌ی کاربران فعال
          </label>
        </div>
        {!allActiveUsers && (
          <div className="form-row">
            <label>شناسه‌ی کاربر (UUID)</label>
            <input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="از صفحه‌ی کاربر کپی کنید" />
          </div>
        )}
        {feedback && <p style={{ fontSize: 13, marginBottom: 8 }}>{feedback}</p>}
        <button type="submit" disabled={sending}>
          {sending ? 'در حال ارسال...' : 'ارسال'}
        </button>
      </form>

      <h3 style={{ marginBottom: 8 }}>اعلان‌های ارسال‌شده</h3>
      {isLoading && <p>در حال بارگذاری...</p>}
      {data && (
        <>
          <table>
            <thead>
              <tr>
                <th>عنوان</th>
                <th>کاربر</th>
                <th>وضعیت خواندن</th>
                <th>تاریخ ارسال</th>
              </tr>
            </thead>
            <tbody>
              {data.data.map((n) => (
                <tr key={n.id}>
                  <td>{n.title}</td>
                  <td>{n.user_full_name}</td>
                  <td>{n.read_at ? 'خوانده‌شده' : 'خوانده‌نشده'}</td>
                  <td>{new Date(n.sent_at).toLocaleDateString('fa-IR')}</td>
                </tr>
              ))}
              {data.data.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', color: '#888' }}>
                    اعلانی یافت نشد
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          <Pagination total={data.meta.total} limit={LIMIT} offset={offset} onOffsetChange={setOffset} />
        </>
      )}
    </div>
  )
}
