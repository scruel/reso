import type { Metadata } from 'next'
import localFont from 'next/font/local'
import './globals.css'
import ErrorBoundary from '@/components/ErrorBoundary'

const inter = localFont({
  src: [
    {
      path: '../../public/fonts/inter-100.ttf',
      weight: '100',
      style: 'normal',
    },
    {
      path: '../../public/fonts/inter-200.ttf',
      weight: '200',
      style: 'normal',
    },
    {
      path: '../../public/fonts/inter-300.ttf',
      weight: '300',
      style: 'normal',
    },
    {
      path: '../../public/fonts/inter-400.ttf',
      weight: '400',
      style: 'normal',
    },
    {
      path: '../../public/fonts/inter-500.ttf',
      weight: '500',
      style: 'normal',
    },
    {
      path: '../../public/fonts/inter-600.ttf',
      weight: '600',
      style: 'normal',
    },
    {
      path: '../../public/fonts/inter-700.ttf',
      weight: '700',
      style: 'normal',
    },
    {
      path: '../../public/fonts/inter-800.ttf',
      weight: '800',
      style: 'normal',
    },
    {
      path: '../../public/fonts/inter-900.ttf',
      weight: '900',
      style: 'normal',
    },
  ],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'AI 精選購物 - 智能電商搜尋',
  description: '現代化的電商搜尋體驗，由 AI 精心策劃的購物介面',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body className={inter.className}>
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  )
}
