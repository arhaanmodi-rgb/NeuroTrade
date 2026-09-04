import React, { useState, useEffect, useRef } from 'react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar
} from 'recharts'
import { fetchStockHistory, searchStocks } from '../services/api.js'

const formatINR = (val, maxDec = 2) => {
  const n = Number(val)
  return isNaN(n) ? '0' : n.toLocaleString('en-IN', { maximumFractionDigits: maxDec })
}

const TIMEFRAMES = [
  { key: '1w', label: '1W' },
  { key: '1m', label: '1M' },
  { key: '6m', label: '6M' },
  { key: '1y', label: '1Y' },
  { key: '2y', label: '2Y' },
  { key: '3y', label: '3Y' },
  { key: '5y', label: '5Y' }
]

const POPULAR_PILLS = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'TATAMOTORS', 'SBIN', 'SUZLON', 'ZOMATO']

function CustomTooltip({ active, payload }) {
  if (!active || !payload || payload.length === 0) return null
  const data = payload[0].payload
  return (
    <div style={{
      background: 'rgba(15, 23, 42, 0.95)',
      border: '1px solid #334155',
      borderRadius: 8,
      padding: '10px 14px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
      fontSize: 12
    }}>
      <div style={{ color: '#94a3b8', marginBottom: 4, fontWeight: 600 }}>{data.time}</div>
      <div style={{ color: '#f8fafc', fontSize: 14, fontWeight: 700, marginBottom: 4 }}>
        Close: ₹{formatINR(data.close, 2)}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px 12px', fontSize: 11, color: '#cbd5e1' }}>
        <div>Open: ₹{formatINR(data.open, 2)}</div>
        <div>High: ₹{formatINR(data.high, 2)}</div>
        <div>Low: ₹{formatINR(data.low, 2)}</div>
        <div>Vol: {formatINR(data.volume, 0)}</div>
      </div>
      {data.sma20 && (
        <div style={{ marginTop: 4, paddingTop: 4, borderTop: '1px solid #334155', display: 'flex', gap: 12, fontSize: 10 }}>
          <span style={{ color: '#3b82f6' }}>SMA 20: ₹{formatINR(data.sma20, 2)}</span>
          <span style={{ color: '#f59e0b' }}>SMA 50: ₹{formatINR(data.sma50, 2)}</span>
        </div>
      )}
    </div>
  )
}

