import React, { useState } from 'react'
import { addHolding, searchStocks } from '../services/api.js'

export default function AddHoldingModal({ isOpen, onClose, onHoldingAdded }) {
  const [formData, setFormData] = useState({
    stock_symbol: '',
    buy_price: '',
    shares: '',
    buy_date: new Date().toISOString().split('T')[0],
    exchange: 'NSE'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searchResults, setSearchResults] = useState([])

  if (!isOpen) return null

  const handleSymbolChange = async (e) => {
    const sym = e.target.value.toUpperCase()
    setFormData({ ...formData, stock_symbol: sym })
    if (sym.length >= 2) {
      try {
        const res = await searchStocks(sym, 'ALL', 5)
        setSearchResults(res.stocks || [])
      } catch (err) {
        // ignore
      }
    } else {
      setSearchResults([])
    }
  }

  const handleSelectSymbol = (stock) => {
    setFormData({
      ...formData,
      stock_symbol: stock.symbol,
      exchange: stock.exchange.includes('BSE') ? 'BSE' : 'NSE'
    })
    setSearchResults([])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const price = parseFloat(formData.buy_price)
      const qty = parseFloat(formData.shares)
      if (isNaN(price) || price <= 0) throw new Error('Enter a valid Buy Price')
      if (isNaN(qty) || qty <= 0) throw new Error('Enter a valid Quantity (shares)')

      await addHolding({
        stock_symbol: formData.stock_symbol.toUpperCase().trim(),
        buy_price: price,
        shares: qty,
        buy_date: formData.buy_date,
        exchange: formData.exchange
      })

      onHoldingAdded()
      onClose()
    } catch (err) {
      setError(err.message || 'Failed to add holding')
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
        maxWidth: 460,
        background: 'var(--bg-card)',
        border: '1px solid var(--border-light)',
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.85)',
        position: 'relative'
      }}>
        {/* Close button */}
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: 16, right: 16, background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 18, cursor: 'pointer' }}
        >
          ✕
        </button>

        {/* Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
          <span style={{ fontSize: 28 }}>📦</span>
          <div>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>Add Purchased Stock Holding</h2>
            <p style={{ fontSize: 11, color: 'var(--text-secondary)' }}>Track live P&L and get tailored AI exit/hold signals</p>
          </div>
        </div>

        {error && (
          <div style={{ background: 'var(--red-bg)', border: '1px solid #7f1d1d', borderRadius: 8, padding: '10px 14px', marginBottom: 16, color: '#fca5a5', fontSize: 12 }}>
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Stock Symbol */}
          <div style={{ position: 'relative' }}>
            <label className="label" style={{ display: 'block', marginBottom: 6 }}>Stock Symbol (NSE / BSE)</label>
            <input
              type="text"
              required
              value={formData.stock_symbol}
              onChange={handleSymbolChange}
              placeholder="e.g. RELIANCE, TATAMOTORS, ZOMATO"
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: 8,
                border: '1px solid var(--border)',
                background: 'var(--bg-base)',
                color: 'var(--text-primary)',
                fontSize: 13,
                textTransform: 'uppercase'
              }}
            />

            {searchResults.length > 0 && (
              <div style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border-light)',
                borderRadius: 8,
                marginTop: 4,
                zIndex: 10,
                maxHeight: 180,
                overflowY: 'auto'
              }}>
                {searchResults.map(s => (
                  <div
                    key={s.symbol}
                    onClick={() => handleSelectSymbol(s)}
                    style={{ padding: '8px 12px', cursor: 'pointer', borderBottom: '1px solid var(--border)', fontSize: 12 }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-hover)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <span style={{ fontWeight: 700, color: '#93c5fd' }}>{s.symbol}</span> - {s.name} ({s.exchange})
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Buy Price & Quantity Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label className="label" style={{ display: 'block', marginBottom: 6 }}>Buy Price (₹ / share)</label>
              <input
                type="number"
                step="0.01"
                required
                value={formData.buy_price}
                onChange={(e) => setFormData({ ...formData, buy_price: e.target.value })}
                placeholder="e.g. 1250.50"
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
              <label className="label" style={{ display: 'block', marginBottom: 6 }}>Quantity (Shares)</label>
              <input
                type="number"
                step="1"
                required
                value={formData.shares}
                onChange={(e) => setFormData({ ...formData, shares: e.target.value })}
                placeholder="e.g. 50"
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

          {/* Purchase Date & Exchange */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label className="label" style={{ display: 'block', marginBottom: 6 }}>Purchase Date</label>
              <input
                type="date"
                value={formData.buy_date}
                onChange={(e) => setFormData({ ...formData, buy_date: e.target.value })}
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
              <label className="label" style={{ display: 'block', marginBottom: 6 }}>Exchange</label>
              <select
                value={formData.exchange}
                onChange={(e) => setFormData({ ...formData, exchange: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 8,
                  border: '1px solid var(--border)',
                  background: 'var(--bg-base)',
                  color: 'var(--text-primary)',
                  fontSize: 13
                }}
              >
                <option value="NSE">NSE (National Stock Exchange)</option>
                <option value="BSE">BSE (Bombay Stock Exchange)</option>
                <option value="SME">NSE/BSE SME</option>
              </select>
            </div>
          </div>

          {/* Total Calculation Preview */}
          {formData.buy_price && formData.shares && (
            <div style={{ background: 'var(--bg-surface)', padding: '10px 14px', borderRadius: 8, fontSize: 12 }}>
              <span style={{ color: 'var(--text-muted)' }}>Total Investment Basis: </span>
              <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                ₹{(parseFloat(formData.buy_price || 0) * parseFloat(formData.shares || 0)).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>
          )}

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
              marginTop: 4
            }}
          >
            {loading ? 'Adding Holding...' : '✓ Add to My Portfolio'}
          </button>
        </form>
      </div>
    </div>
  )
}
