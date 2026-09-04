import React from 'react'

export default function StopLossAlertBanner({ alarms, onSelectStock, onOpenTradeModal }) {
  if (!alarms || alarms.length === 0) return null

  return (
    <div style={{
      marginBottom: 20,
      display: 'flex',
      flexDirection: 'column',
      gap: 10
    }}>
      {alarms.map(alarm => {
        const isStopLoss = alarm.alarm_status === 'STOP_LOSS_BREACH'
        const borderColor = isStopLoss ? '#dc2626' : '#10b981'
        const bgColor = isStopLoss ? 'rgba(220, 38, 38, 0.15)' : 'rgba(16, 185, 129, 0.15)'

        return (
          <div
            key={alarm.id}
            style={{
              background: bgColor,
              border: `2px solid ${borderColor}`,
              borderRadius: 10,
              padding: '14px 18px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: 12,
              animation: 'pulse 2s infinite'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: 24 }}>{isStopLoss ? '🚨' : '🎯'}</span>
              <div>
                <div style={{ fontSize: 14, fontWeight: 700, color: isStopLoss ? '#fca5a5' : '#86efac' }}>
                  {alarm.alarm_message}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>
                  Holding: {alarm.shares} shares of {alarm.stock_symbol} (Bought @ ₹{alarm.buy_price?.toLocaleString('en-IN', { maximumFractionDigits: 2 })} | Current Live: ₹{alarm.current_price?.toLocaleString('en-IN', { maximumFractionDigits: 2 })})
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 8 }}>
              <button
                onClick={() => onSelectStock(alarm.stock_symbol)}
                className="btn"
                style={{ fontSize: 12, padding: '6px 12px' }}
              >
                View Charts
              </button>
              <button
                onClick={() => onOpenTradeModal(alarm.stock_symbol, alarm.current_price, 'SELL')}
                className="btn"
                style={{
                  fontSize: 12,
                  padding: '6px 16px',
                  fontWeight: 700,
                  background: isStopLoss ? '#dc2626' : 'var(--green)',
                  color: '#ffffff'
                }}
              >
                {isStopLoss ? '🚨 SELL NOW (EXIT LOSS)' : '💰 BOOK PROFIT NOW'}
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
