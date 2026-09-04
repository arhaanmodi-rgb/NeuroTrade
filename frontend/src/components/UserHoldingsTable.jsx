import React, { useState } from 'react'
import { removeHolding } from '../services/api.js'
import EditLimitModal from './EditLimitModal.jsx'

const formatINR = (val, maxDec = 2) => {
  const n = Number(val)
  return isNaN(n) ? '0' : n.toLocaleString('en-IN', { maximumFractionDigits: maxDec })
}

export default function UserHoldingsTable({ holdingsData, loading, onSelectStock, onOpenAddModal, onOpenTradeModal, onRefresh }) {
  const [selectedHoldingForLimits, setSelectedHoldingForLimits] = useState(null)
  const holdings = holdingsData?.holdings || []
  const { total_invested = 0, total_current = 0, total_pnl_inr = 0, total_pnl_pct = 0, alarms_count = 0 } = holdingsData || {}
  const isOverallProfit = (Number(total_pnl_inr) || 0) >= 0

  const handleRemove = async (e, id, sym) => {
    e.stopPropagation()
    if (window.confirm(`Remove ${sym} from your portfolio tracker?`)) {
      try {
        await removeHolding(id)
        if (onRefresh) onRefresh()
      } catch (err) {
        alert('Failed to remove holding: ' + err.message)
      }
    }
  }

  return (
    <div className="card" style={{ marginBottom: 20 }}>
      {/* Header row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 22 }}>💼</span>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
              My Purchased Stocks & Real-Time AI Advisor
            </h2>
            {alarms_count > 0 && (
              <span className="badge" style={{ background: 'rgba(220, 38, 38, 0.2)', color: '#f87171', border: '1px solid #dc2626', animation: 'pulse 1.5s infinite' }}>
                🚨 {alarms_count} ACTIVE ALARM{alarms_count > 1 ? 'S' : ''}
              </span>
            )}
          </div>
          <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
            Monitors your buy price, live market ticks, and triggers alarms if prices drop below your Stop-Loss
          </p>
        </div>

        <button
          onClick={onOpenAddModal}
          className="btn btn-primary"
          style={{ padding: '8px 16px', fontWeight: 700, fontSize: 12 }}
        >
          ➕ Add Purchased Stock
        </button>
      </div>

      {/* Portfolio Summary Strip */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
        gap: 10,
        marginBottom: 18
      }}>
        <div style={{ background: 'var(--bg-base)', borderRadius: 8, padding: '12px 14px' }}>
          <div className="label" style={{ fontSize: 10 }}>Total Invested Basis</div>
          <div style={{ fontSize: 17, fontWeight: 700, color: 'var(--text-primary)', marginTop: 2 }}>
            ₹{formatINR(total_invested, 0)}
          </div>
        </div>

        <div style={{ background: 'var(--bg-base)', borderRadius: 8, padding: '12px 14px' }}>
          <div className="label" style={{ fontSize: 10 }}>Current Live Value</div>
          <div style={{ fontSize: 17, fontWeight: 700, color: '#93c5fd', marginTop: 2 }}>
            ₹{formatINR(total_current, 0)}
          </div>
        </div>

        <div style={{ background: 'var(--bg-base)', borderRadius: 8, padding: '12px 14px' }}>
          <div className="label" style={{ fontSize: 10 }}>Net Unrealized P&L</div>
          <div style={{ fontSize: 17, fontWeight: 700, color: isOverallProfit ? 'var(--green)' : 'var(--red)', marginTop: 2 }}>
            {isOverallProfit ? '+' : ''}₹{formatINR(Math.abs(Number(total_pnl_inr) || 0), 0)}
            <span style={{ fontSize: 12, marginLeft: 6, fontWeight: 500 }}>
              ({isOverallProfit ? '+' : ''}{(Number(total_pnl_pct) || 0).toFixed(2)}%)
            </span>
          </div>
        </div>
      </div>

      {/* Holdings Table */}
      {loading && holdings.length === 0 ? (
        <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
          Loading your purchased positions...
        </div>
      ) : holdings.length === 0 ? (
        <div style={{
          padding: '36px 20px',
          textAlign: 'center',
          background: 'var(--bg-base)',
          borderRadius: 8,
          border: '1px dashed var(--border)'
        }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📊</div>
          <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 14 }}>No purchased stocks recorded yet</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4, maxWidth: 460, margin: '4px auto 16px' }}>
            Add your stocks with purchase price & quantity to get live P&L tracking, Stop-Loss alarms, and AI risk advisory.
          </div>
          <button
            onClick={onOpenAddModal}
            className="btn btn-primary"
            style={{ padding: '8px 20px', fontWeight: 600 }}
          >
            ➕ Record First Stock
          </button>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table" style={{ width: '100%', fontSize: 12 }}>
            <thead>
              <tr>
                <th>Stock</th>
                <th>Quantity</th>
                <th>Buy Price</th>
                <th>Live Price</th>
                <th>Stop Loss</th>
                <th>Target</th>
                <th>Invested Basis</th>
                <th>Live Value</th>
                <th>P&L (₹ / %)</th>
                <th>AI Advisory Action</th>
                <th>Rationale</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {holdings.map((h) => {
                const pnlInr = Number(h.pnl_inr) || 0
                const pnlPct = Number(h.pnl_pct) || 0
                const isProfit = pnlInr >= 0
                const isBreach = h.alarm_status === 'STOP_LOSS_BREACH'
                const isTarget = h.alarm_status === 'TARGET_HIT'

                let rowBg = 'transparent'
                if (isBreach) rowBg = 'rgba(220, 38, 38, 0.08)'
                if (isTarget) rowBg = 'rgba(16, 185, 129, 0.08)'

                let actionBadgeClass = 'badge badge-hold'
                if (h.ai_action?.includes('SELL')) actionBadgeClass = 'badge badge-sell'
                if (h.ai_action?.includes('BUY'))  actionBadgeClass = 'badge badge-buy'
                if (h.ai_action?.includes('HOLD')) actionBadgeClass = 'badge badge-hold'

                return (
                  <tr
                    key={h.id}
                    style={{ background: rowBg, cursor: 'pointer' }}
                    onClick={() => onSelectStock(h.stock_symbol)}
                    title="Click row to view live charts & AI analysis"
                  >
                    {/* Stock Symbol */}
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{h.stock_symbol}</span>
                        <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>{h.exchange}</span>
                        {isBreach && <span style={{ fontSize: 12 }} title="Stop Loss Breached!">🚨</span>}
                        {isTarget && <span style={{ fontSize: 12 }} title="Target Reached!">🎯</span>}
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Bought: {h.buy_date}</div>
                    </td>

                    {/* Quantity */}
                    <td style={{ fontWeight: 600 }}>{h.shares}</td>

                    {/* Buy Price */}
                    <td>₹{formatINR(h.buy_price, 2)}</td>

                    {/* Live Market Price */}
                    <td style={{ fontWeight: 700, color: '#93c5fd' }}>
                      ₹{formatINR(h.current_price, 2)}
                    </td>

                    {/* Stop Loss */}
                    <td style={{ color: 'var(--red)', fontWeight: 600 }}>
                      ₹{formatINR(h.stop_loss, 2)}
                    </td>

                    {/* Target */}
                    <td style={{ color: 'var(--green)', fontWeight: 600 }}>
                      ₹{formatINR(h.target_price, 2)}
                    </td>

                    {/* Invested Basis */}
                    <td>₹{formatINR(h.invested_amount, 0)}</td>

                    {/* Current Value */}
                    <td style={{ fontWeight: 600 }}>
                      ₹{formatINR(h.current_value, 0)}
                    </td>

                    {/* P&L */}
                    <td>
                      <span style={{
                        fontWeight: 700,
                        color: isProfit ? 'var(--green)' : 'var(--red)'
                      }}>
                        {isProfit ? '+' : ''}₹{formatINR(Math.abs(pnlInr), 0)}
                      </span>
                      <div style={{ fontSize: 11, fontWeight: 600, color: isProfit ? 'var(--green)' : 'var(--red)' }}>
                        {isProfit ? '+' : ''}{pnlPct.toFixed(2)}%
                      </div>
                    </td>

                    {/* AI Action & Alarm */}
                    <td>
                      <span className={actionBadgeClass} style={{ fontSize: 10, whiteSpace: 'nowrap' }}>
                        {h.ai_action}
                      </span>
                    </td>

                    {/* Rationale */}
                    <td style={{ maxWidth: 260, fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                      {h.ai_rationale}
                    </td>

                    {/* Actions */}
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: 6, alignItems: 'center', justifyContent: 'flex-end' }}>
                        <button
                          className="btn"
                          onClick={(e) => {
                            e.stopPropagation()
                            onSelectStock(h.stock_symbol)
                          }}
                          style={{ padding: '4px 8px', fontSize: 11, color: '#93c5fd' }}
                          title="View Technical Chart"
                        >
                          📈 Chart
                        </button>

                        <button
                          className="btn"
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedHoldingForLimits(h)
                          }}
                          style={{ padding: '4px 8px', fontSize: 11 }}
                          title="Edit Target and Stop Loss"
                        >
                          ⚙️ SL
                        </button>

                        <button
                          className="btn btn-primary"
                          onClick={(e) => {
                            e.stopPropagation()
                            onOpenTradeModal(h.stock_symbol, h.current_price, 'SELL')
                          }}
                          style={{ padding: '4px 8px', fontSize: 11, background: isBreach ? '#dc2626' : undefined }}
                          title="Sell Shares"
                        >
                          Sell
                        </button>

                        <button
                          className="btn"
                          onClick={(e) => handleRemove(e, h.id, h.stock_symbol)}
                          style={{ padding: '4px 8px', fontSize: 11, color: 'var(--red)' }}
                          title="Delete record"
                        >
                          ✕
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Edit SL/Target Modal */}
      {selectedHoldingForLimits && (
        <EditLimitModal
          holding={selectedHoldingForLimits}
          onClose={() => setSelectedHoldingForLimits(null)}
          onUpdated={() => {
            setSelectedHoldingForLimits(null)
            if (onRefresh) onRefresh()
          }}
        />
      )}
    </div>
  )
}
