import React from 'react'
import { ResponsiveContainer, BarChart, Bar, XAxis, Tooltip } from 'recharts'

export default function SideWidgets({
  holdingsData,
  onSelectStock,
  selectedStock,
  onOpenAddModal
}) {
  const holdings = holdingsData?.holdings || []
  const { total_invested = 0, total_current = 0, total_pnl_inr = 0 } = holdingsData || {}

  const barData = [
    { name: 'Invested', amount: total_invested || 100000, fill: '#3b82f6' },
    { name: 'Current', amount: total_current || 120000, fill: '#10b981' },
    { name: 'Target', amount: (total_current || 120000) * 1.15, fill: '#f59e0b' }
  ]

  const watchlistItems = [
    { symbol: 'TATAMOTORS', name: 'Tata Motors', price: '₹975.25', pct: '+2.45%', isUp: true, icon: '🚗' },
    { symbol: 'VAAH', name: 'Vaah Tech', price: '₹910.20', pct: '+8.20%', isUp: true, icon: '⚡' },
    { symbol: 'RELIANCE', name: 'Reliance Ind', price: '₹1,412.50', pct: '+1.15%', isUp: true, icon: '🏢' },
    { symbol: 'ZOMATO', name: 'Zomato Ltd', price: '₹294.80', pct: '-0.85%', isUp: false, icon: '🍔' },
    { symbol: 'INFY', name: 'Infosys Tech', price: '₹1,920.00', pct: '+0.75%', isUp: true, icon: '💻' }
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* 1. Capital Allocation / Risk Distribution */}
      <div className="card" style={{ padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <h4 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
            Capital & Gain Distribution
          </h4>
          <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>⋮</span>
        </div>

        <div style={{ height: 160, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
              <XAxis dataKey="name" stroke="var(--text-muted)" tick={{ fontSize: 11 }} tickLine={false} />
              <Tooltip
                formatter={(val) => `₹${Math.round(val).toLocaleString('en-IN')}`}
                contentStyle={{
                  background: 'var(--bg-card)',
                  borderColor: 'var(--border)',
                  borderRadius: 8,
                  fontSize: 12
                }}
              />
              <Bar dataKey="amount" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--border)', fontSize: 11 }}>
          <span style={{ color: 'var(--text-secondary)' }}>Net Portfolio Growth:</span>
          <span className="mono-num" style={{ fontWeight: 700, color: total_pnl_inr >= 0 ? '#10b981' : '#f43f5e' }}>
            {total_pnl_inr >= 0 ? '+' : ''}₹{Math.round(total_pnl_inr).toLocaleString('en-IN')}
          </span>
        </div>
      </div>

      {/* 2. My Watchlist */}
      <div className="card" style={{ padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <h4 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
            My Watchlist
          </h4>
          <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>⋮</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {watchlistItems.map(item => {
            const isSelected = selectedStock === item.symbol
            return (
              <div
                key={item.symbol}
                onClick={() => onSelectStock(item.symbol)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 12px',
                  borderRadius: 10,
                  background: isSelected ? 'var(--bg-card-selected)' : 'var(--bg-base)',
                  border: isSelected ? '1px solid var(--blue)' : '1px solid transparent',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) e.currentTarget.style.background = 'var(--bg-card-hover)'
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) e.currentTarget.style.background = 'var(--bg-base)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    background: 'var(--bg-card)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 14
                  }}>
                    {item.icon}
                  </div>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>
                      {item.symbol}
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                      {item.name}
                    </div>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div className="mono-num" style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>
                    {item.price}
                  </div>
                  <div style={{
                    fontSize: 10,
                    fontWeight: 700,
                    color: item.isUp ? '#10b981' : '#f43f5e'
                  }}>
                    {item.isUp ? '↑' : '↓'} {item.pct}
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <button
          onClick={onOpenAddModal}
          className="btn"
          style={{ width: '100%', marginTop: 14, borderRadius: 8, fontSize: 11, fontWeight: 600 }}
        >
          ➕ Add to Watchlist
        </button>
      </div>
    </div>
  )
}
