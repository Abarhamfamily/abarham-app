import { Fragment, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchWallets, fetchWalletTransactions, adjustWallet } from '../api/wallet'
import Pagination from '../components/Pagination'

const LIMIT = 20

export default function WalletPage() {
  const [search, setSearch] = useState('')
  const [offset, setOffset] = useState(0)
  const [expandedWalletId, setExpandedWalletId] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-wallets', search, offset],
    queryFn: () => fetchWallets({ search: search || undefined, limit: LIMIT, offset }),
  })

  const { data: transactions } = useQuery({
    queryKey: ['admin-wallet-transactions', expandedWalletId],
    queryFn: () => fetchWalletTransactions(expandedWalletId as string),
    enabled: Boolean(expandedWalletId),
  })

  const handleAdjust = async (walletId: string) => {
    const amountStr = prompt('مبلغ تعدیل (برای کاهش، عدد منفی وارد کنید):')
    if (!amountStr) return
    const description = prompt('توضیح این تعدیل:') || 'تعدیل دستی ادمین'
    try {
      await adjustWallet(walletId, amountStr, description)
      queryClient.invalidateQueries({ queryKey: ['admin-wallets'] })
      queryClient.invalidateQueries({ queryKey: ['admin-wallet-transactions', walletId] })
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'تعدیل با خطا مواجه شد')
    }
  }

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>کیف پول‌ها</h1>

      <div className="form-row" style={{ maxWidth: 320 }}>
        <input
          placeholder="جست‌وجو در نام یا شماره تماس کاربر"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value)
            setOffset(0)
          }}
        />
      </div>

      {isLoading && <p>در حال بارگذاری...</p>}
      {isError && <p>خطا در دریافت لیست کیف‌پول‌ها.</p>}

      {data && (
        <>
          <table>
            <thead>
              <tr>
                <th>کاربر</th>
                <th>موجودی</th>
                <th>مجموع واریزی</th>
                <th>مجموع برداشتی</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.data.map((w) => (
                <Fragment key={w.id}>
                  <tr>
                    <td>
                      {w.user_full_name}
                      <br />
                      <span style={{ fontSize: 12, color: '#888' }}>{w.user_phone_number}</span>
                    </td>
                    <td>{Number(w.balance).toLocaleString('fa-IR')} تومان</td>
                    <td>{Number(w.total_deposited).toLocaleString('fa-IR')}</td>
                    <td>{Number(w.total_withdrawn).toLocaleString('fa-IR')}</td>
                    <td style={{ display: 'flex', gap: 6 }}>
                      <button onClick={() => handleAdjust(w.id)}>تعدیل موجودی</button>
                      <button
                        className="secondary"
                        onClick={() => setExpandedWalletId(expandedWalletId === w.id ? null : w.id)}
                      >
                        {expandedWalletId === w.id ? 'بستن تراکنش‌ها' : 'مشاهده تراکنش‌ها'}
                      </button>
                    </td>
                  </tr>
                  {expandedWalletId === w.id && (
                    <tr>
                      <td colSpan={5} style={{ background: '#fafafa' }}>
                        <table>
                          <thead>
                            <tr>
                              <th>مبلغ</th>
                              <th>نوع</th>
                              <th>وضعیت</th>
                              <th>توضیح</th>
                              <th>تاریخ</th>
                            </tr>
                          </thead>
                          <tbody>
                            {transactions?.map((t) => (
                              <tr key={t.id}>
                                <td>{Number(t.amount).toLocaleString('fa-IR')}</td>
                                <td>{t.type}</td>
                                <td>{t.status}</td>
                                <td>{t.description || '—'}</td>
                                <td>{new Date(t.created_at).toLocaleDateString('fa-IR')}</td>
                              </tr>
                            ))}
                            {(!transactions || transactions.length === 0) && (
                              <tr>
                                <td colSpan={5} style={{ textAlign: 'center', color: '#888' }}>
                                  تراکنشی یافت نشد
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
              {data.data.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', color: '#888' }}>
                    کیف‌پولی یافت نشد
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
