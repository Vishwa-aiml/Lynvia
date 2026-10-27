'use client'

import { useAuth } from '@/contexts/auth-context'
import { useQuery } from '@tanstack/react-query'
import { authApi } from '@/lib/api'
import { AuthTokenSync } from '@/components/auth-token-sync'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect } from 'react'

function Sidebar({ role }: { role: 'CLIENT' | 'DESIGNER' | 'ADMIN' }) {
  const pathname = usePathname()

  const clientLinks = [
    { href: '/dashboard/client', label: 'My Projects' },
    { href: '/dashboard/client/post', label: '+ Post Project' },
  ]
  const designerLinks = [
    { href: '/dashboard/designer', label: 'Browse Projects' },
    { href: '/dashboard/designer/proposals', label: 'My Proposals' },
    { href: '/dashboard/designer/profile', label: 'My Profile' },
  ]
  const adminLinks = [
    { href: '/dashboard/admin', label: 'Vetting Queue' },
    { href: '/dashboard/admin/users', label: 'Users' },
  ]

  const links = role === 'CLIENT' ? clientLinks : role === 'DESIGNER' ? designerLinks : adminLinks

  return (
    <aside style={{
      width: '220px',
      flexShrink: 0,
      borderRight: '1px solid var(--border)',
      padding: '2rem 0',
      minHeight: 'calc(100vh - 64px)',
      background: 'var(--bg-primary)',
    }}>
      <div style={{ padding: '0 1.5rem', marginBottom: '2rem' }}>
        <span className="text-xs" style={{
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          fontWeight: 500,
        }}>
          {role === 'CLIENT' ? 'Client' : role === 'DESIGNER' ? 'Designer' : 'Admin'} Dashboard
        </span>
      </div>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', padding: '0 0.75rem' }}>
        {links.map((link) => (
          <Link key={link.href} href={link.href} style={{
            display: 'block',
            padding: '0.5rem 0.75rem',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.9375rem',
            color: pathname === link.href ? 'var(--accent)' : 'var(--text-secondary)',
            background: pathname === link.href ? 'var(--accent-surface)' : 'transparent',
            fontWeight: pathname === link.href ? 500 : 400,
            textDecoration: 'none',
            transition: 'all var(--transition-fast)',
          }}>
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  )
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading: authLoading, signOut } = useAuth()
  const router = useRouter()

  // Redirect to sign-in if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/sign-in')
    }
  }, [authLoading, user, router])

  const { data: me, isLoading: meLoading } = useQuery({
    queryKey: ['me'],
    queryFn: authApi.me,
    enabled: !!user, // only fetch after Firebase user is known
  })

  // Role-based route guard: prevent navigating to unpermitted role dashboards
  useEffect(() => {
    if (typeof window === 'undefined') return
    const path = window.location.pathname
    if (me && me.role) {
      if (path.startsWith('/dashboard/admin') && me.role !== 'ADMIN') {
        router.replace(me.role === 'DESIGNER' ? '/dashboard/designer' : '/dashboard/client')
      } else if (path.startsWith('/dashboard/client') && me.role === 'DESIGNER') {
        router.replace('/dashboard/designer')
      } else if (path.startsWith('/dashboard/designer') && me.role === 'CLIENT') {
        router.replace('/dashboard/client')
      }
    }
    if (me && !me.onboardingComplete) {
      router.replace('/onboarding')
    }
  }, [me, router])

  const isLoading = authLoading || meLoading

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        color: 'var(--text-muted)',
      }}>
        Loading...
      </div>
    )
  }

  if (!user) return null // redirecting

  // Not onboarded — redirect to onboarding
  if (me && !me.onboardingComplete) {
    return null
  }

  const role = me?.role ?? 'CLIENT'

  const handleSignOut = async () => {
    await signOut()
    router.push('/')
  }

  return (
    <>
      <AuthTokenSync />
      {/* Top bar */}
      <header style={{
        height: '64px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 1.5rem',
        background: 'var(--bg-primary)',
        position: 'sticky',
        top: 0,
        zIndex: 40,
      }}>
        <Link href="/" style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1.25rem',
          fontWeight: 600,
          color: 'var(--text-primary)',
          textDecoration: 'none',
        }}>
          Lynvia
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span className="text-sm" style={{ color: 'var(--text-muted)' }}>
            {user.email}
          </span>
          <button
            onClick={handleSignOut}
            className="btn btn-ghost btn-sm"
            id="dashboard-sign-out"
            style={{ color: 'var(--text-muted)' }}
          >
            Sign out
          </button>
        </div>
      </header>

      <div style={{ display: 'flex' }}>
        <Sidebar role={role} />
        <main style={{
          flex: 1,
          padding: '2.5rem',
          background: 'var(--bg-secondary)',
          minHeight: 'calc(100vh - 64px)',
        }}>
          {children}
        </main>
      </div>
    </>
  )
}
