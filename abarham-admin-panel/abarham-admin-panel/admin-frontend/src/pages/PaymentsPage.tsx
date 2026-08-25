import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchPayments, confirmPayment, rejectPayment } from '../api/payments'
import Pagination from '../components/Pagination'

const LIMIT = 20

const STATUS_LABELS: Record<string, string> = {
  pending: 'در انتظار بررسی',
  confirmed: 'تأییدشده',
  failed: 'ردشده',
  refunded: 'بازگشت‌داده‌شده',
  cancelled: 'لغوشده',
}

export default function PaymentsPage() {
  const [statusFilter, setStatusFilter] = useState('pending')
  const [offset, setOffset] = useState(0)
  const queryClient = useQueryClient()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-payments', statusFilter, offset],
    queryFn: () => fetchPayments({ status: statusFilter || undefined, limit: LIMIT, offset }),
  })

  const handleConfirm = async (id: string) => {
    const referenceCode = prompt('کد پیگیری (اختیاری):') || undefined
    try {
      await confirmPayment(id, referenceCode)
      queryClient.invalidateQueries({ queryKey: ['admin-payments'] })
      queryClient.invalidateQueries({ queryKey: ['admin-dashboard'] })
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'تأیید با خطا مواجه شد')
    }
  }

  const handleReject = async (id: string) => {
    const reason = prompt('دلیل رد کردن (اختیاری):') || undefined
    try {
      await rejectPayment(id, reason)
      queryClient.invalidateQueries({ queryKey: ['admin-payments'] })
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'رد کردن با خطا مواجه شد')
    }
  }

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>پرداخت‌ها</h1>

      <div className="form-row" style={{ maxWidth: 220 }}>
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value)
            setOffset(0)
          }}
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
      {isError && <p>خطا در دریافت لیست پرداخت‌ها.</p>}

      {data && (
        <>
          <table>
            <thead>
              <tr>
                <th>کاربر</th>
                <th>تور</th>
                <th>مبلغ</th>
                <th>نوع</th>
                <th>وضعیت</th>
                <th>تاریخ</th>
                <th>اقدام</th>
              </tr>
            </thead>
            <tbody>
              {data.data.map((p) => (
                <tr key={p.id}>
                  <td>
                    {p.user_full_name}
                    <br />
                    <span style={{ fontSize: 12, color: '#888' }}>{p.user_phone_number}</span>
                  </td>
                  <td>{p.trip_title}</td>
                  <td>{Number(p.amount).toLocaleString('fa-IR')}</td>
                  <td>{p.type === 'deposit' ? 'بیعانه' : p.type === 'full' ? 'کامل' : 'باقی‌مانده'}</td>
                  <td>
                    <span className="badge">{STATUS_LABELS[p.status] || p.status}</span>
                  </td>
                  <td>{new Date(p.created_at).toLocaleDateString('fa-IR')}</td>
                  <td>
                    {p.status === 'pending' && (
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button onClick={() => handleConfirm(p.id)}>تأیید</button>
                        <button className="danger" onClick={() => handleReject(p.id)}>
                          رد
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
              {data.data.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', color: '#888' }}>
                    پرداختی یافت نشد
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
