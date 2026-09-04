import React, { useState, useEffect } from 'react'

export default function EditLimitModal({ isOpen, onClose, holding, onSave }) {
  const [targetPrice, setTargetPrice] = useState('')
  const [stopLoss, setStopLoss] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (isOpen && holding) {
      setTargetPrice(holding.target_price?.toString() || '')
      setStopLoss(holding.stop_loss?.toString() || '')
      setError(null)
    }
  }, [isOpen, holding])

  if (!isOpen || !holding) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const target = parseFloat(targetPrice)
      const stop = parseFloat(stopLoss)
      if (isNaN(target) || target <= 0) throw new Error('Enter a valid Target Price')
      if (isNaN(stop) || stop <= 0) throw new Error('Enter a valid Stop Loss Price')

      await fetch(`/api/holdings/${holding.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('neurotrade_token')}`
        },
        body: JSON.stringify({ target_price: target, stop_loss: stop })
      })

      onSave()
      onClose()
    } catch (err) {
      setError(err.message || 'Failed to update limits')
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
        maxWidth: 420,
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

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <span style={{ fontSize: 24 }}>⚙️</span>
          <div>
            <h2 style={{ fontSize: 17, fontWeight: 700, color: 'var(--text-primary)' }}>
              Set Target & Stop-Loss — {holding.stock_symbol}
            </h2>
            <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              Bought @ ₹{holding.buy_price?.toLocaleString('en-IN', { maximumFractionDigits: 2 })} | Current Live: ₹{holding.current_price?.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
            </p>
          </div>
        </div>

        {error && (
          <div style={{ background: 'var(--red-bg)', border: '1px solid #7f1d1d', borderRadius: 8, padding: '8px 12px', marginBottom: 14, color: '#fca5a5', fontSize: 12 }}>
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label className="label" style={{ display: 'block', marginBottom: 6, color: 'var(--green)' }}>
              🎯 Target Price (Take Profit Limit ₹)
            </label>
            <input
              type="number"
              step="0.01"
              required
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: 8,
                border: '1px solid #065f46',
                background: 'var(--bg-base)',
                color: 'var(--green)',
                fontSize: 14,
                fontWeight: 700
              }}
            />
          </div>

          <div>
            <label className="label" style={{ display: 'block', marginBottom: 6, color: 'var(--red)' }}>
              🚨 Stop Loss (Risk Exit Level ₹)
            </label>
            <input
              type="number"
              step="0.01"
              required
              value={stopLoss}
              onChange={(e) => setStopLoss(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: 8,
                border: '1px solid #7f1d1d',
                background: 'var(--bg-base)',
                color: 'var(--red)',
                fontSize: 14,
                fontWeight: 700
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', padding: '11px', fontWeight: 700, marginTop: 4, justifyContent: 'center' }}
          >
            {loading ? 'Saving...' : '✓ Save Risk Limits'}
          </button>
        </form>
      </div>
    </div>
  )
}
