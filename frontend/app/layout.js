import './globals.css'

export const metadata = {
  title: 'Startup Pitch Analyzer',
  description: 'Frontend (Next.js) calls FastAPI backend',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
