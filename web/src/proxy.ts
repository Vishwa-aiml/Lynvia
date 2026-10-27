import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/**
 * Lightweight proxy middleware — no Clerk, no Firebase Admin needed at edge.
 *
 * Strategy:
 *  - Public routes pass through unconditionally.
 *  - Protected routes check for the presence of an Authorization header or
 *    a __session cookie (set by the client after Firebase sign-in).
 *    Full JWT verification happens inside NestJS via firebase-admin.
 *    The middleware only provides a UX redirect — it is NOT a security boundary.
 */

const PUBLIC_PATHS = ['/', '/designers', '/sign-in', '/sign-up']

function isPublic(pathname: string) {
  return PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith(p + '/'))
}

export default function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Always allow public routes
  if (isPublic(pathname)) return NextResponse.next()

  // Allow Next.js internals and static assets
  if (pathname.startsWith('/_next') || pathname.startsWith('/favicon')) {
    return NextResponse.next()
  }

  // Check for a session indicator set by the client after Firebase sign-in
  const hasSession =
    request.cookies.has('__firebase_session') ||
    request.headers.has('authorization')

  if (!hasSession && pathname.startsWith('/dashboard')) {
    const signInUrl = new URL('/sign-in', request.url)
    signInUrl.searchParams.set('redirect_url', request.nextUrl.pathname)
    return NextResponse.redirect(signInUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}
