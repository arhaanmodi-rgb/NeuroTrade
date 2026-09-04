import React from 'react'

const INDICES = [
  { symbol: 'NIFTY 50', value: '24,852.15', change: '+148.60', pct: '+0.60%', isUp: true },
  { symbol: 'SENSEX', value: '81,332.72', change: '+472.10', pct: '+0.58%', isUp: true },
  { symbol: 'BANK NIFTY', value: '51,280.40', change: '-92.30', pct: '-0.18%', isUp: false },
  { symbol: 'INDIA VIX', value: '13.42', change: '-0.35', pct: '-2.54%', isUp: false },
  { symbol: 'NIFTY IT', value: '38,914.50', change: '+310.20', pct: '+0.80%', isUp: true },
  { symbol: 'NIFTY AUTO', value: '25,410.85', change: '+185.40', pct: '+0.73%', isUp: true }
]

export default function MarketTickerStrip() {
  return (
    <div style={{
      background: 'rgba(6, 8, 14, 0.9)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
      padding: '5px 24px',
      display: 'flex',
      alignItems: 'center',
      gap: 24,
      overflowX: 'auto',
      fontSize: 11,
      whiteSpace: 'nowrap'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#64748b', fontWeight: 700, fontSize: 10, letterSpacing: 0.8, textTransform: 'uppercase' }}>
        <span className="pulse-dot" style={{ background: '#10b981', width: 6, height: 6 }} />
        NSE / BSE LIVE:
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
        {INDICES.map(idx => (
          <div key={idx.symbol} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ color: '#94a3b8', fontWeight: 600 }}>{idx.symbol}</span>
            <span className="mono-num" style={{ fontWeight: 700, color: '#f8fafc' }}>{idx.value}</span>
            <span className="mono-num" style={{
              color: idx.isUp ? '#34d399' : '#fb7185',
              fontWeight: 600,
              fontSize: 10
            }}>
              {idx.isUp ? '▲' : '▼'} {idx.change} ({idx.pct})
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
