import { Navbar } from '@/components/navbar'
import Link from 'next/link'

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main>
        {/* ── Hero ──────────────────────────────────────────────────────── */}
        <section style={{
          padding: 'clamp(4rem, 10vw, 8rem) 0 clamp(3rem, 8vw, 6rem)',
          background: 'var(--bg-primary)',
          position: 'relative',
          overflow: 'hidden',
        }}>
          {/* Subtle decorative element */}
          <div style={{
            position: 'absolute',
            top: '-120px',
            right: '-80px',
            width: '500px',
            height: '500px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(91,58,107,0.06) 0%, transparent 70%)',
            pointerEvents: 'none',
          }} />

          <div className="container-xl">
            <div style={{ maxWidth: '720px' }}>
              <p className="text-sm animate-fade-up" style={{
                color: 'var(--accent)',
                fontWeight: 500,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                marginBottom: '1.25rem',
              }}>
                India&apos;s creative marketplace
              </p>

              <h1 className="text-display-xl animate-fade-up animate-delay-1" style={{
                color: 'var(--text-primary)',
                marginBottom: '1.5rem',
              }}>
                Beautiful design,<br/>
                <em style={{ fontStyle: 'italic', color: 'var(--accent)' }}>crafted for you</em>
              </h1>

              <p className="text-body-lg animate-fade-up animate-delay-2" style={{
                color: 'var(--text-secondary)',
                maxWidth: '560px',
                marginBottom: '2.5rem',
              }}>
                Post your project. Get proposals from vetted Indian designers.
                Logos, branding, posters — work you&apos;ll be proud of.
              </p>

              <div className="animate-fade-up animate-delay-3" style={{
                display: 'flex',
                gap: '1rem',
                flexWrap: 'wrap',
              }}>
                <Link href="/sign-up" className="btn btn-primary btn-lg">
                  Post a project
                </Link>
                <Link href="/designers" className="btn btn-secondary btn-lg">
                  Find designers
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* ── Trust strip ──────────────────────────────────────────────── */}
        <section style={{
          background: 'var(--bg-secondary)',
          borderTop: '1px solid var(--border)',
          borderBottom: '1px solid var(--border)',
          padding: '1.5rem 0',
        }}>
          <div className="container-xl" style={{
            display: 'flex',
            gap: '2.5rem',
            flexWrap: 'wrap',
            alignItems: 'center',
          }}>
            {[
              { icon: '✦', label: 'Vetted designers only' },
              { icon: '✦', label: 'Secure payment escrow' },
              { icon: '✦', label: 'INR pricing, no forex fees' },
              { icon: '✦', label: 'Revision rounds included' },
            ].map((item) => (
              <div key={item.label} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                color: 'var(--text-secondary)',
                fontSize: '0.875rem',
              }}>
                <span style={{ color: 'var(--accent)', fontSize: '0.625rem' }}>{item.icon}</span>
                {item.label}
              </div>
            ))}
          </div>
        </section>

        {/* ── Categories ────────────────────────────────────────────────── */}
        <section className="section">
          <div className="container-xl">
            <p className="text-sm" style={{
              color: 'var(--accent)',
              fontWeight: 500,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: '0.75rem',
            }}>What we offer</p>
            <h2 className="text-display-md" style={{ marginBottom: '3rem' }}>
              Two categories, launching now
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
              gap: '1.5rem',
            }}>
              {[
                {
                  category: 'logo_branding',
                  title: 'Logo & Branding',
                  desc: 'Full brand identity systems — wordmarks, logomarks, colour palettes, type choices. For founders and businesses that want to start with their best foot forward.',
                  tags: ['Logo design', 'Brand identity', 'Business card', 'Brand guide'],
                  href: '/projects/new?category=logo_branding',
                },
                {
                  category: 'poster_social',
                  title: 'Posters & Social Media',
                  desc: 'Campaign posters, Instagram stories, YouTube thumbnails, event creatives. Scroll-stopping visuals built for the platforms your audience lives on.',
                  tags: ['Instagram creatives', 'Event poster', 'YouTube thumbnail', 'Ad banner'],
                  href: '/projects/new?category=poster_social',
                },
              ].map((cat) => (
                <div key={cat.category} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div style={{
                    background: 'var(--accent-surface)',
                    borderRadius: 'var(--radius-md)',
                    height: '180px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '3rem',
                  }}>
                    {cat.category === 'logo_branding' ? '◈' : '▦'}
                  </div>
                  <h3 className="text-heading">{cat.title}</h3>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)', flex: 1 }}>{cat.desc}</p>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    {cat.tags.map((tag) => (
                      <span key={tag} className="badge badge-accepted">{tag}</span>
                    ))}
                  </div>
                  <Link href={cat.href} className="btn btn-primary" style={{ marginTop: '0.5rem' }}>
                    Post a project →
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── How it works ──────────────────────────────────────────────── */}
        <section id="how-it-works" className="section" style={{ background: 'var(--bg-secondary)' }}>
          <div className="container-lg">
            <p className="text-sm" style={{
              color: 'var(--accent)',
              fontWeight: 500,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: '0.75rem',
              textAlign: 'center',
            }}>The process</p>
            <h2 className="text-display-md" style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
              Simple from start to finish
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '2rem',
            }}>
              {[
                { step: '01', title: 'Post your brief', desc: 'Describe what you need, set a budget in rupees. Takes 3 minutes.' },
                { step: '02', title: 'Receive proposals', desc: 'Vetted designers submit proposals with quotes and timelines.' },
                { step: '03', title: 'Pick your designer', desc: 'Review portfolios, read proposals, accept the one that fits.' },
                { step: '04', title: 'Approve & pay', desc: 'Payment releases only when you\'re happy with the final work.' },
              ].map((item) => (
                <div key={item.step} style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
                  <span style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '3rem',
                    fontWeight: 300,
                    color: 'var(--accent-light)',
                    opacity: 0.5,
                    display: 'block',
                    marginBottom: '1rem',
                  }}>{item.step}</span>
                  <h3 className="text-heading" style={{ marginBottom: '0.5rem' }}>{item.title}</h3>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── CTA ───────────────────────────────────────────────────────── */}
        <section className="section">
          <div className="container-md" style={{ textAlign: 'center' }}>
            <h2 className="text-display-md" style={{ marginBottom: '1rem' }}>
              Ready to get started?
            </h2>
            <p className="text-body-lg" style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
              Join designers and clients building great things together.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Link href="/sign-up?role=client" className="btn btn-primary btn-lg">Post a project</Link>
              <Link href="/sign-up?role=designer" className="btn btn-secondary btn-lg">Apply as designer</Link>
            </div>
          </div>
        </section>

        {/* ── Footer ────────────────────────────────────────────────────── */}
        <footer style={{
          borderTop: '1px solid var(--border)',
          padding: '2.5rem 0',
          background: 'var(--bg-secondary)',
        }}>
          <div className="container-xl" style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
          }}>
            <span style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.125rem',
              fontWeight: 500,
              color: 'var(--text-primary)',
            }}>Lynvia</span>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              © 2026 Lynvia. India&apos;s creative marketplace.
            </p>
          </div>
        </footer>
      </main>
    </>
  )
}
