import React from 'react'

const FEATURED_CARDS = [
  {
    symbol: 'RELIANCE',
    name: 'Reliance Industries Ltd',
    exchange: 'NSE',
    price: '1,302.50',
    changePct: '+1.15%',
    isUp: true,
    logoBg: '#1e3a8a',
    icon: '🏢'
  },
  {
    symbol: 'TCS',
    name: 'Tata Consultancy Services',
    exchange: 'NSE',
    price: '2,320.10',
    changePct: '+0.85%',
    isUp: true,
    logoBg: '#0f766e',
    icon: '💻'
  },
  {
    symbol: 'INFY',
    name: 'Infosys Limited',
    exchange: 'NSE',
    price: '1,130.30',
    changePct: '+1.45%',
    isUp: true,
    logoBg: '#2563eb',
    icon: '🌐'
  },
  {
    symbol: 'HDFCBANK',
    name: 'HDFC Bank Ltd',
    exchange: 'NSE',
    price: '706.65',
    changePct: '+0.60%',
    isUp: true,
    logoBg: '#831843',
    icon: '🏦'
  }
]

export default function TopStockCards({ onSelectStock, selectedStock, allSignals }) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
      gap: 16,
      marginBottom: 24
    }}>
      {FEATURED_CARDS.map(card => {
        const liveSig = allSignals?.signals?.find(s => s.stock === card.symbol)
        const displayPrice = liveSig?.price ? liveSig.price.toLocaleString('en-IN', { maximumFractionDigits: 2 }) : card.price
        const isSelected = selectedStock === card.symbol

        return (
          <div
            key={card.symbol}
            onClick={() => onSelectStock(card.symbol)}
            className="card"
            style={{
              padding: '18px 20px',
              cursor: 'pointer',
              border: isSelected ? '1.5px solid var(--blue)' : '1px solid var(--border)',
              background: isSelected ? 'var(--bg-card-selected)' : 'var(--bg-card)',
              borderRadius: 14,
              boxShadow: isSelected ? '0 4px 20px rgba(59, 130, 246, 0.15)' : 'var(--shadow-subtle)',
              transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
            }}
          >
            {/* Top row: Logo + Name */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
              <div style={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                background: card.logoBg,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 18,
                boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                flexShrink: 0
              }}>
                {card.icon}
              </div>
              <div style={{ overflow: 'hidden' }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', whiteSpace: 'nowrap' }}>
                  {card.symbol}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-secondary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {card.name}
                </div>
              </div>
            </div>

            {/* Bottom row: Price + Change Pill */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
              <div className="mono-num" style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)' }}>
                ₹{displayPrice}
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                padding: '3px 8px',
                borderRadius: 20,
                background: card.isUp ? 'rgba(16, 185, 129, 0.12)' : 'rgba(244, 63, 94, 0.12)',
                color: card.isUp ? '#10b981' : '#f43f5e',
                fontSize: 11,
                fontWeight: 700
              }}>
                <span>{card.isUp ? '↑' : '↓'}</span>
                <span>{card.changePct}</span>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
