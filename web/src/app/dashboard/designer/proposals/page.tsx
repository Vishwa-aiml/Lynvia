'use client'

import { useQuery } from '@tanstack/react-query'
import { proposalsApi, paiseToRupees } from '@/lib/api'

function StatusBadge({ status }: { status: string }) {
  const cls = status === 'ACCEPTED' ? 'badge-accepted' : status === 'REJECTED' ? 'badge-rejected' : 'badge-pending'
  return <span className={`badge ${cls}`}>{status}</span>
}

export default function MyProposalsPage() {
  const { data: proposals, isLoading } = useQuery({
    queryKey: ['my-proposals'],
    queryFn: proposalsApi.mine,
    refetchInterval: 30_000,
  })

  return (
    <div>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 className="text-display-md" style={{ marginBottom: '0.5rem' }}>My Proposals</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Track the status of every proposal you've submitted.</p>
      </div>

      {isLoading ? (
        <div style={{ color: 'var(--text-muted)', padding: '3rem 0', textAlign: 'center' }}>Loading proposals...</div>
      ) : !proposals?.length ? (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem', color: 'var(--accent-light)' }}>✦</div>
          <h2 className="text-heading" style={{ marginBottom: '0.75rem' }}>No proposals yet</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Browse open projects and submit your first proposal.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {proposals.map((proposal: any) => (
            <div key={proposal.id} className="card" style={{
              borderLeft: `4px solid ${proposal.status === 'ACCEPTED' ? 'var(--accent)' : proposal.status === 'REJECTED' ? 'var(--error)' : 'var(--border)'}`,
              borderRadius: '0 var(--radius-lg) var(--radius-lg) 0',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h3 className="text-heading" style={{ marginBottom: '0.375rem' }}>{proposal.project?.title}</h3>
                  <p className="text-sm" style={{ color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                    {proposal.project?.category?.replace(/_/g, ' ')} &nbsp;·&nbsp; {proposal.deliveryDays} days delivery
                  </p>
                  <StatusBadge status={proposal.status} />
                </div>
                <div style={{ textAlign: 'right' }}>
                  <p style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 600, color: 'var(--accent)', marginBottom: '0.25rem' }}>
                    {paiseToRupees(proposal.bidPaise)}
                  </p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                    You receive: {paiseToRupees(Math.floor(proposal.bidPaise * 0.9))}
                  </p>
                </div>
              </div>
              {proposal.coverNote && (
                <p className="text-sm" style={{ color: 'var(--text-secondary)', marginTop: '1rem', borderTop: '1px solid var(--border)', paddingTop: '0.875rem' }}>
                  {proposal.coverNote}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
