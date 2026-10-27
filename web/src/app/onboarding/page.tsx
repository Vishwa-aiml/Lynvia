'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { authApi } from '@/lib/api'
import { AuthTokenSync } from '@/components/auth-token-sync'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

const schema = z.object({
  role: z.enum(['CLIENT', 'DESIGNER']),
  name: z.string().min(2, 'Name is required').max(100),
  bio: z.string().max(500).optional(),
})

type FormData = z.infer<typeof schema>

export default function OnboardingPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [step, setStep] = useState<'role' | 'profile'>('role')
  const [selectedRole, setSelectedRole] = useState<'CLIENT' | 'DESIGNER' | null>(null)

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const { mutate, isPending, error } = useMutation({
    mutationFn: authApi.onboard,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['me'] })
      router.push(data.role === 'CLIENT' ? '/dashboard/client' : '/dashboard/designer')
    },
  })

  const selectRole = (role: 'CLIENT' | 'DESIGNER') => {
    setSelectedRole(role)
    setValue('role', role)
    setStep('profile')
  }

  return (
    <>
      <AuthTokenSync />
      <div style={{
        minHeight: '100vh',
        background: 'var(--bg-primary)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
      }}>
        <div style={{ width: '100%', maxWidth: '520px' }}>
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <p style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.5rem',
              fontWeight: 600,
              color: 'var(--text-primary)',
              marginBottom: '0.5rem',
            }}>Lynvia</p>
            <h1 className="text-display-md" style={{ marginBottom: '0.75rem' }}>
              {step === 'role' ? 'How will you use Lynvia?' : 'Tell us about yourself'}
            </h1>
            <p style={{ color: 'var(--text-secondary)' }}>
              {step === 'role'
                ? 'Choose your role — you can only pick one.'
                : `Setting up your ${selectedRole?.toLowerCase()} profile.`}
            </p>
          </div>

          {step === 'role' ? (
            /* Step 1: Role selection */
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              {[
                {
                  role: 'CLIENT' as const,
                  icon: '◈',
                  title: 'I need design work',
                  desc: 'Post projects and hire vetted designers',
                },
                {
                  role: 'DESIGNER' as const,
                  icon: '✦',
                  title: 'I am a designer',
                  desc: 'Submit proposals and get paid for your work',
                },
              ].map((item) => (
                <button
                  key={item.role}
                  onClick={() => selectRole(item.role)}
                  style={{
                    background: 'var(--bg-elevated)',
                    border: `2px solid ${selectedRole === item.role ? 'var(--accent)' : 'var(--border)'}`,
                    borderRadius: 'var(--radius-lg)',
                    padding: '2rem 1.5rem',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all var(--transition-base)',
                    boxShadow: 'var(--shadow-sm)',
                  }}
                >
                  <span style={{ fontSize: '2rem', display: 'block', marginBottom: '1rem', color: 'var(--accent)' }}>
                    {item.icon}
                  </span>
                  <strong style={{ display: 'block', marginBottom: '0.5rem', fontFamily: 'var(--font-display)', fontSize: '1rem' }}>
                    {item.title}
                  </strong>
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{item.desc}</span>
                </button>
              ))}
            </div>
          ) : (
            /* Step 2: Profile details */
            <form onSubmit={handleSubmit((data) => mutate(data))} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div className="card" style={{ marginBottom: '0' }}>
                <div style={{ marginBottom: '1.25rem' }}>
                  <label className="field-label">Full name *</label>
                  <input {...register('name')} className="input" placeholder="Your name" />
                  {errors.name && <p className="field-error">{errors.name.message}</p>}
                </div>

                <div>
                  <label className="field-label">Bio <span style={{ fontWeight: 400, color: 'var(--text-muted)' }}>(optional)</span></label>
                  <textarea
                    {...register('bio')}
                    className="input textarea"
                    placeholder={selectedRole === 'DESIGNER'
                      ? 'Briefly describe your design experience and specialisations...'
                      : 'What do you do? What kind of projects do you bring to Lynvia?'}
                  />
                  {errors.bio && <p className="field-error">{errors.bio.message}</p>}
                </div>
              </div>

              {error && (
                <p style={{ color: 'var(--error)', fontSize: '0.875rem' }}>
                  {(error as any).response?.data?.message ?? 'Something went wrong. Please try again.'}
                </p>
              )}

              <div style={{ display: 'flex', gap: '1rem' }}>
                <button type="button" onClick={() => setStep('role')} className="btn btn-ghost">
                  ← Back
                </button>
                <button type="submit" disabled={isPending} className="btn btn-primary" style={{ flex: 1 }}>
                  {isPending ? 'Setting up...' : 'Complete setup →'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </>
  )
}
