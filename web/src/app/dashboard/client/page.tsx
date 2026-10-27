'use client'

import { useQuery } from '@tanstack/react-query'
import { projectsApi, paiseToRupees } from '@/lib/api'
import Link from 'next/link'

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    OPEN: 'badge-open',
    PROPOSAL_ACCEPTED: 'badge-accepted',
    IN_PROGRESS: 'badge-accepted',
    DELIVERED: 'badge-pending',
    REVISION_REQUESTED: 'badge-pending',
    COMPLETED: 'badge-completed',
    CANCELLED: 'badge-rejected',
    DISPUTED: 'badge-rejected',
  }
  return <span className={`badge ${map[status] ?? 'badge-pending'}`}>{status.replace(/_/g, ' ')}</span>
}

export default function ClientDashboard() {
  const { data: projects, isLoading } = useQuery({
    queryKey: ['my-projects'],
    queryFn: projectsApi.mine,
  })

  return (
    <div>
      {/* Page header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2.5rem' }}>
        <div>
          <h1 className="text-display-md" style={{ marginBottom: '0.5rem' }}>My Projects</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Track all your active and completed design projects.</p>
        </div>
        <Link href="/dashboard/client/post" className="btn btn-primary">
          + Post a project
        </Link>
      </div>

      {isLoading ? (
        <div style={{ color: 'var(--text-muted)', padding: '3rem 0', textAlign: 'center' }}>Loading your projects...</div>
      ) : !projects?.length ? (
        /* Empty state */
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem', color: 'var(--accent-light)' }}>◈</div>
          <h2 className="text-heading" style={{ marginBottom: '0.75rem' }}>No projects yet</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Post your first project and start receiving proposals from vetted designers.
          </p>
          <Link href="/dashboard/client/post" className="btn btn-primary">Post your first project →</Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {projects.map((project: any) => (
            <Link key={project.id} href={`/dashboard/client/projects/${project.id}`} style={{ textDecoration: 'none' }}>
              <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1.5rem', cursor: 'pointer' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                    <h3 className="text-heading" style={{ margin: 0 }}>{project.title}</h3>
                    <StatusBadge status={project.status} />
                  </div>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)', margin: 0 }}>
                    Budget: {paiseToRupees(project.budgetPaise)} &nbsp;·&nbsp;
                    {project._count.proposals} proposal{project._count.proposals !== 1 ? 's' : ''}
                  </p>
                </div>
                <span style={{ color: 'var(--accent)', fontSize: '1.25rem' }}>→</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
