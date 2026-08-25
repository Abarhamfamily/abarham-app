import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchUsers, updateUser } from '../api/users'
import Pagination from '../components/Pagination'

const LIMIT = 20

export default function UsersPage() {
  const [search, setSearch] = useState('')
  const [offset, setOffset] = useState(0)
  const queryClient = useQueryClient()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-users', search, offset],
    queryFn: () => fetchUsers({ search: search || undefined, limit: LIMIT, offset }),
  })

  const toggleActive = async (id: string, current: boolean) => {
    await updateUser(id, { is_active: !current })
    queryClient.invalidateQueries({ queryKey: ['admin-users'] })
  }

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>کاربران</h1>

      <div className="form-row" style={{ maxWidth: 320 }}>
        <input
          placeholder="جست‌وجو در نام، شماره تماس یا کد ملی"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value)
            setOffset(0)
          }}
        />
      </div>

      {isLoading && <p>در حال بارگذاری...</p>}
      {isError && <p>خطا در دریافت لیست کاربران.</p>}

      {data && (
        <>
          <table>
            <thead>
              <tr>
                <th>نام</th>
                <th>شماره تماس</th>
                <th>ایمیل</th>
                <th>وضعیت</th>
                <th>تاریخ عضویت</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.data.map((u) => (
                <tr key={u.id}>
                  <td>
                    <Link to={`/users/${u.id}`}>{u.full_name}</Link>
                  </td>
                  <td>{u.phone_number}</td>
                  <td>{u.email || '—'}</td>
                  <td>
                    <span className="badge" style={{ background: u.is_active ? '#dcfce7' : '#fee2e2', color: u.is_active ? '#166534' : '#991b1b' }}>
                      {u.is_active ? 'فعال' : 'غیرفعال'}
                    </span>
                  </td>
                  <td>{new Date(u.created_at).toLocaleDateString('fa-IR')}</td>
                  <td>
                    <button className="secondary" onClick={() => toggleActive(u.id, u.is_active)}>
                      {u.is_active ? 'غیرفعال کردن' : 'فعال کردن'}
                    </button>
                  </td>
                </tr>
              ))}
              {data.data.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', color: '#888' }}>
                    کاربری یافت نشد
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
