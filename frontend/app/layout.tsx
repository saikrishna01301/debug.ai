import './globals.css'

export const metadata = {
  title: 'DebugAI',
  description: 'DebugAI Application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="gradient-bg">{children}</body>
    </html>
  )
}