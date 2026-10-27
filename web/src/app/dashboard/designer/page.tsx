'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi, proposalsApi, paiseToRupees, rupeesToPaise } from '@/lib/api'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState } from 'react'
import Link from 'next/link'

const proposalSchema = z.object({
  bidRupees: z.coerce.number().min(100, 'Minimum bid ₹100'),
  deliveryDays: z.coerce.number().int().min(1).max(365),
  coverNote: z.string().max(1000).optional(),
})
type ProposalForm = z.infer<typeof proposalSchema>

function ProposalModal({ project, onClose }: { project: any; onClose: () => void }) {
  const queryClient = useQueryClient()
  const { register, handleSubmit, formState: { errors } } = useForm({ resolver: zodResolver(proposalSchema) as any })

  const { mutate, isPending, error } = useMutation({
    mutationFn: (data: any) =>
      proposalsApi.create({
        projectId: project.id,
        bidPaise: rupeesToPaise(data.bidRupees),
        deliveryDays: data.deliveryDays,
        coverNote: data.coverNote,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['open-projects'] })
      queryClient.invalidateQueries({ queryKey: ['my-proposals'] })
      onClose()
    },
  })

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(28,26,23,0.4)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 100, padding: '1.5rem',
    }}>
      <div className="card" style={{ width: '100%', maxWidth: '520px', maxHeight: '90vh', overflowY: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 className="text-heading">Submit a proposal</h2>
          <button onClick={onClose} className="btn btn-ghost btn-sm">✕</button>
        </div>

        <div className="card-flat" style={{ marginBottom: '1.5rem', padding: '1rem' }}>
          <p style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{project.title}</p>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Budget: {paiseToRupees(project.budgetPaise)}</p>
        </div>

        <form onSubmit={handleSubmit((d) => mutate(d))} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label className="field-label">Your bid (₹) *</label>
              <div style={{ position: 'relative' }}>
                <span style={{ position: 'absolute', left: '0.875rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }}>₹</span>
                <input {...register('bidRupees')} type="number" className="input" style={{ paddingLeft: '1.75rem' }} placeholder="5000" />
              </div>
              {errors['bidRupees'] && <p className="field-error">{errors['bidRupees'].message as string}</p>}
            </div>
            <div>
              <label className="field-label">Delivery (days) *</label>
              <input {...register('deliveryDays')} type="number" className="input" placeholder="7" />
              {errors['deliveryDays'] && <p className="field-error">{errors['deliveryDays'].message as string}</p>}
            </div>
          </div>

          <div>
            <label className="field-label">Cover note <span style={{ fontWeight: 400, color: 'var(--text-muted)' }}>(optional)</span></label>
            <textarea {...register('coverNote')} className="input textarea" placeholder="Briefly explain your approach and why you're a good fit..." />
            {errors['coverNote'] && <p className="field-error">{errors['coverNote'].message as string}</p>}
          </div>

          {error && <p style={{ color: 'var(--error)', fontSize: '0.875rem' }}>{(error as any).response?.data?.message ?? 'Failed to submit. Try again.'}</p>}

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button type="button" onClick={onClose} className="btn btn-ghost">Cancel</button>
            <button type="submit" disabled={isPending} className="btn btn-primary" style={{ flex: 1 }}>
              {isPending ? 'Submitting...' : 'Submit proposal →'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function DesignerDashboard() {
  const [selectedProject, setSelectedProject] = useState<any | null>(null)

  const { data: projects, isLoading } = useQuery({
    queryKey: ['open-projects'],
    queryFn: projectsApi.list,
    refetchInterval: 30_000, // Poll every 30s (Stage B polling strategy)
  })

  return (
    <div>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 className="text-display-md" style={{ marginBottom: '0.5rem' }}>Browse Projects</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Open projects from clients. Submit proposals on work you want to take.</p>
      </div>

      {isLoading ? (
        <div style={{ color: 'var(--text-muted)', padding: '3rem 0', textAlign: 'center' }}>Loading projects...</div>
      ) : !projects?.length ? (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <p style={{ color: 'var(--text-muted)' }}>No open projects right now. Check back soon.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {projects.map((project: any) => (
            <div key={project.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                    <h3 className="text-heading" style={{ margin: 0 }}>{project.title}</h3>
                    <span className="badge badge-accepted" style={{ fontSize: '0.7rem' }}>
                      {project.category.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: '0.75rem', maxWidth: '600px' }}>
                    {project.brief.length > 180 ? project.brief.slice(0, 180) + '…' : project.brief}
                  </p>
                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    <span className="text-sm" style={{ color: 'var(--text-muted)' }}>Budget: <strong style={{ color: 'var(--accent)' }}>{paiseToRupees(project.budgetPaise)}</strong></span>
                    <span className="text-sm" style={{ color: 'var(--text-muted)' }}>{project._count?.proposals ?? 0} proposals</span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedProject(project)}
                  className="btn btn-primary btn-sm"
                  style={{ flexShrink: 0 }}
                >
                  Submit proposal
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedProject && (
        <ProposalModal project={selectedProject} onClose={() => setSelectedProject(null)} />
      )}
    </div>
  )
}
