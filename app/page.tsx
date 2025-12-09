// app/page.tsx
import { UploadBox } from "@/components/upload-box"

export const metadata = {
  title: "FinSummarizer - Document Analysis",
  description: "Upload and analyze financial documents with AI",
}

export default function Home() {
  return (
    <main className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-semibold text-foreground mb-2">FinSummarizer</h1>
          <p className="text-muted-foreground">
            Upload a PDF document for instant analysis
          </p>
        </div>
        <UploadBox />
      </div>
    </main>
  )
}
