import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:3001/api'

export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

/**
 * Attach auth Bearer token to every request.
 * Call this in a client component or auth hook when session token changes.
 */
export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

// ─── Typed API helpers ───────────────────────────────────────────────────────

export const authApi = {
  me: () => api.get('/auth/me').then((r) => r.data),
  onboard: (data: { role: 'CLIENT' | 'DESIGNER'; name: string; bio?: string }) =>
    api.post('/auth/onboarding', data).then((r) => r.data),
}

export const projectsApi = {
  list: () => api.get('/projects').then((r) => r.data),
  mine: () => api.get('/projects/mine').then((r) => r.data),
  get: (id: string) => api.get(`/projects/${id}`).then((r) => r.data),
  create: (data: {
    title: string
    brief: string
    category: string
    budgetPaise: number
  }) => api.post('/projects', data).then((r) => r.data),
  acceptProposal: (projectId: string, proposalId: string) =>
    api.patch(`/projects/${projectId}/accept-proposal/${proposalId}`).then((r) => r.data),
}

export const proposalsApi = {
  create: (data: {
    projectId: string
    bidPaise: number
    deliveryDays: number
    coverNote?: string
  }) => api.post('/proposals', data).then((r) => r.data),
  mine: () => api.get('/proposals/mine').then((r) => r.data),
  forProject: (projectId: string) =>
    api.get(`/proposals/for-project/${projectId}`).then((r) => r.data),
}

export const designersApi = {
  list: () => api.get('/designers').then((r) => r.data),
  get: (userId: string) => api.get(`/designers/${userId}`).then((r) => r.data),
  portfolio: (userId: string) =>
    api.get(`/designers/${userId}/portfolio`).then((r) => r.data),
  getUploadUrl: (filename: string, contentType: string) =>
    api.post('/designers/portfolio/upload-url', { filename, contentType }).then((r) => r.data),
  confirmUpload: (s3Key: string) =>
    api.post('/designers/portfolio/confirm', { s3Key }).then((r) => r.data),
  // Admin
  pendingDesigners: () => api.get('/designers/admin/pending').then((r) => r.data),
  updateVetting: (userId: string, status: 'APPROVED' | 'REJECTED', note?: string) =>
    api.patch(`/designers/admin/${userId}/vetting`, { status, note }).then((r) => r.data),
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Convert INR rupees (number) to paise (integer). Always floor. */
export const rupeesToPaise = (rupees: number): number => Math.floor(rupees * 100)

/** Convert paise (integer) to INR string. */
export const paiseToRupees = (paise: number): string =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', minimumFractionDigits: 0 })
    .format(paise / 100)
