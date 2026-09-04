interface PaginationProps {
  total: number
  limit: number
  offset: number
  onOffsetChange: (offset: number) => void
}

export default function Pagination({ total, limit, offset, onOffsetChange }: PaginationProps) {
  const page = Math.floor(offset / limit) + 1
  const totalPages = Math.max(Math.ceil(total / limit), 1)

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 12 }}>
      <button
        className="secondary"
        disabled={offset === 0}
        onClick={() => onOffsetChange(Math.max(offset - limit, 0))}
      >
        قبلی
      </button>
      <span style={{ fontSize: 13 }}>
        صفحه {page} از {totalPages} ({total} مورد)
      </span>
      <button
        className="secondary"
        disabled={offset + limit >= total}
        onClick={() => onOffsetChange(offset + limit)}
      >
        بعدی
      </button>
    </div>
  )
}
