'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi, rupeesToPaise } from '@/lib/api'
import { useRouter } from 'next/navigation'
import axios from 'axios'

const schema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters').max(150),
  brief: z.string().min(30, 'Please describe your project in at least 30 characters').max(5000),
  category: z.enum(['logo_branding', 'poster_social']),
  budgetRupees: z.number().min(500, 'Minimum budget is ₹500').max(500000),
})

type PostProjectForm = z.infer<typeof schema>

export default function PostProjectPage() {
  const router = useRouter()
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<PostProjectForm>({
    resolver: zodResolver(schema),
    defaultValues: { category: 'logo_branding' },
  })

  const { mutate, isPending, error } = useMutation({
    mutationFn: (data: PostProjectForm) =>
      projectsApi.create({
        title: data.title,
        brief: data.brief,
        category: data.category,
        budgetPaise: rupeesToPaise(Number(data.budgetRupees)),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-projects'] })
      router.push('/dashboard/client')
    },
  })

  const budgetRupees = watch('budgetRupees')
  const category = watch('category')

  return (
    <div style={{ maxWidth: '640px' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 className="text-display-md" style={{ marginBottom: '0.5rem' }}>Post a project</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Describe what you need. Vetted designers will send you proposals.
        </p>
      </div>

      <form onSubmit={handleSubmit((data) => mutate(data))} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Category */}
        <div>
          <label className="field-label">Category *</label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            {[
              { value: 'logo_branding', label: 'Logo & Branding', icon: '◈' },
              { value: 'poster_social', label: 'Poster & Social', icon: '▦' },
            ].map((cat) => {
              const isSelected = category === cat.value
              return (
                <label key={cat.value} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.875rem 1rem',
                  border: `2px solid ${isSelected ? 'var(--accent)' : 'var(--border)'}`,
                  borderRadius: 'var(--radius-md)',
                  background: isSelected ? 'var(--accent-surface)' : 'var(--bg-elevated)',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                }}>
                  <input type="radio" value={cat.value} {...register('category')} style={{ display: 'none' }} />
                  <span style={{ color: 'var(--accent)', fontSize: '1.25rem' }}>{cat.icon}</span>
                  <span style={{ fontSize: '0.9375rem', fontWeight: isSelected ? 500 : 400 }}>{cat.label}</span>
                </label>
              )
            })}
          </div>
          {errors['category'] && <p className="field-error">{errors['category'].message as string}</p>}
        </div>

        {/* Title */}
        <div>
          <label className="field-label">Project title *</label>
          <input
            {...register('title')}
            className="input"
            placeholder="e.g. Logo for my photography studio"
          />
          {errors['title'] && <p className="field-error">{errors['title'].message as string}</p>}
        </div>

        {/* Brief */}
        <div>
          <label className="field-label">Project brief *</label>
          <textarea
            {...register('brief')}
            className="input textarea"
            style={{ minHeight: '160px' }}
            placeholder="Describe your project in detail. What's the purpose? Who's your audience? Do you have references or a specific style in mind? The more context you give, the better proposals you'll receive."
          />
          {errors['brief'] && <p className="field-error">{errors['brief'].message as string}</p>}
        </div>

        {/* Budget */}
        <div>
          <label className="field-label">Budget (₹) *</label>
          <div style={{ position: 'relative' }}>
            <span style={{
              position: 'absolute',
              left: '0.875rem',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-secondary)',
              fontWeight: 500,
            }}>₹</span>
            <input
              {...register('budgetRupees', { valueAsNumber: true })}
              type="number"
              className="input"
              style={{ paddingLeft: '1.75rem' }}
              placeholder="5000"
            />
          </div>
          {budgetRupees && !errors['budgetRupees'] && (
            <p className="text-sm" style={{ color: 'var(--text-muted)', marginTop: '0.375rem' }}>
              Designers receive 90% (₹{Math.floor(Number(budgetRupees) * 0.9).toLocaleString('en-IN')}). Platform fee 10%.
            </p>
          )}
          {errors['budgetRupees'] && <p className="field-error">{errors['budgetRupees'].message as string}</p>}
        </div>

        {error && (
          <p style={{ color: 'var(--error)', fontSize: '0.875rem' }}>
            {axios.isAxiosError(error) ? error.response?.data?.message ?? error.message : 'Something went wrong. Please try again.'}
          </p>
        )}

        <div style={{ display: 'flex', gap: '1rem', paddingTop: '0.5rem' }}>
          <button
            type="button"
            onClick={() => router.back()}
            className="btn btn-ghost"
          >
            Cancel
          </button>
          <button type="submit" disabled={isPending} className="btn btn-primary" style={{ flex: 1 }}>
            {isPending ? 'Posting...' : 'Post project →'}
          </button>
        </div>
      </form>
    </div>
  )
}
