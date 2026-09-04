import React from 'react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer
} from 'recharts'

const INITIAL = 100000

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  const color = d?.portfolio >= INITIAL ? 'var(--green)' : 'var(--red)'
  return (
    <div style={{
      background: 'var(--bg-elevated)',
      border: '1px solid var(--border-light)',
      borderRadius: 8,
      padding: '10px 14px',
      fontSize: 12
    }}>
      <div style={{ color: 'var(--text-secondary)', marginBottom: 4 }}>Trade #{d?.index}</div>
      <div style={{ color: 'var(--text-muted)', marginBottom: 6, fontSize: 11 }}>{d?.date} · {d?.stock}</div>
      <div style={{ color, fontWeight: 700, fontSize: 14 }}>
        ₹{d?.portfolio?.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
      </div>
      <div style={{ marginTop: 4 }}>
        <span className={`badge badge-${d?.action?.toLowerCase()}`}>{d?.action}</span>
      </div>
    </div>
  )
}

export default function EquityChart({ trades }) {
  if (!trades || trades.length === 0) {
    return (
      <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 220, gap: 10 }}>
        <span style={{ fontSize: 32 }}>📊</span>
        <div className="label">Portfolio History</div>
        <div style={{ color: 'var(--text-muted)', fontSize: 12, textAlign: 'center' }}>
          No trades logged yet.<br />BUY/SELL signals will chart here.
        </div>
      </div>
    )
  }

  const chartData = trades.map((t, i) => ({
    index: i + 1,
    date: new Date(t.timestamp).toLocaleDateString('en-IN'),
    portfolio: parseFloat(t.portfolio_value),
    action: t.action,
    stock: t.stock
  }))

  const allValues = chartData.map(d => d.portfolio)
  const minVal = Math.min(...allValues, INITIAL)
  const maxVal = Math.max(...allValues, INITIAL)
  const isProfit = chartData[chartData.length - 1]?.portfolio >= INITIAL

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div className="label">Portfolio History</div>
        <div style={{ fontSize: 12, color: isProfit ? 'var(--green)' : 'var(--red)', fontWeight: 600 }}>
          {trades.length} trades logged
        </div>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={chartData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
          <defs>
            <linearGradient id="portfolioGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor={isProfit ? '#10b981' : '#ef4444'} stopOpacity={0.25} />
              <stop offset="95%" stopColor={isProfit ? '#10b981' : '#ef4444'} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis
            dataKey="index"
            stroke="var(--text-muted)"
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            stroke="var(--text-muted)"
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={v => `₹${(v / 1000).toFixed(0)}K`}
            domain={[minVal * 0.99, maxVal * 1.01]}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={INITIAL}
            stroke="var(--border-light)"
            strokeDasharray="6 3"
            label={{ value: 'Initial ₹1L', position: 'right', fill: 'var(--text-muted)', fontSize: 10 }}
          />
          <Area
            type="monotone"
            dataKey="portfolio"
            stroke={isProfit ? '#10b981' : '#ef4444'}
            strokeWidth={2}
            fill="url(#portfolioGrad)"
            dot={false}
            activeDot={{ r: 5, fill: isProfit ? '#10b981' : '#ef4444' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
