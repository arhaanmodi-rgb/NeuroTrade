import React from 'react'

export default function Sidebar({
  activeTab,
  onNavigate,
  isOpen,
  setIsOpen,
  alarmsCount = 0,
  currentUser,
  onOpenSearch,
  onOpenAddModal
}) {
  return (
    <aside style={{
      width: isOpen ? 250 : 70,
      background: 'var(--sidebar-bg)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      transition: 'width 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
      zIndex: 110,
      height: '100vh',
      position: 'fixed',
      top: 0,
      left: 0,
      bottom: 0,
      overflowY: 'auto'
    }}>
      {/* Brand Header */}
      <div style={{
        height: 68,
        padding: '0 20px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        borderBottom: '1px solid var(--border)',
        cursor: 'pointer',
        flexShrink: 0
      }}
      onClick={() => onNavigate('dashboard')}
      >
        <div style={{
          width: 36,
          height: 36,
          borderRadius: 10,
          background: 'linear-gradient(135deg, #2563eb, #38bdf8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          fontWeight: 800,
          fontSize: 18,
          boxShadow: '0 4px 12px rgba(37, 99, 235, 0.35)',
          flexShrink: 0
        }}>
          ⚡
        </div>
        {isOpen && (
          <div style={{ overflow: 'hidden', whiteSpace: 'nowrap' }}>
            <div style={{ fontSize: 17, fontWeight: 800, letterSpacing: -0.2, color: 'var(--text-primary)' }}>
              Neuro<span style={{ color: 'var(--blue)' }}>Trade</span>
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 600 }}>
              AI TRADING & RISK PRO
            </div>
          </div>
        )}
      </div>

      {/* Navigation List */}
      <div style={{ flex: 1, padding: '16px 12px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
        {isOpen && (
          <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', letterSpacing: 1, padding: '6px 10px', textTransform: 'uppercase' }}>
            Menu
          </div>
        )}

        {/* Dashboard / Portfolio */}
        <NavItem
          icon="📊"
          label="Dashboard"
          active={activeTab === 'dashboard'}
          onClick={() => onNavigate('dashboard')}
          isOpen={isOpen}
          badge="PRO"
        />

        {/* My Purchased Stocks / Holdings */}
        <NavItem
          icon="💼"
          label="My Holdings"
          active={activeTab === 'holdings'}
          onClick={() => onNavigate('holdings')}
          isOpen={isOpen}
          badge="LIVE"
          badgeColor="emerald"
        />

        {/* Technical Chart Studio */}
        <NavItem
          icon="📈"
          label="Technical Charts"
          active={activeTab === 'charts'}
          onClick={() => onNavigate('charts')}
          isOpen={isOpen}
        />

        {/* Risk & Stop-Loss Alarms */}
        <NavItem
          icon="🚨"
          label="Risk & Stop-Loss"
          active={activeTab === 'alarms'}
          onClick={() => onNavigate('alarms')}
          isOpen={isOpen}
          badge={alarmsCount > 0 ? `${alarmsCount}` : null}
          badgeColor="rose"
        />

        {/* AI Neural Signals */}
        <NavItem
          icon="🧠"
          label="AI Deep Signals"
          active={activeTab === 'signals'}
          onClick={() => onNavigate('signals')}
          isOpen={isOpen}
          badge="DQN"
          badgeColor="indigo"
        />

        {/* Trade Ledger / History */}
        <NavItem
          icon="📜"
          label="Trade Ledger"
          active={activeTab === 'trades'}
          onClick={() => onNavigate('trades')}
          isOpen={isOpen}
        />

        {/* Divider */}
        <div style={{ height: 1, background: 'var(--border)', margin: '10px 4px' }} />

        {isOpen && (
          <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', letterSpacing: 1, padding: '6px 10px', textTransform: 'uppercase' }}>
            Quick Actions
          </div>
        )}

        {/* Search 93 Universe */}
        <button
          onClick={onOpenSearch}
          className="btn"
          style={{
            justifyContent: isOpen ? 'flex-start' : 'center',
            padding: '9px 12px',
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            borderRadius: 10,
            fontSize: 12
          }}
          title="Search 93 Verified Stocks"
        >
          <span style={{ fontSize: 14 }}>🔍</span>
          {isOpen && <span>Search 88 Verified AI Stocks</span>}
        </button>

        {/* Add Purchased Stock */}
        <button
          onClick={onOpenAddModal}
          className="btn btn-primary"
          style={{
            justifyContent: isOpen ? 'flex-start' : 'center',
            padding: '9px 12px',
            borderRadius: 10,
            fontSize: 12,
            marginTop: 4
          }}
          title="Record New Stock"
        >
          <span>➕</span>
          {isOpen && <span>Record Trade Entry</span>}
        </button>
      </div>

      {/* User Footer Profile */}
      <div style={{
        padding: '14px 12px',
        borderTop: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        background: 'var(--sidebar-bg)',
        flexShrink: 0
      }}>
        <div style={{
          width: 34,
          height: 34,
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #1e3a8a, #3b82f6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          fontWeight: 700,
          fontSize: 13,
          flexShrink: 0
        }}>
          {currentUser ? currentUser.username[0].toUpperCase() : 'U'}
        </div>
        {isOpen && (
          <div style={{ overflow: 'hidden', whiteSpace: 'nowrap' }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>
              {currentUser ? currentUser.username : 'Guest Trader'}
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
              {currentUser ? 'SEBI Pro Account' : 'Demo Account'}
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}

function NavItem({ icon, label, active, onClick, isOpen, badge, badgeColor = 'blue' }) {
  const badgeStyles = {
    blue: { bg: 'rgba(59, 130, 246, 0.15)', color: '#3b82f6' },
    emerald: { bg: 'rgba(16, 185, 129, 0.15)', color: '#10b981' },
    rose: { bg: 'rgba(244, 63, 94, 0.15)', color: '#f43f5e' },
    indigo: { bg: 'rgba(99, 102, 241, 0.15)', color: '#6366f1' }
  }[badgeColor]

  return (
    <button
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: isOpen ? 'space-between' : 'center',
        padding: '10px 12px',
        borderRadius: 10,
        border: 'none',
        background: active ? 'var(--nav-active-bg)' : 'transparent',
        color: active ? 'var(--nav-active-color)' : 'var(--text-secondary)',
        fontWeight: active ? 700 : 500,
        fontSize: 13,
        cursor: 'pointer',
        transition: 'all 0.15s ease',
        width: '100%',
        textAlign: 'left'
      }}
      onMouseEnter={(e) => {
        if (!active) e.currentTarget.style.background = 'var(--bg-card-hover)'
      }}
      onMouseLeave={(e) => {
        if (!active) e.currentTarget.style.background = 'transparent'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 16 }}>{icon}</span>
        {isOpen && <span>{label}</span>}
      </div>

      {isOpen && badge && (
        <span style={{
          fontSize: 9,
          fontWeight: 800,
          padding: '2px 7px',
          borderRadius: 12,
          background: badgeStyles.bg,
          color: badgeStyles.color,
          letterSpacing: 0.4
        }}>
          {badge}
        </span>
      )}
    </button>
  )
}