export default function StockHistoryChart({ stock, onSelectStock }) {
  const [period, setPeriod] = useState('1y')
  const [chartData, setChartData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  const searchRef = useRef(null)

  useEffect(() => {
    let isMounted = true
    setLoading(true)
    setError(null)

    fetchStockHistory(stock, period)
      .then(res => {
        if (isMounted) {
          setChartData(res)
          setLoading(false)
          setError(null)
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err?.response?.data?.detail || err.message || 'Failed to load stock history')
          setLoading(false)
        }
      })

    return () => { isMounted = false }
  }, [stock, period])

  // Instant fuzzy search across 7,000+ stocks
  const handleSearchInput = async (e) => {
    const q = e.target.value.toUpperCase()
    setSearchQuery(q)
    if (q.length >= 2) {
      setIsSearching(true)
      try {
        const res = await searchStocks(q, 'ALL', 6)
        setSearchResults(res.stocks || [])
      } catch {
        setSearchResults([])
      }
    } else {
      setSearchResults([])
      setIsSearching(false)
    }
  }

  const handlePickStock = (sym) => {
    setSearchQuery('')
    setSearchResults([])
    setIsSearching(false)
    if (onSelectStock) onSelectStock(sym)
  }

  const candles = chartData?.candles || []
  const isPositive = (Number(chartData?.period_change_inr) || 0) >= 0
  const color = isPositive ? '#10b981' : '#ef4444'

  const minPrice = candles.length ? Math.min(...candles.map(c => c.low || c.close)) * 0.98 : 'auto'
  const maxPrice = candles.length ? Math.max(...candles.map(c => c.high || c.close)) * 1.02 : 'auto'

  return (
    <div className="card" style={{ marginBottom: 20 }}>
      {/* Header with Stock Search, Title & Timeframe Selector */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 12,
        marginBottom: 14
      }}>
        {/* Left: Title & Live Metrics */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 22 }}>📈</span>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
              Historical Candlestick & Technical Studio — <span style={{ color: '#93c5fd' }}>{stock}</span>
            </h3>
          </div>
          {chartData && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 4, fontSize: 12, flexWrap: 'wrap' }}>
              <span style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: 16 }}>
                ₹{formatINR(chartData.current_price, 2)}
              </span>
              <span style={{ fontWeight: 700, color }}>
                {isPositive ? '+' : ''}₹{formatINR(chartData.period_change_inr, 2)} ({isPositive ? '+' : ''}{(Number(chartData.period_change_pct) || 0).toFixed(2)}%)
              </span>
              <span style={{ color: 'var(--text-muted)', fontSize: 11 }}>
                Period High: ₹{formatINR(chartData.high_period, 2)} · Low: ₹{formatINR(chartData.low_period, 2)}
              </span>
            </div>
          )}
        </div>

        {/* Right: Inline Search across 7000+ stocks & Timeframe buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          {/* Direct Stock Search Input */}
          <div style={{ position: 'relative' }} ref={searchRef}>
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchInput}
              placeholder="🔍 Search 93 Verified Stocks (e.g. INFY, TATAMOTORS)"
              style={{
                width: 240,
                padding: '6px 12px',
                borderRadius: 8,
                border: '1px solid var(--border)',
                background: 'var(--bg-base)',
                color: 'var(--text-primary)',
                fontSize: 11,
                textTransform: 'uppercase'
              }}
            />

            {/* Dropdown search results */}
            {isSearching && searchResults.length > 0 && (
              <div style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border-light)',
                borderRadius: 8,
                marginTop: 4,
                zIndex: 100,
                boxShadow: '0 8px 30px rgba(0,0,0,0.85)',
                maxHeight: 220,
                overflowY: 'auto'
              }}>
                {searchResults.map(s => (
                  <div
                    key={s.symbol}
                    onClick={() => handlePickStock(s.symbol)}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      borderBottom: '1px solid var(--border)',
                      fontSize: 11,
                      display: 'flex',
                      justifyContent: 'space-between'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-hover)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <div>
                      <span style={{ fontWeight: 700, color: '#93c5fd' }}>{s.symbol}</span>
                      <span style={{ color: 'var(--text-secondary)', marginLeft: 6 }}>{s.name}</span>
                    </div>
                    <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>{s.exchange}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Timeframe Buttons (1W, 1M, 6M, 1Y, 2Y, 3Y, 5Y) */}
          <div style={{
            display: 'flex',
            background: 'var(--bg-base)',
            borderRadius: 8,
            padding: 3,
            border: '1px solid var(--border)'
          }}>
            {TIMEFRAMES.map(tf => (
              <button
                key={tf.key}
                onClick={() => setPeriod(tf.key)}
                style={{
                  background: period === tf.key ? 'var(--blue)' : 'transparent',
                  color: period === tf.key ? '#ffffff' : 'var(--text-secondary)',
                  border: 'none',
                  borderRadius: 6,
                  padding: '5px 10px',
                  fontSize: 11,
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                {tf.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Quick-switch Ticker Pills */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        marginBottom: 12,
        overflowX: 'auto',
        paddingBottom: 4
      }}>
        <span style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginRight: 4 }}>
          Quick Switch:
        </span>
        {POPULAR_PILLS.map(sym => (
          <button
            key={sym}
            onClick={() => handlePickStock(sym)}
            style={{
              background: stock === sym ? 'var(--blue-bg)' : 'var(--bg-base)',
              color: stock === sym ? '#93c5fd' : 'var(--text-secondary)',
              border: `1px solid ${stock === sym ? 'var(--blue)' : 'var(--border)'}`,
              borderRadius: 6,
              padding: '3px 9px',
              fontSize: 10,
              fontWeight: 600,
              cursor: 'pointer',
              whiteSpace: 'nowrap'
            }}
          >
            {sym}
          </button>
        ))}
      </div>

      {/* Main Chart Canvas */}
      <div style={{ height: 280, width: '100%' }}>
        {error ? (
          <div style={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 24,
            textAlign: 'center',
            background: error.toLowerCase().includes('not listed') || error.toLowerCase().includes('invalid') || error.toLowerCase().includes('not found')
              ? 'rgba(244, 63, 94, 0.06)'
              : 'rgba(59, 130, 246, 0.06)',
            borderRadius: 12,
            border: error.toLowerCase().includes('not listed') || error.toLowerCase().includes('invalid') || error.toLowerCase().includes('not found')
              ? '1px solid rgba(244, 63, 94, 0.2)'
              : '1px solid rgba(59, 130, 246, 0.2)'
          }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>
              {error.toLowerCase().includes('not listed') || error.toLowerCase().includes('invalid') || error.toLowerCase().includes('not found') ? '🚨' : '⚡'}
            </div>
            <div style={{
              fontSize: 14,
              fontWeight: 700,
              color: error.toLowerCase().includes('not listed') || error.toLowerCase().includes('invalid') || error.toLowerCase().includes('not found') ? '#f43f5e' : '#60a5fa',
              marginBottom: 4
            }}>
              {error.toLowerCase().includes('not listed') || error.toLowerCase().includes('invalid') || error.toLowerCase().includes('not found')
                ? `Unlisted / Invalid Stock Symbol: "${stock}"`
                : 'Cloud AI Backend Initializing...'}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', maxWidth: 460, marginBottom: 10 }}>
              {error.toLowerCase().includes('not listed') || error.toLowerCase().includes('invalid') || error.toLowerCase().includes('not found')
                ? 'This stock is not listed on the National Stock Exchange (NSE) or Bombay Stock Exchange (BSE). Please choose a valid listed company (e.g., RELIANCE, TATAMOTORS, INFY, TCS, HDFCBANK).'
                : (error || 'Connecting to Render AI server. Free tier cloud instances may take ~30s on first load.')}
            </div>
            <button
              onClick={() => {
                setLoading(true)
                setError(null)
                fetchStockHistory(stock, period)
                  .then(res => { setChartData(res); setLoading(false); })
                  .catch(err => { setError(err?.response?.data?.detail || err.message || 'Error'); setLoading(false); })
              }}
              style={{
                background: 'var(--blue)',
                color: '#fff',
                border: 'none',
                borderRadius: 6,
                padding: '6px 14px',
                fontSize: 11,
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              🔄 Retry Connection
            </button>
          </div>
        ) : loading ? (
          <div style={{
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-muted)',
            fontSize: 13
          }}>
            Loading {stock} {period.toUpperCase()} multi-year charts...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={candles} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={color} stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis
                dataKey="time"
                stroke="#64748b"
                tick={{ fontSize: 10 }}
                tickLine={false}
                minTickGap={40}
              />
              <YAxis
                domain={[minPrice, maxPrice]}
                stroke="#64748b"
                tick={{ fontSize: 10 }}
                tickLine={false}
                tickFormatter={(v) => `₹${Math.round(v)}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="close"
                name="Price"
                stroke={color}
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#priceGrad)"
              />
              <Line
                type="monotone"
                dataKey="sma20"
                name="SMA 20"
                stroke="#3b82f6"
                strokeWidth={1.2}
                dot={false}
                strokeDasharray="4 4"
              />
              <Line
                type="monotone"
                dataKey="sma50"
                name="SMA 50"
                stroke="#f59e0b"
                strokeWidth={1.2}
                dot={false}
                strokeDasharray="2 2"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Volume Sub-Chart */}
      {!loading && candles.length > 0 && (
        <div style={{ height: 60, width: '100%', marginTop: 8 }}>
          <div className="label" style={{ fontSize: 9, marginBottom: 2 }}>Volume Activity</div>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={candles} margin={{ top: 0, right: 10, left: -10, bottom: 0 }}>
              <XAxis dataKey="time" hide />
              <YAxis hide />
              <Bar
                dataKey="volume"
                fill="rgba(59, 130, 246, 0.4)"
                radius={[2, 2, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
