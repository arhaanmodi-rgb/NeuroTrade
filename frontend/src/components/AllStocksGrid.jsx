import React from 'react'

const COLOR  = { BUY: 'var(--green)', HOLD: 'var(--yellow)', SELL: 'var(--red)' }
const BG     = { BUY: 'var(--green-bg)', HOLD: 'var(--yellow-bg)', SELL: 'var(--red-bg)' }
const ARROW  = { BUY: '↑', HOLD: '→', SELL: '↓' }
const SECTOR = {
  RELIANCE:  'Energy',
  TCS:       'IT',
  INFY:      'IT',
  HDFCBANK:  'Banking',
  ICICIBANK: 'Banking',
}

function SignalCard({ sig, loading, onClick, isSelected }) {
  if (loading) {
    return (
      <div className="card skeleton" style={{ height: 110, cursor: 'pointer' }} />
    )
  }
  if (!sig) return null

  const color = COLOR[sig.action] || 'var(--text-muted)'
  const returnPct = sig.portfolio_value
    ? (((sig.portfolio_value - 100000) / 100000) * 100).toFixed(1)
    : '0.0'
  const isProfit = parseFloat(returnPct) >= 0

  return (
    <div
      className="card"
      onClick={onClick}
      style={{
        cursor: 'pointer',
        borderColor: isSelected ? 'var(--blue)' : 'var(--border)',
        background: isSelected ? 'var(--blue-bg)' : 'var(--bg-card)',
        transition: 'all 0.15s'
      }}
    >
      {/* Top row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>{sig.stock}</div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{SECTOR[sig.stock] || 'NSE'}</div>
        </div>
        <div style={{
          background: BG[sig.action],
          color,
          borderRadius: 6,
          padding: '4px 10px',
          fontSize: 12,
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          gap: 4
        }}>
          {ARROW[sig.action]} {sig.action}
        </div>
      </div>

      {/* Price + return */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>Price</div>
          <div style={{ fontSize: 16, fontWeight: 700 }}>
            ₹{(sig.price || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>Return</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: isProfit ? 'var(--green)' : 'var(--red)' }}>
            {isProfit ? '+' : ''}{returnPct}%
          </div>
        </div>
      </div>

      {/* Confidence bar */}
      <div style={{ marginTop: 10 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>AI Confidence</span>
          <span style={{ fontSize: 10, color }}>
            {((sig.confidence || 0) * 100).toFixed(0)}%
          </span>
        </div>
        <div className="q-bar-track" style={{ height: 4 }}>
          <div className="q-bar-fill" style={{
            width: `${(sig.confidence || 0) * 100}%`,
            background: color
          }} />
        </div>
      </div>
    </div>
  )
}

export default function AllStocksGrid({ allSignals, loading, onSelectStock, selectedStock }) {
  const signals = allSignals?.signals || []

  return (
    <div>
      <div className="label" style={{ marginBottom: 12 }}>All Stocks — AI Signals Overview</div>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: 12
      }}>
        {loading && !signals.length
          ? [0, 1, 2, 3, 4].map(i => (
              <div key={i} className="card skeleton" style={{ height: 140 }} />
            ))
          : signals.map(sig => (
              <SignalCard
                key={sig.stock}
                sig={sig}
                loading={false}
                onClick={() => onSelectStock(sig.stock)}
                isSelected={selectedStock === sig.stock}
              />
            ))
        }
      </div>
    </div>
  )
}
