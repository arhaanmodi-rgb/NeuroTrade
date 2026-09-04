import React, { useState } from 'react'
import { loginUser, registerUser } from '../services/api.js'

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isRegister, setIsRegister] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  if (!isOpen) return null

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      let res
      if (isRegister) {
        res = await registerUser(formData)
      } else {
        res = await loginUser({
          username_or_email: formData.username || formData.email,
          password: formData.password
        })
      }

      if (res.access_token) {
        localStorage.setItem('neurotrade_token', res.access_token)
        localStorage.setItem('neurotrade_user', JSON.stringify(res.user))
        onAuthSuccess(res.user)
        onClose()
      }
    } catch (err) {
      setError(err.message || 'Authentication failed')
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
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.8)',
        position: 'relative'
      }}>
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 16,
            right: 16,
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            fontSize: 18,
            cursor: 'pointer'
          }}
        >
          ✕
        </button>

        {/* Title */}
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <span style={{ fontSize: 32 }}>🔐</span>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginTop: 8, color: 'var(--text-primary)' }}>
            {isRegister ? 'Create NeuroTrade Account' : 'Welcome Back'}
          </h2>
          <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
            {isRegister
              ? 'Access 7,000+ NSE/BSE stocks and save personalized watchlists'
              : 'Sign in to access your personal AI signals and portfolio'}
          </p>
        </div>

        {error && (
          <div style={{
            background: 'var(--red-bg)',
            border: '1px solid #7f1d1d',
            borderRadius: 8,
            padding: '10px 14px',
            marginBottom: 16,
            color: '#fca5a5',
            fontSize: 12
          }}>
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {isRegister && (
            <div>
              <label className="label" style={{ display: 'block', marginBottom: 6 }}>Full Name</label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                placeholder="e.g. Rahul Sharma"
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
          )}

          <div>
            <label className="label" style={{ display: 'block', marginBottom: 6 }}>
              {isRegister ? 'Username' : 'Username or Email'}
            </label>
            <input
              type="text"
              name="username"
              required
              value={formData.username}
              onChange={handleChange}
              placeholder={isRegister ? 'Choose a unique username' : 'Enter username or email'}
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

          {isRegister && (
            <div>
              <label className="label" style={{ display: 'block', marginBottom: 6 }}>Email Address</label>
              <input
                type="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                placeholder="user@example.com"
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
          )}

          <div>
            <label className="label" style={{ display: 'block', marginBottom: 6 }}>Password</label>
            <input
              type="password"
              name="password"
              required
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
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
              marginTop: 6
            }}
          >
            {loading ? 'Processing...' : (isRegister ? 'Sign Up' : 'Sign In')}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: 18, fontSize: 12, color: 'var(--text-muted)' }}>
          {isRegister ? 'Already have an account?' : "Don't have an account yet?"}{' '}
          <button
            onClick={() => { setIsRegister(!isRegister); setError(null) }}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--blue)',
              fontWeight: 600,
              cursor: 'pointer',
              textDecoration: 'underline'
            }}
          >
            {isRegister ? 'Log In' : 'Register Here'}
          </button>
        </div>
      </div>
    </div>
  )
}
