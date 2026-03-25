import type { ReactNode } from 'react'

export const metadata = {
  title: 'Tasks Dashboard',
  description: 'Frontend for tasks and projects challenge',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, background: '#f6f8fb' }}>{children}</body>
    </html>
  )
}
