import React, { useState, useEffect, useCallback, useRef } from 'react'
import './index.css'
import Sidebar           from './components/Sidebar.jsx'
import TopNavbar         from './components/TopNavbar.jsx'
import TopStockCards     from './components/TopStockCards.jsx'
import SideWidgets       from './components/SideWidgets.jsx'
import SignalPanel       from './components/SignalPanel.jsx'
import MetricsCard       from './components/MetricsCard.jsx'
import StockHistoryChart from './components/StockHistoryChart.jsx'
import TradeHistory      from './components/TradeHistory.jsx'
import AllStocksGrid     from './components/AllStocksGrid.jsx'
import AuthModal         from './components/AuthModal.jsx'
import StockSearchModal  from './components/StockSearchModal.jsx'
import AIFeedbackCard    from './components/AIFeedbackCard.jsx'
import UserHoldingsTable from './components/UserHoldingsTable.jsx'
import AddHoldingModal   from './components/AddHoldingModal.jsx'
import RecordTradeModal  from './components/RecordTradeModal.jsx'
import StopLossAlertBanner from './components/StopLossAlertBanner.jsx'
import {
  fetchSignal, fetchAllSignals, fetchTrades, fetchHealth, fetchPortfolio,
  fetchMe, fetchHoldings
} from './services/api.js'

const DEFAULT_STOCKS = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'TATAMOTORS', 'SBIN', 'SUZLON', 'ZOMATO']
const HIGH_SPEED_TICK_INTERVAL_MS = 3000

