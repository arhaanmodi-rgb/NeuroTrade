import React, { useState } from 'react'
import NotificationDropdown from './NotificationDropdown.jsx'

export default function TopNavbar({
  isSidebarOpen,
  setIsSidebarOpen,
  onOpenSearch,
  alarmsCount = 0,
  alarms = [],
  trades = [],
  onSelectStock,
  onOpenTradeModal,
  currentUser,
  onOpenAuth,
  onLogout,
  theme,
  setTheme,
  signal,
  refreshing,
  onRefresh,
  autoRefresh,
  onToggleAuto
}) {
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false)

  return (
    <header style={{
      height: 68,
      background: 'var(--header-bg)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border)',
      padding: '0 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      {/* Left: Sidebar Toggle & Search Input */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, flex: 1, maxWidth: 600 }}>
        {/* Toggle Sidebar Button */}
        <button
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            width: 38,
            height: 38,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            fontSize: 16,
            transition: 'all 0.15s'
          }}
          title="Toggle Navigation Menu"
        >
          ☰
        </button>

        {/* Global Search Bar with Cmd+K */}
        <div
          onClick={onOpenSearch}
          style={{
            flex: 1,
            background: 'var(--search-bg)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: '8px 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer',
            transition: 'all 0.2s',
            boxShadow: '0 1px 3px rgba(0,0,0,0.03)'
          }}
          onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--border-light)'}
          onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border)'}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>🔍</span>
            <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>Search or type command...</span>
          </div>
          <kbd style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 6,
            padding: '2px 7px',
            fontSize: 10,
            color: 'var(--text-muted)',
            fontFamily: 'var(--font-mono)'
          }}>
            ⌘K
          </kbd>
        </div>
      </div>

      {/* Right Controls: Live Ticker + Theme + Notifications + User */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        {/* Live Active Stock Price Pill */}
        {signal && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: '6px 14px'
          }}>
            <span style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: 12 }}>
              {signal.stock}
            </span>
            <span className="mono-num" style={{ fontWeight: 700, color: '#38bdf8', fontSize: 13 }}>
              ₹{(signal.price || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
            </span>
            <button
              onClick={onToggleAuto}
              style={{
                background: autoRefresh ? 'rgba(16, 185, 129, 0.15)' : 'transparent',
                color: autoRefresh ? '#10b981' : 'var(--text-muted)',
                border: 'none',
                borderRadius: 6,
                padding: '2px 6px',
                fontSize: 10,
                fontWeight: 700,
                cursor: 'pointer'
              }}
              title="Toggle Live Ticker Stream"
            >
              {autoRefresh ? '● LIVE 3s' : 'PAUSED'}
            </button>
          </div>
        )}

        {/* Theme Toggle Button */}
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: '50%',
            width: 38,
            height: 38,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            fontSize: 15,
            transition: 'all 0.15s'
          }}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? '🌙' : '☀️'}
        </button>

        {/* Interactive Notification Bell with Dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
            style={{
              background: isNotificationsOpen ? 'var(--bg-card-selected)' : 'var(--bg-card)',
              border: isNotificationsOpen ? '1px solid var(--blue)' : '1px solid var(--border)',
              borderRadius: '50%',
              width: 38,
              height: 38,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-primary)',
              cursor: 'pointer',
              fontSize: 15,
              transition: 'all 0.15s'
            }}
            title={alarmsCount > 0 ? `${alarmsCount} Active Risk Alerts` : 'Notifications & Alarms'}
          >
            🔔
          </button>
          {alarmsCount > 0 && (
            <span style={{
              position: 'absolute',
              top: -2,
              right: -2,
              background: '#f43f5e',
              color: '#ffffff',
              fontSize: 9,
              fontWeight: 800,
              width: 17,
              height: 17,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 10px rgba(244, 63, 94, 0.6)',
              pointerEvents: 'none'
            }}>
              {alarmsCount}
            </span>
          )}

          {/* Render Notification Dropdown */}
          <NotificationDropdown
            isOpen={isNotificationsOpen}
            onClose={() => setIsNotificationsOpen(false)}
            alarms={alarms}
            trades={trades}
            onSelectStock={onSelectStock}
            onOpenTradeModal={onOpenTradeModal}
          />
        </div>

        {/* User Account Chip */}
        {currentUser ? (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 12,
            padding: '4px 12px 4px 6px',
            cursor: 'pointer'
          }}>
            <div style={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #2563eb, #38bdf8)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: 12
            }}>
              {currentUser.username[0].toUpperCase()}
            </div>
            <div>
              <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>
                {currentUser.username}
              </div>
              <button
                onClick={onLogout}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#f43f5e',
                  fontSize: 10,
                  cursor: 'pointer',
                  padding: 0,
                  fontWeight: 600
                }}
              >
                Sign Out
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={onOpenAuth}
            className="btn btn-primary"
            style={{ padding: '8px 16px', borderRadius: 10, fontWeight: 700 }}
          >
            👤 Sign In
          </button>
        )}
      </div>
    </header>
  )
}
