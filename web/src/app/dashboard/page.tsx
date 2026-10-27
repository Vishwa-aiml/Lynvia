import { redirect } from 'next/navigation'

/**
 * /dashboard — simple entry point.
 * Auth guard and role-based redirect are handled by DashboardLayout.
 * This page just redirects to the client sub-route as a default;
 * the layout will redirect away if the user is a DESIGNER or ADMIN.
 */
export default function DashboardPage() {
  redirect('/dashboard/client')
}
