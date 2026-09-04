import React, { useState, useEffect } from 'react'
import { executeTrade, addHolding } from '../services/api.js'

export default function RecordTradeModal({ isOpen, onClose, stock, currentPrice, initialAction = 'BUY', onTradeSuccess }) {
  const [action, setAction] = useState(initialAction)
  const [shares, setShares] = useState('10')
  const [price, setPrice] = useState('')
  const [targetPrice, setTargetPrice] = useState('')
  const [stopLoss, setStopLoss] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (isOpen && currentPrice) {
      setPrice(currentPrice.toString())
      setTargetPrice((currentPrice * 1.08).toFixed(2))
      setStopLoss((currentPrice * 0.95).toFixed(2))
      setAction(initialAction)
      setError(null)
    }
  }, [isOpen, currentPrice, initialAction])

  if (!isOpen) return null

  const totalValue = (parseFloat(shares || 0) * parseFloat(price || 0))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const qty = parseFloat(shares)
      const executionPrice = parseFloat(price)
      const target = parseFloat(targetPrice)
      const stop = parseFloat(stopLoss)

      if (isNaN(qty) || qty <= 0) throw new Error('Enter a valid share quantity')
      if (isNaN(executionPrice) || executionPrice <= 0) throw new Error('Enter a valid price')

      if (action === 'BUY') {
        // Record both as holding and in trade audit log
        await addHolding({
          stock_symbol: stock,
          buy_price: executionPrice,
          shares: qty,
          target_price: target,
          stop_loss: stop,
          exchange: 'NSE'
        })
      } else {
        // Execute Sell
        await executeTrade(stock, 'SELL', qty)
      }

      if (onTradeSuccess) onTradeSuccess()
      onClose()
    } catch (err) {
      setError(err.message || 'Trade logging failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(5, 7, 13, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: 16
    }}>
      <div className="card" style={{
        width: '100%',
        maxWidth: 480,
        background: 'var(--bg-card)',
        border: '1px solid var(--border-light)',
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.85)',
        position: 'relative'
      }}>
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: 16, right: 16, background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 18, cursor: 'pointer' }}
        >
          ✕
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
          <span style={{ fontSize: 28 }}>{action === 'BUY' ? '⚡' : '💰'}</span>
          <div>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>
              {action === 'BUY' ? `Record Buy Entry — ${stock}` : `Execute Sell Exit — ${stock}`}
            </h2>
            <p style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
              Enter shares, cost price, and set live AI Stop-Loss alarms
            </p>
          </div>
        </div>

        {error && (
          <div style={{ background: 'var(--red-bg)', border: '1px solid #7f1d1d', borderRadius: 8, padding: '10px 14px', marginBottom: 16, color: '#fca5a5', fontSize: 12 }}>
            ⚠️ {error}
          </div>
        )}

        {/* Action Toggle */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
          <button
            type="button"
            onClick={() => setAction('BUY')}
            className={`btn ${action === 'BUY' ? 'btn-active' : ''}`}
            style={{ flex: 1, justifyContent: 'center', fontWeight: 700, color: action === 'BUY' ? 'var(--green)' : 'inherit' }}
          >
            ⚡ BUY ENTRY
          </button>
          <button
            type="button"
            onClick={() => setAction('SELL')}
            className={`btn ${action === 'SELL' ? 'btn-active' : ''}`}
            style={{ flex: 1, justifyContent: 'center', fontWeight: 700, color: action === 'SELL' ? 'var(--red)' : 'inherit' }}
          >
            💰 SELL EXIT
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Shares Quantity & Price */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label className="label" style={{ display: 'block', marginBottom: 6 }}>Quantity (Shares)</label>
              <input
                type="number"
                step="1"
                required
                value={shares}
                onChange={(e) => setShares(e.target.value)}
                placeholder="e.g. 25"
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 8,
                  border: '1px solid var(--border)',
                  background: 'var(--bg-base)',
                  color: 'var(--text-primary)',
                  fontSize: 13
                }}
              />
            </div>

            <div>
              <label className="label" style={{ display: 'block', marginBottom: 6 }}>Execution Price (₹)</label>
              <input
                type="number"
                step="0.01"
                required
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="e.g. 1305.50"
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 8,
                  border: '1px solid var(--border)',
                  background: 'var(--bg-base)',
                  color: 'var(--text-primary)',
                  fontSize: 13
                }}
              />
            </div>
          </div>

          {/* Target Limit & Stop Loss (AI Alarm parameters) */}
          {action === 'BUY' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label className="label" style={{ display: 'block', marginBottom: 6, color: 'var(--green)' }}>
                  🎯 Target Limit (₹)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(e.target.value)}
                  placeholder="Target Price"
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: 8,
                    border: '1px solid #065f46',
                    background: 'var(--bg-base)',
                    color: 'var(--green)',
                    fontSize: 13,
                    fontWeight: 600
                  }}
                />
              </div>

              <div>
                <label className="label" style={{ display: 'block', marginBottom: 6, color: 'var(--red)' }}>
                  🚨 Stop Loss (₹ Alarm)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={stopLoss}
                  onChange={(e) => setStopLoss(e.target.value)}
                  placeholder="Stop Loss"
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: 8,
                    border: '1px solid #7f1d1d',
                    background: 'var(--bg-base)',
                    color: 'var(--red)',
                    fontSize: 13,
                    fontWeight: 600
                  }}
                />
              </div>
            </div>
          )}

          {/* Order Summary Strip */}
          <div style={{ background: 'var(--bg-surface)', borderRadius: 8, padding: '12px 14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Total Order Value ({shares || 0} shares @ ₹{price || 0}):
            </span>
            <span style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
              ₹{totalValue.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
            </span>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{
              width: '100%',
              padding: '12px',
              fontSize: 14,
              fontWeight: 700,
              justifyContent: 'center',
              background: action === 'BUY' ? 'var(--blue)' : '#dc2626'
            }}
          >
            {loading ? 'Recording...' : `✓ Record ${action} Order for ${stock}`}
          </button>
        </form>
      </div>
    </div>
  )
}
