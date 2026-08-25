import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchTrips, deleteTrip } from '../api/trips'
import Pagination from '../components/Pagination'

const LIMIT = 20

export default function TripsPage() {
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')
  const [offset, setOffset] = useState(0)
  const queryClient = useQueryClient()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-trips', statusFilter, search, offset],
    queryFn: () =>
      fetchTrips({ status: statusFilter || undefined, search: search || undefined, limit: LIMIT, offset }),
  })

  const handleDelete = async (id: string) => {
    if (!confirm('آیا از حذف این تور مطمئن هستید؟')) return
    try {
      await deleteTrip(id)
      queryClient.invalidateQueries({ queryKey: ['admin-trips'] })
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'حذف با خطا مواجه شد')
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1>تورها</h1>
        <Link to="/trips/new">
          <button>+ تور جدید</button>
        </Link>
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
        <input
          placeholder="جست‌وجو در عنوان یا مقصد"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value)
            setOffset(0)
          }}
          style={{ maxWidth: 280 }}
        />
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value)
            setOffset(0)
          }}
          style={{ maxWidth: 180 }}
        >
          <option value="">همه وضعیت‌ها</option>
          <option value="draft">پیش‌نویس</option>
          <option value="published">منتشرشده</option>
          <option value="ongoing">در حال برگزاری</option>
          <option value="completed">برگزارشده</option>
          <option value="cancelled">لغوشده</option>
        </select>
      </div>

      {isLoading && <p>در حال بارگذاری...</p>}
      {isError && <p>خطا در دریافت لیست تورها.</p>}

      {data && (
        <>
          <table>
            <thead>
              <tr>
                <th>عنوان</th>
                <th>مقصد</th>
                <th>تاریخ شروع</th>
                <th>قیمت</th>
                <th>ظرفیت</th>
                <th>وضعیت</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.data.map((t) => (
                <tr key={t.id}>
                  <td>
                    <Link to={`/trips/${t.id}`}>{t.title}</Link>
                  </td>
                  <td>{t.destination}</td>
                  <td>{new Date(t.start_date).toLocaleDateString('fa-IR')}</td>
                  <td>{Number(t.price).toLocaleString('fa-IR')}</td>
                  <td>
                    {t.remaining_capacity} / {t.capacity}
                  </td>
                  <td>
                    <span className="badge">{t.status}</span>
                  </td>
                  <td>
                    <button className="danger" onClick={() => handleDelete(t.id)}>
                      حذف
                    </button>
                  </td>
                </tr>
              ))}
              {data.data.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', color: '#888' }}>
                    توری یافت نشد
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
