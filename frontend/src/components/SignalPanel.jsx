import React from 'react'

const COLOR = { BUY: '#10b981', HOLD: '#f59e0b', SELL: '#ef4444' }
const EMOJI = { BUY: '🟢', HOLD: '🟡', SELL: '🔴' }

function SkeletonSignal() {
  return (
    <div className="card" style={{ minHeight: 340 }}>
      <div className="skeleton" style={{ height: 14, width: '60%', marginBottom: 24 }} />
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <div className="skeleton" style={{ height: 64, width: 64, borderRadius: '50%' }} />
        <div className="skeleton" style={{ height: 48, width: 140 }} />
        <div className="skeleton" style={{ height: 14, width: 100 }} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20 }}>
        <div className="skeleton" style={{ height: 64, borderRadius: 8 }} />
        <div className="skeleton" style={{ height: 64, borderRadius: 8 }} />
      </div>
      {[0, 1, 2].map(i => <div key={i} className="skeleton" style={{ height: 8, marginBottom: 8 }} />)}
    </div>
  )
}

export default function SignalPanel({ signal, loading, onOpenTradeModal }) {
  if (loading) return <SkeletonSignal />

  if (!signal) {
    return (
      <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 300, gap: 12 }}>
        <span style={{ fontSize: 40 }}>📡</span>
        <div style={{ color: 'var(--text-secondary)', fontSize: 14 }}>No signal available</div>
        <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>Make sure the API is running</div>
      </div>
    )
  }

  const color = COLOR[signal.action] || '#9ca3af'
  const confidencePct = ((signal.confidence || 0) * 100).toFixed(1)
  const [qHold = 0, qBuy = 0, qSell = 0] = signal.q_values || []
  
  const sharesHeld = signal.shares || 0
  const isHolding = sharesHeld > 0
  const canSell = isHolding

  return (
    <div className="card">
      {/* Header row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div className="label">AI Signal & Position</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="badge badge-demo" style={{ fontSize: 10 }}>
            {signal.data_source || 'LIVE'}
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            {signal.timestamp ? new Date(signal.timestamp).toLocaleTimeString('en-IN') : ''}
          </span>
        </div>
      </div>

      {/* Action — big centred display */}
      <div style={{ textAlign: 'center', marginBottom: 20 }}>
        <div style={{ fontSize: 48, marginBottom: 4 }}>{EMOJI[signal.action]}</div>
        <div style={{
          fontSize: 46,
          fontWeight: 800,
          color,
          letterSpacing: 4,
          textShadow: `0 0 35px ${color}50`,
          lineHeight: 1.1
        }}>
          {signal.action}
        </div>
        <div style={{ marginTop: 8, display: 'flex', justifyContent: 'center', gap: 8 }}>
          <span className="label">AI Confidence</span>
          <span style={{ color, fontWeight: 700, fontSize: 14 }}>{confidencePct}%</span>
        </div>
      </div>

      {/* Position Holding State Alert */}
      <div style={{
        background: isHolding ? 'rgba(16, 185, 129, 0.12)' : 'var(--bg-base)',
        border: `1px solid ${isHolding ? '#065f46' : 'var(--border)'}`,
        borderRadius: 8,
        padding: '10px 14px',
        marginBottom: 16,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <div className="label" style={{ fontSize: 10 }}>Position Holding</div>
          <div style={{ fontSize: 13, fontWeight: 700, color: isHolding ? 'var(--green)' : 'var(--text-secondary)' }}>
            {isHolding ? `🟢 ${sharesHeld.toFixed(2)} Shares Owned` : '⚪ 0 Shares (Not Held)'}
          </div>
        </div>
        <div>
          <span className={`badge ${canSell ? 'badge-buy' : 'badge-hold'}`} style={{ fontSize: 10 }}>
            {canSell ? '✓ SELL ALLOWED' : 'SELL LOCKED (0 SHARES)'}
          </span>
        </div>
      </div>

      {/* Interactive Record Trade Buttons (Opens Qty & Cost Price Dialog) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 18 }}>
        <button
          onClick={() => onOpenTradeModal(signal.stock, signal.price, 'BUY')}
          className="btn"
          style={{
            background: 'var(--green-bg)',
            color: 'var(--green)',
            border: '1px solid #065f46',
            padding: '11px',
            fontWeight: 700,
            justifyContent: 'center',
            fontSize: 13
          }}
        >
          ⚡ Record BUY Entry
        </button>

        <button
          onClick={() => onOpenTradeModal(signal.stock, signal.price, 'SELL')}
          disabled={!canSell}
          className="btn"
          style={{
            background: canSell ? 'var(--red-bg)' : '#1a1f2c',
            color: canSell ? 'var(--red)' : '#6b7280',
            border: `1px solid ${canSell ? '#7f1d1d' : 'var(--border)'}`,
            padding: '11px',
            fontWeight: 700,
            justifyContent: 'center',
            cursor: canSell ? 'pointer' : 'not-allowed',
            opacity: canSell ? 1 : 0.6,
            fontSize: 13
          }}
          title={canSell ? 'Record Sell Exit' : 'Cannot Sell: You must record a buy entry first.'}
        >
          {canSell ? '💰 Record SELL Exit' : '🔒 SELL (Buy 1st)'}
        </button>
      </div>

      {/* Stats grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 16 }}>
        <div style={{ background: 'var(--bg-base)', borderRadius: 8, padding: '10px 12px' }}>
          <div className="label" style={{ marginBottom: 2 }}>Current Price</div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
            ₹{(signal.price || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
          </div>
        </div>
        <div style={{ background: 'var(--bg-base)', borderRadius: 8, padding: '10px 12px' }}>
          <div className="label" style={{ marginBottom: 2 }}>Available Cash</div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
            ₹{(signal.cash || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
        </div>
      </div>

      {/* Q-Value bars */}
      <div>
        <div className="label" style={{ marginBottom: 8 }}>Neural Decision Q-Weights</div>
        {[['HOLD', qHold, 'var(--yellow)'], ['BUY', qBuy, 'var(--green)'], ['SELL', qSell, 'var(--red)']].map(([lbl, val, col]) => {
          const all = [Math.abs(qHold), Math.abs(qBuy), Math.abs(qSell)]
          const maxQ = Math.max(...all, 0.001)
          const barPct = (Math.abs(val) / maxQ) * 100
          const isChosen = (lbl === signal.action)
          return (
            <div key={lbl} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <div style={{ width: 36, fontSize: 10, color: col, fontWeight: isChosen ? 700 : 400 }}>{lbl}</div>
              <div className="q-bar-track" style={{ height: 5 }}>
                <div className="q-bar-fill" style={{ width: `${barPct}%`, background: col, opacity: isChosen ? 1 : 0.5 }} />
              </div>
              <div style={{ width: 50, fontSize: 10, color: 'var(--text-secondary)', textAlign: 'right', fontFamily: 'monospace' }}>
                {val.toFixed(4)}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
