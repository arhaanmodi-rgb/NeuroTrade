import React from 'react'

export default function LivePrice({ signal, refreshing, onRefresh, autoRefresh, onToggleAuto }) {
  if (!signal) return null

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
      {/* Price chip */}
      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        padding: '7px 14px',
        display: 'flex',
        alignItems: 'center',
        gap: 8
      }}>
        <div style={{
          width: 7,
          height: 7,
          borderRadius: '50%',
          background: 'var(--green)',
          flexShrink: 0
        }}
          className={refreshing ? '' : 'pulse'}
        />
        <span style={{ color: 'var(--text-secondary)', fontSize: 11 }}>
          {signal.stock}
        </span>
        <span style={{ color: 'var(--text-primary)', fontWeight: 700, fontSize: 15 }}>
          ₹{(signal.price || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
        </span>
      </div>

      {/* Refresh */}
      <button
        className="btn"
        onClick={onRefresh}
        disabled={refreshing}
        title="Refresh signal"
      >
        <span className={refreshing ? 'spin' : ''}>⟳</span>
        {refreshing ? 'Fetching…' : 'Refresh'}
      </button>

      {/* Auto toggle */}
      <button
        className={`btn ${autoRefresh ? 'btn-active' : ''}`}
        onClick={onToggleAuto}
        title="Toggle 60-second auto refresh"
      >
        {autoRefresh ? '⏸ Auto ON' : '▶ Auto'}
      </button>
    </div>
  )
}
