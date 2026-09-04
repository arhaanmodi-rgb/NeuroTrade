import React from 'react'

export default function AIFeedbackCard({ feedback, stock, price }) {
  if (!feedback) return null

  const {
    headline,
    rationale,
    holding_context,
    risk_level,
    target_price,
    stop_loss,
    indicators,
    position
  } = feedback

  const isHolding = position?.is_holding
  const riskColor = risk_level === 'LOW' ? 'var(--green)' : (risk_level === 'HIGH' ? 'var(--red)' : 'var(--yellow)')

  return (
    <div className="card" style={{
      background: 'linear-gradient(145deg, var(--bg-card), #141b2d)',
      border: '1px solid var(--border-light)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Top Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 20 }}>🧠</span>
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
              AI Market Rationale & Position Feedback
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              Why it IS or IS NOT the best time to trade {stock}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <span className="badge" style={{
            background: risk_level === 'LOW' ? 'var(--green-bg)' : (risk_level === 'HIGH' ? 'var(--red-bg)' : 'var(--yellow-bg)'),
            color: riskColor,
            border: `1px solid ${riskColor}40`
          }}>
            {risk_level} RISK
          </span>
          <span className="badge badge-demo">AI EXPLANATION</span>
        </div>
      </div>

      {/* Headline & Rationale */}
      <div style={{
        background: 'var(--bg-base)',
        borderLeft: `4px solid ${feedback.action === 'BUY' ? 'var(--green)' : (feedback.action === 'SELL' ? 'var(--red)' : 'var(--yellow)')}`,
        borderRadius: '0 8px 8px 0',
        padding: '12px 16px',
        marginBottom: 16
      }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: '#93c5fd', marginBottom: 4 }}>
          {headline}
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-primary)', lineHeight: 1.6 }}>
          {rationale}
        </div>
      </div>

      {/* Position & Holding Notice */}
      <div style={{
        background: isHolding ? 'rgba(16, 185, 129, 0.08)' : 'rgba(107, 114, 128, 0.08)',
        border: `1px solid ${isHolding ? '#065f46' : 'var(--border)'}`,
        borderRadius: 8,
        padding: '10px 14px',
        marginBottom: 16,
        fontSize: 12,
        color: isHolding ? 'var(--green)' : 'var(--text-secondary)'
      }}>
        {holding_context}
      </div>

      {/* Technical Indicators Breakdown Grid */}
      <div className="label" style={{ marginBottom: 8 }}>Key Technical Drivers Analyzed</div>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
        gap: 10,
        marginBottom: 16
      }}>
        {indicators && Object.entries(indicators).map(([key, ind]) => (
          <div key={key} style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            padding: '10px 12px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <span className="label" style={{ fontSize: 10 }}>{key.toUpperCase()}</span>
              <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-primary)' }}>{ind.value}</span>
            </div>
            <div style={{ fontSize: 11, fontWeight: 600, color: '#93c5fd', marginBottom: 2 }}>{ind.status}</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', lineHeight: 1.3 }}>{ind.note}</div>
          </div>
        ))}
      </div>

      {/* Price Target & Stop Loss Levels */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr 1fr',
        gap: 10,
        background: 'var(--bg-base)',
        borderRadius: 8,
        padding: '12px 14px'
      }}>
        <div>
          <div className="label" style={{ fontSize: 10 }}>Current Price</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>₹{price?.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</div>
        </div>
        <div>
          <div className="label" style={{ fontSize: 10 }}>Target (Take Profit)</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--green)' }}>₹{target_price?.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</div>
        </div>
        <div>
          <div className="label" style={{ fontSize: 10 }}>Stop Loss (Risk Gate)</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--red)' }}>₹{stop_loss?.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</div>
        </div>
      </div>
    </div>
  )
}
