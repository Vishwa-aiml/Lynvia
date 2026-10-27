'use client'

import Link from 'next/link'
import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'

export function Navbar() {
  const { user, signOut } = useAuth()
  const router = useRouter()

  const handleSignOut = async () => {
    await signOut()
    router.push('/')
  }

  return (
    <header style={{
      background: 'var(--bg-primary)',
      borderBottom: '1px solid var(--border)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
    }}>
      <div className="container-xl" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '64px',
      }}>
        {/* Logo */}
        <Link href="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.5rem',
            fontWeight: 600,
            color: 'var(--text-primary)',
            letterSpacing: '-0.02em',
          }}>
            Lynvia
          </span>
          <span style={{
            fontSize: '0.625rem',
            fontWeight: 600,
            color: 'var(--accent)',
            background: 'var(--accent-surface)',
            padding: '2px 7px',
            borderRadius: '99px',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginTop: '2px',
          }}>
            Beta
          </span>
        </Link>

        {/* Center nav */}
        <nav style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
          <Link href="/designers" className="nav-link">Find Designers</Link>
          <Link href="/#how-it-works" className="nav-link">How it works</Link>
        </nav>

        {/* Right actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {user ? (
            <>
              <Link href="/dashboard" className="btn btn-ghost btn-sm">Dashboard</Link>
              <button
                onClick={handleSignOut}
                className="btn btn-ghost btn-sm"
                id="navbar-sign-out"
                style={{ color: 'var(--text-muted)' }}
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link href="/sign-in" className="btn btn-ghost btn-sm" id="navbar-sign-in">
                Sign in
              </Link>
              <Link href="/sign-up" className="btn btn-primary btn-sm" id="navbar-get-started">
                Get started
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
