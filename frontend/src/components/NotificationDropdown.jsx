import React, { useState, useEffect, useRef } from 'react'

export default function NotificationDropdown({
  isOpen,
  onClose,
  alarms = [],
  trades = [],
  onSelectStock,
  onOpenTradeModal
}) {
  const [filter, setFilter] = useState('ALL') // ALL, ALARMS, TRADES
  const [dismissed, setDismissed] = useState([])
  const dropdownRef = useRef(null)

  // Close when clicking outside
  useEffect(() => {
    if (!isOpen) return
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const activeAlarms = alarms.filter(a => !dismissed.includes(`alarm-${a.id || a.stock_symbol}`))
  const recentTrades = trades.slice(0, 5).filter(t => !dismissed.includes(`trade-${t.id || t.timestamp}`))

  const totalNotifications = activeAlarms.length + recentTrades.length

  const handleDismiss = (id, e) => {
    e.stopPropagation()
    setDismissed(prev => [...prev, id])
  }

  const handleClearAll = () => {
    const allIds = [
      ...alarms.map(a => `alarm-${a.id || a.stock_symbol}`),
      ...trades.map(t => `trade-${t.id || t.timestamp}`)
    ]
    setDismissed(allIds)
  }

  return (
    <div
      ref={dropdownRef}
      style={{
        position: 'absolute',
        top: 48,
        right: 0,
        width: 380,
        background: 'var(--bg-card)',
        border: '1px solid var(--border-light)',
        borderRadius: 16,
        boxShadow: '0 12px 36px rgba(0,0,0,0.35)',
        zIndex: 1000,
        overflow: 'hidden',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)'
      }}
    >
      {/* Header */}
      <div style={{
        padding: '16px 18px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'var(--bg-base)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 16 }}>🔔</span>
          <span style={{ fontSize: 13, fontWeight: 800, color: 'var(--text-primary)' }}>
            Notifications & Risk Alarms
          </span>
          {activeAlarms.length > 0 && (
            <span style={{
              background: '#f43f5e',
              color: '#ffffff',
              fontSize: 10,
              fontWeight: 800,
              padding: '2px 7px',
              borderRadius: 12
            }}>
              {activeAlarms.length} ALARM{activeAlarms.length > 1 ? 'S' : ''}
            </span>
          )}
        </div>

        {totalNotifications > 0 && (
          <button
            onClick={handleClearAll}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: 11,
              cursor: 'pointer',
              fontWeight: 600
            }}
          >
            Clear All
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--border)',
        background: 'var(--bg-card)',
        padding: '4px 8px'
      }}>
        <TabButton label="All" count={totalNotifications} active={filter === 'ALL'} onClick={() => setFilter('ALL')} />
        <TabButton label="Risk Alarms" count={activeAlarms.length} active={filter === 'ALARMS'} onClick={() => setFilter('ALARMS')} alert={activeAlarms.length > 0} />
        <TabButton label="Trade Ledger" count={recentTrades.length} active={filter === 'TRADES'} onClick={() => setFilter('TRADES')} />
      </div>

      {/* Notifications Body */}
      <div style={{ maxHeight: 360, overflowY: 'auto', padding: '10px 12px', display: 'flex', flexDirection: 'column', gap: 8 }}>
        {totalNotifications === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>✨</div>
            <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>All Clear!</div>
            <div style={{ fontSize: 11, marginTop: 4 }}>No active stop-loss breaches or unread alarms.</div>
          </div>
        ) : (
          <>
            {/* 1. Active Risk Alarms (Stop-Loss / Target Triggers) */}
            {(filter === 'ALL' || filter === 'ALARMS') && activeAlarms.map(alarm => {
              const isSL = alarm.alarm_status === 'STOP_LOSS_HIT'
              const curPrice = alarm.current_price || alarm.buy_price || 0
              return (
                <div
                  key={`alarm-${alarm.id || alarm.stock_symbol}`}
                  style={{
                    padding: '12px 14px',
                    borderRadius: 12,
                    background: isSL ? 'rgba(244, 63, 94, 0.08)' : 'rgba(16, 185, 129, 0.08)',
                    border: isSL ? '1px solid rgba(244, 63, 94, 0.3)' : '1px solid rgba(16, 185, 129, 0.3)',
                    position: 'relative'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ fontSize: 14 }}>{isSL ? '🚨' : '🎯'}</span>
                      <span style={{ fontWeight: 800, fontSize: 12.5, color: isSL ? '#f43f5e' : '#10b981' }}>
                        {isSL ? 'STOP-LOSS TRIGGERED' : 'TARGET ACHIEVED'}
                      </span>
                    </div>
                    <button
                      onClick={(e) => handleDismiss(`alarm-${alarm.id || alarm.stock_symbol}`, e)}
                      style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 12 }}
                    >
                      ✕
                    </button>
                  </div>

                  <div style={{ fontSize: 12, color: 'var(--text-primary)', marginBottom: 8 }}>
                    <strong>{alarm.stock_symbol}</strong> price is <strong>₹{curPrice.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</strong>
                    {isSL ? ` (Breached Stop-Loss ₹${alarm.stop_loss})` : ` (Hit Target ₹${alarm.target_price})`}
                  </div>

                  <div style={{ display: 'flex', gap: 8 }}>
                    <button
                      onClick={() => {
                        onSelectStock?.(alarm.stock_symbol)
                        onClose()
                      }}
                      className="btn"
                      style={{ padding: '4px 10px', fontSize: 10.5, borderRadius: 6 }}
                    >
                      📈 View Chart
                    </button>
                    <button
                      onClick={() => {
                        onOpenTradeModal?.(alarm.stock_symbol, curPrice, 'SELL')
                        onClose()
                      }}
                      className="btn btn-primary"
                      style={{
                        padding: '4px 10px',
                        fontSize: 10.5,
                        borderRadius: 6,
                        background: isSL ? '#f43f5e' : '#10b981',
                        borderColor: isSL ? '#e11d48' : '#059669'
                      }}
                    >
                      ⚡ {isSL ? 'Exit & Stop Loss' : 'Book Profit Now'}
                    </button>
                  </div>
                </div>
              )
            })}

            {/* 2. Recent Trade Executions */}
            {(filter === 'ALL' || filter === 'TRADES') && recentTrades.map(trade => (
              <div
                key={`trade-${trade.id || trade.timestamp}`}
                style={{
                  padding: '10px 12px',
                  borderRadius: 10,
                  background: 'var(--bg-base)',
                  border: '1px solid var(--border)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{
                    width: 26,
                    height: 26,
                    borderRadius: '50%',
                    background: trade.action === 'BUY' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
                    color: trade.action === 'BUY' ? '#10b981' : '#f43f5e',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 11,
                    fontWeight: 800
                  }}>
                    {trade.action === 'BUY' ? '↓' : '↑'}
                  </div>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>
                      {trade.action} {trade.stock}
                    </div>
                    <div style={{ fontSize: 10.5, color: 'var(--text-secondary)' }}>
                      {trade.shares} shares @ ₹{(trade.price || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                    </div>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 9.5, color: 'var(--text-muted)' }}>
                    {trade.timestamp ? new Date(trade.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recent'}
                  </div>
                  <button
                    onClick={(e) => handleDismiss(`trade-${trade.id || trade.timestamp}`, e)}
                    style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 10, marginTop: 2 }}
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </>
        )}
      </div>

      {/* Footer */}
      <div style={{
        padding: '10px 16px',
        borderTop: '1px solid var(--border)',
        background: 'var(--bg-base)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: 11,
        color: 'var(--text-muted)'
      }}>
        <span>System: <strong>AI Risk Engine Active</strong></span>
        <button
          onClick={onClose}
          className="btn"
          style={{ padding: '3px 8px', fontSize: 10.5, borderRadius: 6 }}
        >
          Close
        </button>
      </div>
    </div>
  )
}

function TabButton({ label, count, active, onClick, alert }) {
  return (
    <button
      onClick={onClick}
      style={{
        flex: 1,
        padding: '6px 8px',
        background: active ? 'var(--nav-active-bg)' : 'transparent',
        color: active ? 'var(--nav-active-color)' : 'var(--text-secondary)',
        border: 'none',
        borderRadius: 8,
        fontSize: 11,
        fontWeight: active ? 700 : 500,
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 5
      }}
    >
      <span>{label}</span>
      {count > 0 && (
        <span style={{
          fontSize: 9,
          fontWeight: 800,
          padding: '1px 5px',
          borderRadius: 8,
          background: alert ? '#f43f5e' : 'rgba(59, 130, 246, 0.2)',
          color: alert ? '#ffffff' : 'var(--blue)'
        }}>
          {count}
        </span>
      )}
    </button>
  )
}
