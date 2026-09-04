import React from 'react'

const formatINR = (val, maxDec = 2) => {
  const n = Number(val)
  return isNaN(n) ? '0' : n.toLocaleString('en-IN', { maximumFractionDigits: maxDec })
}

export default function MetricsCard({ signal }) {
  if (!signal) {
    return (
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div className="label">Position & Capital Metrics</div>
        <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>Select a stock to view blocked capital and live position value</div>
      </div>
    )
  }

  const fb = signal.ai_feedback || {}
  const pos = fb.position || {}
  const shares = Number(pos.shares || signal.shares || 0)
  const avgBuyPrice = Number(pos.avg_buy_price || 0)
  const currentPrice = Number(signal.price || 0)

  const investedBlocked = roundNumber(shares * avgBuyPrice)
  const currentTotalVal = roundNumber(shares * currentPrice)
  const pnlInr = roundNumber(currentTotalVal - investedBlocked)
  const pnlPct = (investedBlocked > 0) ? ((pnlInr / investedBlocked) * 100) : 0
  const isProfit = pnlInr >= 0

  const targetPrice = Number(fb.target_price || roundNumber(currentPrice * 1.08))
  const stopLoss = Number(fb.stop_loss || roundNumber(currentPrice * 0.95))
  const targetUpsideInr = shares > 0 ? roundNumber((targetPrice - avgBuyPrice) * shares) : 0
  const maxLossAtSL = shares > 0 ? roundNumber((avgBuyPrice - stopLoss) * shares) : 0

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
        <div className="label">
          Position & Blocked Capital Metrics — <span style={{ color: '#93c5fd', fontWeight: 700 }}>{signal.stock}</span>
        </div>
        <span className={`badge ${shares > 0 ? 'badge-buy' : 'badge-hold'}`} style={{ fontSize: 10 }}>
          {shares > 0 ? `🟢 ${shares} SHARES ACTIVE` : '⚪ NO ACTIVE POSITION'}
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
        gap: 10
      }}>
        {/* Blocked Capital */}
        <div style={{ background: 'var(--bg-base)', borderRadius: 8, padding: '10px 12px' }}>
          <div className="label" style={{ fontSize: 10 }}>Capital Blocked (Invested)</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginTop: 2 }}>
            ₹{formatINR(investedBlocked, 0)}
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
            {shares > 0 ? `${shares} shares @ avg ₹${formatINR(avgBuyPrice, 2)}` : '0 shares'}
          </div>
        </div>

        {/* Current Value */}
        <div style={{ background: 'var(--bg-base)', borderRadius: 8, padding: '10px 12px' }}>
          <div className="label" style={{ fontSize: 10 }}>Current Position Value</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: '#93c5fd', marginTop: 2 }}>
            ₹{formatINR(currentTotalVal, 0)}
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
            Live @ ₹{formatINR(currentPrice, 2)}
          </div>
        </div>

        {/* Unrealized P&L */}
        <div style={{ background: 'var(--bg-base)', borderRadius: 8, padding: '10px 12px' }}>
          <div className="label" style={{ fontSize: 10 }}>Unrealized Net P&L</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: isProfit ? 'var(--green)' : 'var(--red)', marginTop: 2 }}>
            {shares > 0 ? `${isProfit ? '+' : ''}₹${formatINR(Math.abs(pnlInr), 0)}` : '₹0'}
          </div>
          <div style={{ fontSize: 10, fontWeight: 600, color: isProfit ? 'var(--green)' : 'var(--red)', marginTop: 2 }}>
            {shares > 0 ? `${isProfit ? '+' : ''}${pnlPct.toFixed(2)}%` : '0.00%'}
          </div>
        </div>

        {/* Target Gain */}
        <div style={{ background: 'var(--bg-base)', borderRadius: 8, padding: '10px 12px' }}>
          <div className="label" style={{ fontSize: 10, color: 'var(--green)' }}>Target Gain (+Profit)</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--green)', marginTop: 2 }}>
            🎯 ₹{formatINR(targetPrice, 1)}
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
            {shares > 0 ? `+₹${formatINR(targetUpsideInr, 0)} projected` : '+8.0% potential'}
          </div>
        </div>

        {/* Stop Loss Level */}
        <div style={{ background: 'var(--bg-base)', borderRadius: 8, padding: '10px 12px' }}>
          <div className="label" style={{ fontSize: 10, color: 'var(--red)' }}>Stop Loss (Risk Gate)</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--red)', marginTop: 2 }}>
            🚨 ₹{formatINR(stopLoss, 1)}
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
            {shares > 0 ? `-₹${formatINR(maxLossAtSL, 0)} max risk` : '-5.0% risk gate'}
          </div>
        </div>
      </div>
    </div>
  )
}

function roundNumber(num) {
  return Math.round(((Number(num) || 0) + Number.EPSILON) * 100) / 100
}
