'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi, paiseToRupees } from '@/lib/api'
import { useParams, useRouter } from 'next/navigation'
import { useState } from 'react'

interface ProposalItem {
  id: string
  status: string
  bidPaise: number
  deliveryDays: number
  coverNote?: string
  designer?: {
    email?: string
    designerProfile?: {
      name?: string
      specializations?: string[]
    }
  }
}

interface ProjectDetail {
  id: string
  title: string
  brief: string
  category: string
  status: string
  budgetPaise: number
  proposals?: ProposalItem[]
}

export default function ClientProjectDetailPage() {
  const params = useParams<{ id: string }>()
  const router = useRouter()
  const queryClient = useQueryClient()
  const [accepting, setAccepting] = useState<string | null>(null)

  const { data: project, isLoading } = useQuery<ProjectDetail>({
    queryKey: ['project', params.id],
    queryFn: () => projectsApi.get(params.id),
  })

  const { mutate: acceptProposal, isPending } = useMutation({
    mutationFn: (proposalId: string) => projectsApi.acceptProposal(params.id, proposalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', params.id] })
      queryClient.invalidateQueries({ queryKey: ['my-projects'] })
      setAccepting(null)
    },
  })

  if (isLoading) return <div style={{ color: 'var(--text-muted)' }}>Loading project...</div>
  if (!project) return <div style={{ color: 'var(--error)' }}>Project not found.</div>

  const proposals: ProposalItem[] = project.proposals ?? []
  const acceptedProposal = proposals.find((p: ProposalItem) => p.status === 'ACCEPTED')

  return (
    <div style={{ maxWidth: '800px' }}>
      {/* Header */}
      <button onClick={() => router.back()} className="btn btn-ghost btn-sm" style={{ marginBottom: '1.5rem', paddingLeft: 0 }}>
        ← Back
      </button>

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '2rem', flexWrap: 'wrap' }}>
        <div>
          <h1 className="text-display-md" style={{ marginBottom: '0.5rem' }}>{project.title}</h1>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <span className={`badge badge-${project.status === 'OPEN' ? 'open' : project.status === 'COMPLETED' ? 'completed' : 'accepted'}`}>
              {project.status.replace(/_/g, ' ')}
            </span>
            <span className="text-sm" style={{ color: 'var(--text-muted)' }}>Budget: {paiseToRupees(project.budgetPaise)}</span>
            <span className="text-sm" style={{ color: 'var(--text-muted)' }}>Category: {project.category.replace(/_/g, ' ')}</span>
          </div>
        </div>
      </div>

      {/* Brief */}
      <div className="card-flat" style={{ marginBottom: '2.5rem' }}>
        <h2 className="text-heading" style={{ marginBottom: '1rem' }}>Project Brief</h2>
        <p style={{ color: 'var(--text-secondary)', whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{project.brief}</p>
      </div>

      {/* Proposals */}
      <div>
        <h2 className="text-heading" style={{ marginBottom: '1.25rem' }}>
          Proposals ({proposals.length})
        </h2>

        {proposals.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <p style={{ color: 'var(--text-muted)' }}>No proposals yet. Check back soon.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {proposals.map((proposal: ProposalItem) => (
              <div key={proposal.id} className="card" style={{
                borderColor: proposal.status === 'ACCEPTED' ? 'var(--accent)' : 'var(--border)',
                borderWidth: proposal.status === 'ACCEPTED' ? '2px' : '1px',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
                  <div>
                    <p style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                      {proposal.designer?.designerProfile?.name ?? proposal.designer?.email}
                    </p>
                    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                      {(proposal.designer?.designerProfile?.specializations ?? []).map((s: string) => (
                        <span key={s} className="badge badge-accepted">{s}</span>
                      ))}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <p style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem', fontWeight: 600, color: 'var(--accent)', marginBottom: '0.25rem' }}>
                      {paiseToRupees(proposal.bidPaise)}
                    </p>
                    <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{proposal.deliveryDays} days delivery</p>
                  </div>
                </div>

                {proposal.coverNote && (
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem', lineHeight: 1.65, marginBottom: '1rem', borderLeft: '3px solid var(--border)', paddingLeft: '1rem' }}>
                    {proposal.coverNote}
                  </p>
                )}

                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                  <span className={`badge ${proposal.status === 'ACCEPTED' ? 'badge-accepted' : proposal.status === 'REJECTED' ? 'badge-rejected' : 'badge-pending'}`}>
                    {proposal.status}
                  </span>

                  {project.status === 'OPEN' && proposal.status === 'PENDING' && !acceptedProposal && (
                    <button
                      onClick={() => {
                        setAccepting(proposal.id)
                        acceptProposal(proposal.id)
                      }}
                      disabled={isPending && accepting === proposal.id}
                      className="btn btn-primary btn-sm"
                    >
                      {isPending && accepting === proposal.id ? 'Accepting...' : 'Accept proposal'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
