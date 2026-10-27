import type { Metadata } from 'next'
import { AuthProvider } from '@/contexts/auth-context'
import { Providers } from '@/components/providers'
import './globals.css'

export const metadata: Metadata = {
  title: 'Lynvia — India\'s Creative Services Marketplace',
  description: 'Connect with top designers for logos, branding, posters, and social media design. Post your project and get proposals from vetted Indian designers.',
  keywords: ['design marketplace', 'India', 'logo design', 'branding', 'poster design', 'freelance design'],
  openGraph: {
    title: 'Lynvia — Creative Services Marketplace',
    description: 'India\'s premium marketplace for creative design work',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        <AuthProvider>
          <Providers>{children}</Providers>
        </AuthProvider>
      </body>
    </html>
  )
}
