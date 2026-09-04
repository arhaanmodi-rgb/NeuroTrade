import React from 'react'

const SECTOR = {
  RELIANCE:  'Energy / Conglom.',
  TCS:       'IT Services',
  INFY:      'IT Services',
  HDFCBANK:  'Private Banking',
  ICICIBANK: 'Private Banking',
  SBIN:      'PSU Banking',
  TATAMOTORS:'Automobile',
  ZOMATO:    'Consumer Tech',
  PAYTM:     'Fintech',
  KORE:      'SME Telecom'
}

export default function StockSelector({ stocks, selected, onSelect, allSignals, onOpenSearch }) {
  const signalMap = {}
  if (allSignals?.signals) {
    allSignals.signals.forEach(s => { signalMap[s.stock] = s })
  }

  return (
    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
      {stocks.map(stock => {
        const sig = signalMap[stock]
        const isSelected = selected === stock
        const actionColor = sig
          ? sig.action === 'BUY'  ? 'var(--green)'
          : sig.action === 'SELL' ? 'var(--red)'
          : 'var(--yellow)'
          : 'var(--text-muted)'

        return (
          <button
            key={stock}
            onClick={() => onSelect(stock)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: 3,
              padding: '9px 14px',
              borderRadius: 10,
              border: isSelected ? '2px solid var(--blue)' : '2px solid var(--border)',
              background: isSelected ? 'var(--blue-bg)' : 'var(--bg-card)',
              cursor: 'pointer',
              transition: 'all 0.15s',
              minWidth: 110
            }}
          >
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              width: '100%',
              alignItems: 'center',
              gap: 8
            }}>
              <span style={{
                fontSize: 13,
                fontWeight: isSelected ? 700 : 500,
                color: isSelected ? '#93c5fd' : 'var(--text-primary)'
              }}>
                {stock}
              </span>
              {sig && (
                <span style={{
                  fontSize: 9,
                  fontWeight: 700,
                  color: actionColor,
                  letterSpacing: 0.5
                }}>
                  {sig.action}
                </span>
              )}
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
              {SECTOR[stock] || 'NSE / BSE'}
            </div>
            {sig && (
              <div style={{ fontSize: 10, color: 'var(--text-secondary)' }}>
                ₹{(sig.price || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
              </div>
            )}
          </button>
        )
      })}

      {/* Button to search across all 7000 stocks */}
      <button
        onClick={onOpenSearch}
        className="btn btn-primary"
        style={{
          padding: '12px 18px',
          borderRadius: 10,
          border: '1px dashed var(--blue)',
          fontSize: 13,
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          gap: 6
        }}
        title="Search across all 7,000+ NSE and BSE tickers"
      >
        <span>🔍</span>
        <span>+ Search 7,000+ Stocks</span>
      </button>
    </div>
  )
}
