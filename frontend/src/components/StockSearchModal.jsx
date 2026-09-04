import React, { useState, useEffect } from 'react'
import { searchStocks } from '../services/api.js'

const CATEGORIES = ['ALL', 'LARGECAP', 'MIDCAP', 'SMALLCAP', 'SME', 'BSE']

export default function StockSearchModal({ isOpen, onClose, onSelectStock }) {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('ALL')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!isOpen) return
    let active = true
    const delayDebounce = setTimeout(async () => {
      setLoading(true)
      try {
        const res = await searchStocks(query, category, 30)
        if (active) setResults(res.stocks || [])
      } catch (err) {
        console.error(err)
      } finally {
        if (active) setLoading(false)
      }
    }, 200)

    return () => {
      active = false
      clearTimeout(delayDebounce)
    }
  }, [query, category, isOpen])

  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(5, 7, 13, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '40px 16px'
    }}>
      <div className="card" style={{
        width: '100%',
        maxWidth: 640,
        background: 'var(--bg-card)',
        border: '1px solid var(--border-light)',
        boxShadow: '0 12px 48px rgba(0, 0, 0, 0.85)',
        maxHeight: '85vh',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 20 }}>🔍</span>
            <span style={{ fontSize: 16, fontWeight: 700 }}>Search 88 Verified Deep Q-Network Equities</span>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 18, cursor: 'pointer' }}
          >
            ✕
          </button>
        </div>

        {/* Input */}
        <div style={{ position: 'relative', marginBottom: 12 }}>
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type company name or ticker (e.g. TATAMOTORS, ZOMATO, SBIN, KORE)..."
            style={{
              width: '100%',
              padding: '12px 16px',
              borderRadius: 10,
              border: '1px solid var(--blue)',
              background: 'var(--bg-base)',
              color: 'var(--text-primary)',
              fontSize: 14,
              outline: 'none'
            }}
          />
        </div>

        {/* Category filters */}
        <div style={{ display: 'flex', gap: 6, marginBottom: 16, flexWrap: 'wrap' }}>
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`btn ${category === cat ? 'btn-active' : ''}`}
              style={{ fontSize: 11, padding: '4px 10px' }}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Results List */}
        <div style={{ overflowY: 'auto', flex: 1, paddingRight: 4, display: 'flex', flexDirection: 'column', gap: 6 }}>
          {loading && (
            <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)' }}>
              Searching universe...
            </div>
          )}

          {!loading && results.length === 0 && (
            <div style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)' }}>
              No matches found for "{query}". You can still analyze it as a custom NSE ticker.
            </div>
          )}

          {!loading && results.map(stock => (
            <div
              key={stock.symbol}
              onClick={() => {
                onSelectStock(stock.symbol)
                onClose()
              }}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '10px 14px',
                borderRadius: 8,
                background: 'var(--bg-surface)',
                border: '1px solid var(--border)',
                cursor: 'pointer',
                transition: 'all 0.15s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--blue)'
                e.currentTarget.style.background = 'var(--bg-elevated)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border)'
                e.currentTarget.style.background = 'var(--bg-surface)'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontWeight: 700, fontSize: 14, color: '#93c5fd' }}>{stock.symbol}</span>
                  <span className="badge badge-demo" style={{ fontSize: 10, padding: '2px 6px' }}>{stock.exchange}</span>
                  {stock.category === 'SME' && (
                    <span className="badge badge-hold" style={{ fontSize: 10, padding: '2px 6px' }}>SME</span>
                  )}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>{stock.name}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{stock.sector}</span>
                <div style={{ fontSize: 11, color: 'var(--blue)', fontWeight: 600, marginTop: 2 }}>Analyze AI Signal →</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
