// components/upload-box.tsx
"use client"

import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { uploadDocument } from "@/lib/api"
import { useDocument } from "@/context/DocumentContext"
import { Button } from "@/components/ui/button"
import { ProcessingSteps } from "./processing-steps"

export function UploadBox() {
  const router = useRouter()
  const { setDocument, setIsLoading } = useDocument()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleUpload = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please upload a PDF file")
      return
    }

    setUploading(true)
    setError(null)
    setIsLoading(true)

    try {
  const data = await uploadDocument(file)

  if (data.status === "error") {
    throw new Error("Upload failed")
  }

  setDocument(data)
  router.push(`/document/${data.file_id}`)
} catch (err: any) {
  console.error(err)
  setError(err.message || "Upload failed. Please try again.")
  setIsLoading(false)
}
    setUploading(false)
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const files = e.dataTransfer.files
    if (files.length > 0 && !uploading) {
      handleUpload(files[0])
    }
  }

  return (
    <div className="flex flex-col items-center gap-6 w-full">
      {/* Upload Box */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => fileInputRef.current?.click()}
        className={`w-full max-w-md rounded-lg border-2 border-dashed p-12 text-center cursor-pointer transition-colors 
          ${uploading ? "border-primary bg-muted" : "border-border bg-card hover:border-primary hover:bg-muted"}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file && !uploading) handleUpload(file)
          }}
          className="hidden"
        />

        <div className="flex flex-col items-center gap-2">
          <div className="text-4xl text-muted-foreground">↑</div>

          <p className="font-medium text-foreground">
            {uploading ? "Processing..." : "Upload PDF"}
          </p>

          <p className="text-sm text-muted-foreground">
            {uploading
              ? "Analyzing and summarizing your document..."
              : "Drag and drop or click to browse"}
          </p>
        </div>
      </div>

      {/* Error message */}
      {error && <p className="text-sm text-red-500">{error}</p>}

      {/* Button */}
      <Button onClick={() => fileInputRef.current?.click()} disabled={uploading}>
        {uploading ? "Processing..." : "Select File"}
      </Button>

      {/* Harvey-style Processing UI */}
      {uploading && <ProcessingSteps />}
    </div>
  )
}