export default function App() {
  const [stocks, setStocks]             = useState(DEFAULT_STOCKS)
  const [selectedStock, setSelected]    = useState('RELIANCE')
  const [signal, setSignal]             = useState(null)
  const [allSignals, setAllSignals]     = useState(null)
  const [trades, setTrades]             = useState([])
  const [portfolio, setPortfolio]       = useState(null)
  const [holdingsData, setHoldingsData] = useState(null)
  const [loading, setLoading]           = useState(true)
  const [loadingAll, setLoadingAll]     = useState(true)
  const [refreshing, setRefreshing]     = useState(false)
  const [autoRefresh, setAutoRefresh]   = useState(true)
  const [apiStatus, setApiStatus]       = useState('connecting')
  const [dataMode, setDataMode]         = useState('DEMO')
  const [lastUpdate, setLastUpdate]     = useState(null)
  const [error, setError]               = useState(null)

  // Layout & Theme states
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [theme, setTheme]                 = useState('dark') // 'dark' or 'light'
  const [activeTab, setActiveTab]         = useState('dashboard')

  // Auth & Modal states
  const [currentUser, setCurrentUser]   = useState(null)
  const [isAuthOpen, setIsAuthOpen]     = useState(false)
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const [isAddHoldingOpen, setIsAddHoldingOpen] = useState(false)
  const [tradeModal, setTradeModal]     = useState({ isOpen: false, stock: '', currentPrice: 0, action: 'BUY' })

  const autoRef = useRef(null)

  // ── Sync data-theme attribute on document root ────────────
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  // ── Navigation Redirection Handler ────────────────────────
  const handleNavigate = (tabId) => {
    setActiveTab(tabId)
    const targetMap = {
      dashboard: 'top-overview',
      holdings: 'holdings-section',
      charts: 'charts-section',
      alarms: 'alarms-section',
      signals: 'signals-section',
      trades: 'trades-section'
    }
    const elementId = targetMap[tabId]
    if (elementId) {
      const el = document.getElementById(elementId)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
  }

  // ── Keyboard shortcut: Ctrl+K / Cmd+K to open stock search ──
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setIsSearchOpen(true)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // ── Load individual stock signal ──────────────────────────
  const loadSignal = useCallback(async (stock, silent = false) => {
    if (!silent) setRefreshing(true)
    try {
      const [sig, tradesData] = await Promise.all([
        fetchSignal(stock),
        fetchTrades(100)
      ])
      setSignal(sig)
      setTrades(tradesData.trades || [])
      setApiStatus('online')
      setLastUpdate(new Date())
      if (sig.data_mode) setDataMode(sig.data_mode)
    } catch (err) {
      if (!silent) setError(err.message)
      setApiStatus('offline')
    } finally {
      if (!silent) {
        setLoading(false)
        setRefreshing(false)
      }
    }
  }, [])

  // ── Load all stocks overview ──────────────────────────────
  const loadAllSignals = useCallback(async () => {
    try {
      const data = await fetchAllSignals()
      setAllSignals(data)
    } catch {
      // non-critical
    } finally {
      setLoadingAll(false)
    }
  }, [])

  // ── Load portfolio & holdings ─────────────────────────────
  const loadPortfolioAndHoldings = useCallback(async () => {
    try {
      const [portData, hData, tradesData] = await Promise.all([
        fetchPortfolio(),
        fetchHoldings().catch(() => null),
        fetchTrades(100).catch(() => ({ trades: [] }))
      ])
      setPortfolio(portData)
      if (hData) setHoldingsData(hData)
      if (tradesData?.trades) setTrades(tradesData.trades)
    } catch {
      // non-critical
    }
  }, [])

  // ── Check user session ────────────────────────────────────
  useEffect(() => {
    const savedUser = localStorage.getItem('neurotrade_user')
    if (savedUser) {
      try {
        setCurrentUser(JSON.parse(savedUser))
      } catch (e) {
        localStorage.removeItem('neurotrade_user')
      }
    }
    
    fetchMe()
      .then(user => {
        setCurrentUser(user)
        localStorage.setItem('neurotrade_user', JSON.stringify(user))
        loadPortfolioAndHoldings()
      })
      .catch(() => {
        if (!savedUser) setCurrentUser(null)
      })
  }, [])

  // ── Initial bootstrap ─────────────────────────────────────
  useEffect(() => {
    fetchHealth()
      .then(h => {
        setApiStatus('online')
        if (h.data_mode) setDataMode(h.data_mode)
        if (h.models_loaded?.length > 0) {
          setStocks(prev => Array.from(new Set([...prev, ...h.models_loaded])))
        }
      })
      .catch(() => setApiStatus('offline'))

    loadSignal(selectedStock)
    loadAllSignals()
    loadPortfolioAndHoldings()
  }, [])

  // ── Reload when stock changes ─────────────────────────────
  useEffect(() => {
    setLoading(true)
    loadSignal(selectedStock)
  }, [selectedStock])

  // ── High-Speed Auto-Tick Refresh (Every 3 seconds) ───────────
  useEffect(() => {
    if (autoRef.current) clearInterval(autoRef.current)
    if (autoRefresh) {
      autoRef.current = setInterval(() => {
        loadSignal(selectedStock, true)
        loadPortfolioAndHoldings()
      }, HIGH_SPEED_TICK_INTERVAL_MS)
    }
    return () => { if (autoRef.current) clearInterval(autoRef.current) }
  }, [autoRefresh, selectedStock, loadSignal, loadPortfolioAndHoldings])

  const handleManualRefresh = () => {
    loadSignal(selectedStock)
    loadAllSignals()
    loadPortfolioAndHoldings()
  }

  const handleLogout = () => {
    localStorage.removeItem('neurotrade_token')
    localStorage.removeItem('neurotrade_user')
    setCurrentUser(null)
    setHoldingsData(null)
  }

  const handleSelectFromSearch = (symbol) => {
    if (!stocks.includes(symbol)) {
      setStocks(prev => [symbol, ...prev])
    }
    setSelected(symbol)
  }

  const handleOpenTradeModal = (stk, curPrice, act = 'BUY') => {
    if (!currentUser) {
      setIsAuthOpen(true)
      return
    }
    setTradeModal({
      isOpen: true,
      stock: stk || selectedStock,
      currentPrice: curPrice || signal?.price || 100,
      action: act
    })
  }

  const activeAlarms = holdingsData?.holdings?.filter(h => h.alarm_status !== 'NORMAL') || []

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-deep)' }}>

      {/* ══════════════ 1. FIXED LEFT SIDEBAR (100% Stationary) ══════════════ */}
      <Sidebar
        activeTab={activeTab}
        onNavigate={handleNavigate}
        isOpen={isSidebarOpen}
        setIsOpen={setIsSidebarOpen}
        alarmsCount={activeAlarms.length}
        currentUser={currentUser}
        onOpenSearch={() => setIsSearchOpen(true)}
        onOpenAddModal={() => {
          if (!currentUser) setIsAuthOpen(true)
          else setIsAddHoldingOpen(true)
        }}
      />

      {/* ══════════════ 2. RIGHT SCROLLABLE CONTENT (Independent) ══════════════ */}
      <div style={{
        marginLeft: isSidebarOpen ? 250 : 70,
        transition: 'margin-left 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        minWidth: 0
      }}>

        {/* Top Header Navbar */}
        <TopNavbar
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
          onOpenSearch={() => setIsSearchOpen(true)}
          alarmsCount={activeAlarms.length}
          alarms={activeAlarms}
          trades={trades}
          onSelectStock={handleSelectFromSearch}
          onOpenTradeModal={handleOpenTradeModal}
          currentUser={currentUser}
          onOpenAuth={() => setIsAuthOpen(true)}
          onLogout={handleLogout}
          theme={theme}
          setTheme={setTheme}
          signal={signal}
          refreshing={refreshing}
          onRefresh={handleManualRefresh}
          autoRefresh={autoRefresh}
          onToggleAuto={() => setAutoRefresh(a => !a)}
        />

        {/* Main Dashboard Canvas */}
        <main style={{ padding: '24px 28px', flex: 1 }}>

          {/* Active Stop Loss / Target Alarms Banner */}
          <div id="alarms-section" style={{ scrollMarginTop: 80 }}>
            <StopLossAlertBanner
              alarms={activeAlarms}
              onSelectStock={handleSelectFromSearch}
              onOpenTradeModal={handleOpenTradeModal}
            />
          </div>

          {/* ── TOP 4-CARD STOCK TICKER ROW ── */}
          <div id="top-overview" style={{ scrollMarginTop: 80 }}>
            <TopStockCards
              onSelectStock={handleSelectFromSearch}
              selectedStock={selectedStock}
              allSignals={allSignals}
            />
          </div>

          {/* ── TWO-COLUMN TAILADMIN COMMAND GRID ── */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(0, 2fr) minmax(320px, 1fr)',
            gap: 24,
            marginBottom: 24,
            alignItems: 'start'
          }}>

            {/* ── LEFT MAIN COLUMN ── */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24, minWidth: 0 }}>
              
              {/* Portfolio Performance & Multi-Year Historical Chart Studio */}
              <div id="charts-section" style={{ scrollMarginTop: 80 }}>
                <StockHistoryChart
                  stock={selectedStock}
                  onSelectStock={handleSelectFromSearch}
                />
              </div>

              {/* My Purchased Stocks & Real-Time AI Advisor (Holdings Table) */}
              <div id="holdings-section" style={{ scrollMarginTop: 80 }}>
                <UserHoldingsTable
                  holdingsData={holdingsData}
                  loading={loading}
                  onSelectStock={handleSelectFromSearch}
                  onOpenAddModal={() => {
                    if (!currentUser) setIsAuthOpen(true)
                    else setIsAddHoldingOpen(true)
                  }}
                  onOpenTradeModal={handleOpenTradeModal}
                  onRefresh={loadPortfolioAndHoldings}
                />
              </div>

              {/* Trending Indian Stocks Overview */}
              <AllStocksGrid
                allSignals={allSignals}
                loading={loadingAll}
                onSelectStock={(s) => { setSelected(s); setLoading(true) }}
                selectedStock={selectedStock}
              />
            </div>

            {/* ── RIGHT SIDEBAR COLUMN ── */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              
              {/* Side Widgets (Capital Distribution + Watchlist) */}
              <SideWidgets
                holdingsData={holdingsData}
                onSelectStock={handleSelectFromSearch}
                selectedStock={selectedStock}
                onOpenAddModal={() => {
                  if (!currentUser) setIsAuthOpen(true)
                  else setIsAddHoldingOpen(true)
                }}
              />

              {/* AI Neural Decision & Signal Panel */}
              <div id="signals-section" style={{ scrollMarginTop: 80 }}>
                <SignalPanel
                  signal={signal}
                  loading={loading}
                  onOpenTradeModal={handleOpenTradeModal}
                />
              </div>

              {/* Position & Blocked Capital Metrics */}
              <MetricsCard signal={signal} />
            </div>
          </div>

          {/* ── FULL-WIDTH BOTTOM SECTIONS ── */}
          {signal?.ai_feedback && (
            <div style={{ marginBottom: 24 }}>
              <AIFeedbackCard
                feedback={signal.ai_feedback}
                stock={signal.stock}
                price={signal.price}
              />
            </div>
          )}

          {/* Immutable Trade Audit History */}
          <div id="trades-section" style={{ scrollMarginTop: 80 }}>
            <TradeHistory trades={trades} />
          </div>

          {/* Footer */}
          <footer style={{
            textAlign: 'center',
            padding: '32px 0 16px',
            color: 'var(--text-muted)',
            fontSize: 11.5,
            borderTop: '1px solid var(--border)',
            marginTop: 32
          }}>
            NeuroTrade v2.0 Enterprise &nbsp;·&nbsp; TailAdmin Pro Design System &nbsp;·&nbsp;
            <span style={{ color: 'var(--rose)' }}>⚠ Simulation & Educational Risk Platform — Not Financial Advice</span>
          </footer>
        </main>
      </div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={(user) => {
          setCurrentUser(user)
          loadPortfolioAndHoldings()
        }}
      />

      {/* 7000 Stock Universe Search Modal */}
      <StockSearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onSelectStock={handleSelectFromSearch}
      />

      {/* Add Purchased Stock Holding Modal */}
      <AddHoldingModal
        isOpen={isAddHoldingOpen}
        onClose={() => setIsAddHoldingOpen(false)}
        onHoldingAdded={() => {
          handleManualRefresh()
          loadPortfolioAndHoldings()
        }}
      />

      {/* Record Order & Set Stop Loss Modal */}
      <RecordTradeModal
        isOpen={tradeModal.isOpen}
        onClose={() => setTradeModal({ ...tradeModal, isOpen: false })}
        stock={tradeModal.stock}
        currentPrice={tradeModal.currentPrice}
        initialAction={tradeModal.action}
        onTradeSuccess={() => {
          handleManualRefresh()
          loadPortfolioAndHoldings()
        }}
      />
    </div>
  )
}
