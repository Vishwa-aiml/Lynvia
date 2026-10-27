'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth, firebaseErrorMessage } from '@/contexts/auth-context'

/** Google "G" logo as an inline SVG — no external dependency needed */
function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M17.64 9.205c0-.638-.057-1.252-.164-1.841H9v3.481h4.844a4.14 4.14 0 0 1-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615Z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18Z" fill="#34A853"/>
      <path d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332Z" fill="#FBBC05"/>
      <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58Z" fill="#EA4335"/>
    </svg>
  )
}

function Divider() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', margin: '0.25rem 0' }}>
      <div style={{ flex: 1, height: '1px', background: 'var(--border)' }} />
      <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>or continue with email</span>
      <div style={{ flex: 1, height: '1px', background: 'var(--border)' }} />
    </div>
  )
}

export default function SignInPage() {
  const { signIn, signInWithGoogle } = useAuth()
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await signIn(email, password)
      router.push('/dashboard')
    } catch (err) {
      setError(firebaseErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const handleGoogle = async () => {
    setError(null)
    setGoogleLoading(true)
    try {
      await signInWithGoogle()
      router.push('/dashboard')
    } catch (err) {
      const msg = firebaseErrorMessage(err)
      if (msg) setError(msg) // silent if user just closed the popup
    } finally {
      setGoogleLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-primary)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
    }}>
      <div style={{ width: '100%', maxWidth: '420px' }}>
        {/* Brand */}
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <Link href="/" style={{ textDecoration: 'none' }}>
            <span style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.75rem',
              fontWeight: 600,
              color: 'var(--text-primary)',
              letterSpacing: '-0.02em',
            }}>
              Lynvia
            </span>
          </Link>
          <h1 className="text-display-sm" style={{ marginTop: '1.5rem', marginBottom: '0.5rem' }}>
            Welcome back
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem' }}>
            Sign in to your Lynvia account
          </p>
        </div>

        {/* Decorative line */}
        <div style={{
          height: '2px',
          background: 'linear-gradient(90deg, transparent, var(--accent), transparent)',
          marginBottom: '2rem',
          opacity: 0.3,
        }} />

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* ── Google button ── */}
          <button
            type="button"
            onClick={handleGoogle}
            disabled={googleLoading || loading}
            id="google-sign-in"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.625rem',
              width: '100%',
              padding: '0.6875rem 1rem',
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.9375rem',
              fontWeight: 500,
              color: 'var(--text-primary)',
              cursor: googleLoading ? 'wait' : 'pointer',
              transition: 'all var(--transition-fast)',
              fontFamily: 'var(--font-body)',
            }}
            onMouseEnter={(e) => { if (!googleLoading) (e.currentTarget.style.borderColor = 'var(--accent)') }}
            onMouseLeave={(e) => { (e.currentTarget.style.borderColor = 'var(--border)') }}
          >
            <GoogleIcon />
            {googleLoading ? 'Signing in…' : 'Continue with Google'}
          </button>

          <Divider />

          {/* ── Email/password form ── */}
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label className="field-label" htmlFor="email">Email address</label>
              <input
                id="email"
                type="email"
                className="input"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <div>
              <label className="field-label" htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                className="input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>

            {error && (
              <p style={{
                color: 'var(--error)',
                fontSize: '0.875rem',
                background: 'rgba(220,38,38,0.06)',
                border: '1px solid rgba(220,38,38,0.15)',
                borderRadius: 'var(--radius-md)',
                padding: '0.75rem 1rem',
              }}>
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading || googleLoading}
              className="btn btn-primary"
              style={{ width: '100%' }}
              id="sign-in-submit"
            >
              {loading ? 'Signing in…' : 'Sign in →'}
            </button>
          </form>
        </div>

        <p style={{
          textAlign: 'center',
          marginTop: '1.75rem',
          fontSize: '0.9375rem',
          color: 'var(--text-muted)',
        }}>
          New to Lynvia?{' '}
          <Link href="/sign-up" style={{ color: 'var(--accent)', fontWeight: 500, textDecoration: 'none' }}>
            Create an account
          </Link>
        </p>
      </div>
    </div>
  )
}
