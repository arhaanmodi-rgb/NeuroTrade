import axios from 'axios'

const BASE = '/api'

const api = axios.create({
  baseURL: BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('neurotrade_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail
      || error.message
      || 'Network error'
    return Promise.reject(new Error(message))
  }
)

// Signals & Models
export const fetchSignal     = (stock)         => api.get(`/signal/${stock}`)
export const fetchAllSignals = ()              => api.get('/signals')
export const fetchStocks     = ()              => api.get('/stocks')
export const fetchPortfolio  = ()              => api.get('/portfolio')
export const fetchTrades     = (limit = 50)    => api.get(`/trades?limit=${limit}`)
export const fetchHealth     = ()              => api.get('/health')
export const fetchBacktest   = (stock)         => api.get(`/backtest/${stock}`)

// Historical Chart Data (1W, 1M, 6M, 1Y, 2Y, 3Y, 5Y)
export const fetchStockHistory = (symbol, period = '1y') =>
  api.get(`/stocks/${symbol}/history?period=${period}`)

// User Real Holdings & AI Portfolio Advisor
export const fetchHoldings   = ()              => api.get('/holdings')
export const addHolding      = (data)          => api.post('/holdings', data)
export const removeHolding   = (id)            => api.delete(`/holdings/${id}`)

// Trade Execution (Position validation)
export const executeTrade    = (stock, action, shares = null, price = null, target_price = null, stop_loss = null) =>
  api.post('/trades/execute', { stock, action, shares, price, target_price, stop_loss })

// 7000 Stock Universe Search
export const searchStocks    = (q = '', category = 'ALL', limit = 25) => 
  api.get(`/stocks/search?q=${encodeURIComponent(q)}&category=${encodeURIComponent(category)}&limit=${limit}`)
export const fetchStockDirectory = () => api.get('/stocks/directory')

// Authentication & User Watchlist
export const loginUser       = (data)          => api.post('/auth/login', data)
export const registerUser    = (data)          => api.post('/auth/register', data)
export const fetchMe         = ()              => api.get('/auth/me')
export const fetchWatchlist  = ()              => api.get('/auth/watchlist')
export const addToWatchlist  = (stock_symbol, exchange = 'NSE') => 
  api.post('/auth/watchlist', { stock_symbol, exchange })
export const removeFromWatchlist = (stock_symbol) => 
  api.delete(`/auth/watchlist/${stock_symbol}`)
