import React, { useState } from 'react'

const PAGE_SIZE = 10

export default function TradeHistory({ trades }) {
  const [page, setPage] = useState(1)
  const [filter, setFilter] = useState('ALL')

  const filtered = filter === 'ALL'
    ? trades
    : trades.filter(t => t.action === filter)

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)
  const paginated = filtered.slice().reverse().slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  if (!trades || trades.length === 0) {
    return (
      <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '40px 20px', gap: 10 }}>
        <span style={{ fontSize: 32 }}>🔖</span>
        <div className="label">Trade History</div>
        <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>
          BUY and SELL signals will be logged here automatically.
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 10 }}>
        <div className="label">
          Trade History&nbsp;
          <span style={{ color: 'var(--text-muted)', fontWeight: 400, textTransform: 'none', letterSpacing: 0 }}>
            ({filtered.length} records)
          </span>
        </div>
        {/* Filter tabs */}
        <div style={{ display: 'flex', gap: 6 }}>
          {['ALL', 'BUY', 'SELL'].map(f => (
            <button
              key={f}
              onClick={() => { setFilter(f); setPage(1) }}
              className={`btn ${filter === f ? 'btn-active' : ''}`}
              style={{ padding: '4px 12px', fontSize: 11 }}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead>
            <tr>
              {['#', 'Stock', 'Action', 'Price', 'Shares', 'Portfolio Value', 'Time'].map(h => (
                <th key={h}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginated.map((trade, idx) => {
              const isProfit = trade.portfolio_value >= 100000
              return (
                <tr key={trade.id ?? idx}>
                  <td style={{ color: 'var(--text-muted)' }}>{trade.id}</td>
                  <td style={{ fontWeight: 600 }}>{trade.stock}</td>
                  <td>
                    <span className={`badge badge-${trade.action?.toLowerCase()}`}>
                      {trade.action}
                    </span>
                  </td>
                  <td>₹{parseFloat(trade.price).toLocaleString('en-IN', { maximumFractionDigits: 2 })}</td>
                  <td style={{ color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                    {parseFloat(trade.shares).toFixed(2)}
                  </td>
                  <td style={{ color: isProfit ? 'var(--green)' : 'var(--red)', fontWeight: 600 }}>
                    ₹{parseFloat(trade.portfolio_value).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 11, whiteSpace: 'nowrap' }}>
                    {new Date(trade.timestamp).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', hour12: true })}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 8, marginTop: 16 }}>
          <button className="btn" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>← Prev</button>
          <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Page {page} / {totalPages}</span>
          <button className="btn" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next →</button>
        </div>
      )}
    </div>
  )
}
