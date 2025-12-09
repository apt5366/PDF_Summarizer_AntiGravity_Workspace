import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import "./globals.css"
import { DocumentProvider } from "@/context/DocumentContext"
import { Analytics } from "@vercel/analytics/next"

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" })
const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-geist-mono" })

export const metadata: Metadata = {
  title: "FinSummarizer – AI Document Analysis",
  description: "Upload financial documents and receive instant AI-powered insights.",
    generator: 'v0.app'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${geist.variable} ${geistMono.variable} font-sans bg-background text-foreground`}>
        <DocumentProvider>
          {children}
        </DocumentProvider>
        <Analytics />
      </body>
    </html>
  )
}
