import { Navbar } from '@/components/navbar'
import { designersApi } from '@/lib/api'

export const metadata = {
  title: 'Find Designers — Lynvia',
  description: 'Browse vetted Indian designers for logos, branding, and social media design.',
}

async function getDesigners() {
  try {
    // Server-side fetch at build/request time
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/designers`, {
      next: { revalidate: 60 }, // ISR — refresh every 60s
    })
    if (!res.ok) return []
    return res.json()
  } catch {
    return []
  }
}

export default async function DesignersPage() {
  const designers = await getDesigners()

  return (
    <>
      <Navbar />
      <main>
        <section style={{ padding: 'clamp(3rem,6vw,5rem) 0 2rem' }}>
          <div className="container-xl">
            <p className="text-sm" style={{ color: 'var(--accent)', fontWeight: 500, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
              Our designers
            </p>
            <h1 className="text-display-lg" style={{ marginBottom: '0.75rem' }}>
              Vetted creative talent
            </h1>
            <p className="text-body-lg" style={{ color: 'var(--text-secondary)', maxWidth: '560px', marginBottom: '3rem' }}>
              Every designer on Lynvia is manually reviewed before they can take on client work.
            </p>

            {designers.length === 0 ? (
              <div className="card" style={{ textAlign: 'center', padding: '5rem 2rem' }}>
                <p style={{ color: 'var(--text-muted)' }}>Designers coming soon — we're vetting our first cohort.</p>
              </div>
            ) : (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                gap: '1.5rem',
              }}>
                {designers.map((designer: any) => (
                  <a
                    key={designer.userId}
                    href={`/designers/${designer.userId}`}
                    style={{ textDecoration: 'none', display: 'block' }}
                  >
                    <div className="card" style={{ height: '100%' }}>
                      {/* Avatar placeholder */}
                      <div style={{
                        width: '56px',
                        height: '56px',
                        borderRadius: '50%',
                        background: 'var(--accent-surface)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontFamily: 'var(--font-display)',
                        fontSize: '1.25rem',
                        fontWeight: 600,
                        color: 'var(--accent)',
                        marginBottom: '1rem',
                        flexShrink: 0,
                      }}>
                        {designer.name?.charAt(0) ?? '?'}
                      </div>

                      <h2 className="text-heading" style={{ marginBottom: '0.375rem' }}>{designer.name}</h2>

                      {designer.bio && (
                        <p className="text-sm" style={{ color: 'var(--text-secondary)', marginBottom: '1rem', lineHeight: 1.6 }}>
                          {designer.bio.length > 120 ? designer.bio.slice(0, 120) + '…' : designer.bio}
                        </p>
                      )}

                      {designer.specializations?.length > 0 && (
                        <div style={{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap', marginTop: 'auto' }}>
                          {designer.specializations.slice(0, 4).map((s: string) => (
                            <span key={s} className="badge badge-accepted">{s}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  </a>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </>
  )
}
