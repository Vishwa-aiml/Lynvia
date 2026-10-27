'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { designersApi } from '@/lib/api'
import { useState } from 'react'

interface PendingDesigner {
  id: string
  name: string
  bio?: string
  specializations?: string[]
  portfolioUrls?: string[]
  user?: { email?: string }
}

export default function AdminVettingPage() {
  const queryClient = useQueryClient()
  const [note, setNote] = useState<Record<string, string>>({})

  const { data: pending, isLoading } = useQuery<PendingDesigner[]>({
    queryKey: ['pending-designers'],
    queryFn: designersApi.pendingDesigners,
    refetchInterval: 60_000,
  })

  const { mutate: updateVetting, isPending: isUpdating } = useMutation({
    mutationFn: ({ userId, status, note }: { userId: string; status: 'APPROVED' | 'REJECTED'; note?: string }) =>
      designersApi.updateVetting(userId, status, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-designers'] })
    },
  })

  return (
    <div>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 className="text-display-md" style={{ marginBottom: '0.5rem' }}>Designer Vetting Queue</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Review designer applications. Only approved designers appear in public listings.
        </p>
      </div>

      {isLoading ? (
        <div style={{ color: 'var(--text-muted)', padding: '3rem 0', textAlign: 'center' }}>Loading...</div>
      ) : !pending?.length ? (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>✓</div>
          <h2 className="text-heading">Queue is clear</h2>
          <p style={{ color: 'var(--text-secondary)' }}>No pending designer applications right now.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {pending.map((designer: PendingDesigner) => (
            <div key={designer.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <h3 className="text-heading" style={{ marginBottom: '0.25rem' }}>{designer.name}</h3>
                  <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{designer.user?.email}</p>
                </div>
                <span className="badge badge-pending">PENDING</span>
              </div>

              {designer.bio && (
                <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem', fontSize: '0.9375rem' }}>{designer.bio}</p>
              )}

              {designer.specializations?.length > 0 && (
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                  {designer.specializations.map((s: string) => (
                    <span key={s} className="badge badge-accepted">{s}</span>
                  ))}
                </div>
              )}

              <div style={{ marginBottom: '1rem' }}>
                <label className="field-label">Internal note (optional)</label>
                <input
                  className="input"
                  placeholder="Reason for approval/rejection..."
                  value={note[designer.userId] ?? ''}
                  onChange={(e) => setNote((n) => ({ ...n, [designer.userId]: e.target.value }))}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <button
                  onClick={() => updateVetting({ userId: designer.userId, status: 'APPROVED', note: note[designer.userId] })}
                  disabled={isUpdating}
                  className="btn btn-primary btn-sm"
                  style={{ background: 'var(--success)', borderColor: 'var(--success)' }}
                >
                  ✓ Approve
                </button>
                <button
                  onClick={() => updateVetting({ userId: designer.userId, status: 'REJECTED', note: note[designer.userId] })}
                  disabled={isUpdating}
                  className="btn btn-secondary btn-sm"
                  style={{ color: 'var(--error)', borderColor: 'var(--error)' }}
                >
                  ✕ Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
