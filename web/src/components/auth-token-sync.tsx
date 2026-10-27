'use client'

import { useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { setAuthToken } from '@/lib/api'
import { auth } from '@/lib/firebase'

/**
 * Sets the Firebase ID token on the axios client whenever the auth state changes.
 * Mount this component once inside authenticated layouts.
 * Firebase tokens expire in 1 hour — we refresh every 50 minutes.
 */
export function AuthTokenSync() {
  const { user } = useAuth()

  useEffect(() => {
    if (!user) {
      setAuthToken(null)
      return
    }

    let cancelled = false

    const sync = async () => {
      try {
        // forceRefresh=false on first call; true on subsequent to ensure freshness
        const token = await auth.currentUser?.getIdToken()
        if (!cancelled) setAuthToken(token ?? null)
      } catch {
        if (!cancelled) setAuthToken(null)
      }
    }

    sync()

    // Firebase tokens last 1 hour — refresh every 50 min
    const interval = setInterval(async () => {
      try {
        const token = await auth.currentUser?.getIdToken(true)
        if (!cancelled) setAuthToken(token ?? null)
      } catch {
        if (!cancelled) setAuthToken(null)
      }
    }, 50 * 60 * 1000)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [user])

  return null
}
