import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchWithdrawals, approveWithdrawal, rejectWithdrawal } from '../api/wallet'

const STATUS_LABELS: Record<string, string> = {
  pending: 'در انتظار بررسی',
  confirmed: 'تأییدشده',
  reversed: 'ردشده',
}

export default function WithdrawalsPage() {
  const [statusFilter, setStatusFilter] = useState('pending')
  const queryClient = useQueryClient()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-withdrawals', statusFilter],
    queryFn: () => fetchWithdrawals({ status: statusFilter || undefined, limit: 50, offset: 0 }),
  })

  const handleApprove = async (id: string) => {
    if (!confirm('آیا از تأیید این درخواست برداشت مطمئن هستید؟')) return
    try {
      await approveWithdrawal(id)
      queryClient.invalidateQueries({ queryKey: ['admin-withdrawals'] })
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'تأیید با خطا مواجه شد')
    }
  }

  const handleReject = async (id: string) => {
    const reason = prompt('دلیل رد کردن (اختیاری):') || undefined
    try {
      await rejectWithdrawal(id, reason)
      queryClient.invalidateQueries({ queryKey: ['admin-withdrawals'] })
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'رد کردن با خطا مواجه شد')
    }
  }

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>درخواست‌های برداشت</h1>

      <div className="form-row" style={{ maxWidth: 220 }}>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">همه وضعیت‌ها</option>
          {Object.entries(STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {isLoading && <p>در حال بارگذاری...</p>}
      {isError && <p>خطا در دریافت لیست درخواست‌های برداشت.</p>}

      {data && (
        <table>
          <thead>
            <tr>
              <th>کاربر</th>
              <th>مبلغ</th>
              <th>شماره کارت</th>
              <th>وضعیت</th>
              <th>تاریخ</th>
              <th>اقدام</th>
            </tr>
          </thead>
          <tbody>
            {data.map((w) => (
              <tr key={w.id}>
                <td>
                  {w.user_full_name}
                  <br />
                  <span style={{ fontSize: 12, color: '#888' }}>{w.user_phone_number}</span>
                </td>
                <td>{Number(w.amount).toLocaleString('fa-IR')} تومان</td>
                <td>{w.card_number || '—'}</td>
                <td>
                  <span className="badge">{STATUS_LABELS[w.status] || w.status}</span>
                </td>
                <td>{new Date(w.created_at).toLocaleDateString('fa-IR')}</td>
                <td>
                  {w.status === 'pending' && (
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button onClick={() => handleApprove(w.id)}>تأیید</button>
                      <button className="danger" onClick={() => handleReject(w.id)}>
                        رد
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
            {data.length === 0 && (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', color: '#888' }}>
                  درخواستی یافت نشد
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  )
}