import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchRegistrations, updateRegistrationStatus } from '../api/registrations'
import Pagination from '../components/Pagination'

const LIMIT = 20

const STATUS_LABELS: Record<string, string> = {
  pending_payment: 'در انتظار پرداخت',
  confirmed: 'تأییدشده',
  cancelled: 'لغوشده',
  completed: 'برگزارشده',
  expired: 'منقضی‌شده',
}

export default function RegistrationsPage() {
  const [statusFilter, setStatusFilter] = useState('')
  const [offset, setOffset] = useState(0)
  const queryClient = useQueryClient()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-registrations', statusFilter, offset],
    queryFn: () => fetchRegistrations({ status: statusFilter || undefined, limit: LIMIT, offset }),
  })

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await updateRegistrationStatus(id, status)
      queryClient.invalidateQueries({ queryKey: ['admin-registrations'] })
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'به‌روزرسانی با خطا مواجه شد')
    }
  }

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>ثبت‌نام‌ها</h1>

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
      {isError && <p>خطا در دریافت لیست ثبت‌نام‌ها.</p>}

      {data && (
        <>
          <table>
            <thead>
              <tr>
                <th>کاربر</th>
                <th>تور</th>
                <th>مبلغ کل</th>
                <th>پرداخت‌شده</th>
                <th>باقی‌مانده</th>
                <th>وضعیت</th>
                <th>تغییر وضعیت</th>
              </tr>
            </thead>
            <tbody>
              {data.data.map((r) => (
                <tr key={r.id}>
                  <td>
                    {r.user_full_name}
                    <br />
                    <span style={{ fontSize: 12, color: '#888' }}>{r.user_phone_number}</span>
                  </td>
                  <td>{r.trip_title}</td>
                  <td>{Number(r.total_price).toLocaleString('fa-IR')}</td>
                  <td>{Number(r.deposit_paid).toLocaleString('fa-IR')}</td>
                  <td>{Number(r.remaining_amount).toLocaleString('fa-IR')}</td>
                  <td>
                    <span className="badge">{STATUS_LABELS[r.status] || r.status}</span>
                  </td>
                  <td>
                    <select
                      defaultValue=""
                      onChange={(e) => {
                        if (e.target.value) handleStatusChange(r.id, e.target.value)
                        e.target.value = ''
                      }}
                    >
                      <option value="" disabled>
                        تغییر به...
                      </option>
                      {Object.entries(STATUS_LABELS)
                        .filter(([value]) => value !== r.status)
                        .map(([value, label]) => (
                          <option key={value} value={value}>
                            {label}
                          </option>
                        ))}
                    </select>
                  </td>
                </tr>
              ))}
              {data.data.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', color: '#888' }}>
                    ثبت‌نامی یافت نشد
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
