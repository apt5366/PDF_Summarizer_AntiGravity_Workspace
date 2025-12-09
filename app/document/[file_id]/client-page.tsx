"use client"

import { useEffect } from "react"
import { useDocument } from "@/context/DocumentContext"
import { ExecutiveSummaryCard } from "@/components/executive-summary-card"
import { CategoryAccordion } from "@/components/category-accordion"
import { InsightList } from "@/components/insight-list"
import { FollowupActions } from "@/components/followup-actions"
import { ChatPanel } from "@/components/chat-panel"

interface ClientPageProps {
  fileId: string
}

export function DocumentClientPage({ fileId }: ClientPageProps) {
  const { document, setIsLoading } = useDocument()

  // Document already loaded via upload → just stop loading spinner
  useEffect(() => {
    setIsLoading(false)
  }, [setIsLoading])

  if (!document) {
    return (
      <main className="min-h-screen bg-background">
        <div className="h-screen flex items-center justify-center">
          <p className="text-muted-foreground">Loading document...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="flex h-screen">
        {/* LEFT MAIN PANEL */}
        <div className="flex-1 overflow-y-auto p-8 border-r border-border">
          <ExecutiveSummaryCard
            title={document.file_name ?? ""}
            docType={document.doc_type_display ?? ""}
            summary={document.executive_summary ?? ""}
            themes={document.themes ?? []}
          />

          <InsightList insights={document.key_insights ?? []} />

          <CategoryAccordion categories={document.categories ?? []} />

          <FollowupActions fileId={fileId} actions={document.follow_up_actions ?? []} />
        </div>

        {/* RIGHT ASIDE PANEL */}
        <div className="w-96 bg-card border-l border-border flex flex-col">
          <ChatPanel fileId={fileId} />
        </div>
      </div>
    </main>
  )
}
