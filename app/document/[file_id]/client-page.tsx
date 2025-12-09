// app/document/[file_id]/client-page.tsx
"use client"

import { useEffect, useState } from "react"
import { useDocument } from "@/context/DocumentContext"
import { ExecutiveSummaryCard } from "@/components/executive-summary-card"
import { CategoryAccordion } from "@/components/category-accordion"
import { InsightList } from "@/components/insight-list"
import { FollowupActions } from "@/components/followup-actions"
import { ChatPanel } from "@/components/chat-panel"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { refineSummary, type SummarizeOptions } from "@/lib/api"

interface ClientPageProps {
  fileId: string
}

type FocusKey =
  | "risks"
  | "financials"
  | "strategy"
  | "management"
  | "metrics"

export function DocumentClientPage({ fileId }: ClientPageProps) {
  const { document, setIsLoading } = useDocument()

  const [selectedFocus, setSelectedFocus] = useState<FocusKey[]>([
    "risks",
    "financials",
  ])
  const [audience, setAudience] = useState<string>("banker")
  const [format, setFormat] = useState<"bullets" | "narrative">("bullets")
  const [depth, setDepth] = useState<"quick" | "medium" | "deep">("medium")
  const [customSummary, setCustomSummary] = useState<string | null>(null)
  const [isSummarizing, setIsSummarizing] = useState(false)
  const [summaryError, setSummaryError] = useState<string | null>(null)

  // PDF is already uploaded + analyzed → stop the global loading spinner
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

  const handleToggleFocus = (key: FocusKey) => {
    setSelectedFocus((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    )
  }

  const handleGenerateSummary = async () => {
    if (!document.full_text) return
    setIsSummarizing(true)
    setSummaryError(null)

    // Map focus keys → human-readable priorities for backend
    const priorities: string[] = []

    if (selectedFocus.includes("risks")) {
      priorities.push("Risks, mitigations, downside scenarios")
    }
    if (selectedFocus.includes("financials")) {
      priorities.push("Revenue, margins, profitability, cash flow")
    }
    if (selectedFocus.includes("strategy")) {
      priorities.push("Strategy, growth drivers, roadmap, expansion plans")
    }
    if (selectedFocus.includes("management")) {
      priorities.push("Management commentary, tone, key messages")
    }
    if (selectedFocus.includes("metrics")) {
      priorities.push("Key metrics, KPIs, ratios, operational numbers")
    }

    // Encode audience as an extra “soft” priority
    if (audience) {
      priorities.push(`Write this for a ${audience} who is skimming quickly.`)
    }

    const payload: SummarizeOptions = {
      text: document.full_text,
      priorities,
      format,
      depth,
    }

    try {
      const result = await refineSummary(payload)

      if (result.status === "error" || !result.summary) {
        setSummaryError(
          result.message || "Could not generate summary. Please try again."
        )
        return
      }

      setCustomSummary(result.summary)
    } catch (err) {
      console.error("Error generating refined summary:", err)
      setSummaryError("Unexpected error while generating summary.")
    } finally {
      setIsSummarizing(false)
    }
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="flex h-screen">
        {/* LEFT MAIN PANEL */}
        <div className="flex-1 overflow-y-auto p-8 border-r border-border space-y-8">
          {/* 1) Guided Summary Builder */}
          <Card className="p-6 space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h1 className="text-xl font-semibold text-foreground">
                  What do you want from this document?
                </h1>
                <p className="text-sm text-muted-foreground mt-1">
                  We&apos;ll generate a tailored summary based on your current
                  needs. This is exactly the “define your schema & constraints”
                  step your employer described.
                </p>
              </div>
              <div className="hidden md:block text-xs text-muted-foreground">
                {document.raw_doc_type
                  ? `Detected: ${document.raw_doc_type}`
                  : ""}
              </div>
            </div>

            {/* Focus areas */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
              <button
                type="button"
                onClick={() => handleToggleFocus("risks")}
                className={`text-left border rounded-lg px-3 py-2 text-sm transition ${
                  selectedFocus.includes("risks")
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/60"
                }`}
              >
                <div className="font-medium">Risks & downsides</div>
                <div className="text-xs text-muted-foreground">
                  All material risks, risk factors and mitigations.
                </div>
              </button>

              <button
                type="button"
                onClick={() => handleToggleFocus("financials")}
                className={`text-left border rounded-lg px-3 py-2 text-sm transition ${
                  selectedFocus.includes("financials")
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/60"
                }`}
              >
                <div className="font-medium">Financial performance</div>
                <div className="text-xs text-muted-foreground">
                  Revenue, margins, profitability, cash flow.
                </div>
              </button>

              <button
                type="button"
                onClick={() => handleToggleFocus("strategy")}
                className={`text-left border rounded-lg px-3 py-2 text-sm transition ${
                  selectedFocus.includes("strategy")
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/60"
                }`}
              >
                <div className="font-medium">Strategy & growth drivers</div>
                <div className="text-xs text-muted-foreground">
                  Expansion plans, GTM, product roadmap, growth narrative.
                </div>
              </button>

              <button
                type="button"
                onClick={() => handleToggleFocus("management")}
                className={`text-left border rounded-lg px-3 py-2 text-sm transition ${
                  selectedFocus.includes("management")
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/60"
                }`}
              >
                <div className="font-medium">Management commentary</div>
                <div className="text-xs text-muted-foreground">
                  CEO / management tone, key messages, soft signals.
                </div>
              </button>

              <button
                type="button"
                onClick={() => handleToggleFocus("metrics")}
                className={`text-left border rounded-lg px-3 py-2 text-sm transition ${
                  selectedFocus.includes("metrics")
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/60"
                }`}
              >
                <div className="font-medium">Key metrics & ratios</div>
                <div className="text-xs text-muted-foreground">
                  KPIs, ratios, operational metrics pulled out explicitly.
                </div>
              </button>
            </div>

            {/* Audience + format + depth */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  Audience
                </label>
                <select
                  className="border border-border rounded-md px-2 py-1 text-sm bg-background"
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                >
                  <option value="banker">Banker</option>
                  <option value="equity analyst">Equity analyst</option>
                  <option value="wealth manager">Wealth manager</option>
                  <option value="vc">VC / investor</option>
                  <option value="general">General business reader</option>
                </select>
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  Style
                </label>
                <select
                  className="border border-border rounded-md px-2 py-1 text-sm bg-background"
                  value={format}
                  onChange={(e) =>
                    setFormat(e.target.value as "bullets" | "narrative")
                  }
                >
                  <option value="bullets">Bullet points</option>
                  <option value="narrative">Narrative</option>
                </select>
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  Depth
                </label>
                <select
                  className="border border-border rounded-md px-2 py-1 text-sm bg-background"
                  value={depth}
                  onChange={(e) =>
                    setDepth(e.target.value as "quick" | "medium" | "deep")
                  }
                >
                  <option value="quick">Quick skim (4–6 points)</option>
                  <option value="medium">Standard (8–12 points)</option>
                  <option value="deep">Deep dive</option>
                </select>
              </div>
            </div>

            {summaryError && (
              <p className="text-xs text-red-500 mt-2">{summaryError}</p>
            )}

            <div className="flex items-center justify-between mt-4">
              <div className="text-xs text-muted-foreground">
                We won&apos;t generate the executive summary until you confirm
                what matters. No decision anxiety, but you stay in control.
              </div>
              <Button
                onClick={handleGenerateSummary}
                disabled={isSummarizing}
                size="sm"
              >
                {isSummarizing ? "Generating…" : "Generate tailored summary"}
              </Button>
            </div>
          </Card>

          {/* 2) Tailored Executive Summary */}
          {customSummary ? (
            <ExecutiveSummaryCard
              title={document.file_name ?? ""}
              docType={document.doc_type_display ?? document.doc_type ?? ""}
              summary={customSummary}
              themes={document.themes ?? []}
            />
          ) : (
            <Card className="p-4">
              <p className="text-sm text-muted-foreground">
                No summary generated yet. Choose your focus and click{" "}
                <span className="font-medium">Generate tailored summary</span>{" "}
                above.{" "}
                {document.quick_preview && (
                  <>
                    <br />
                    <span className="mt-2 block text-xs">
                      Initial preview: {document.quick_preview}
                    </span>
                  </>
                )}
              </p>
            </Card>
          )}

          {/* 3) Key Insights & Categories – moved after summary to reduce initial overwhelm */}
          {document.key_insights && document.key_insights.length > 0 && (
            <InsightList insights={document.key_insights} />
          )}

          {document.categories && document.categories.length > 0 && (
            <CategoryAccordion categories={document.categories} />
          )}

          {/* 4) Suggested follow-up actions */}
          <FollowupActions
            fileId={fileId}
            actions={document.follow_up_actions ?? []}
          />
        </div>

        {/* RIGHT ASIDE PANEL – Chat stays as is */}
        <div className="w-96 bg-card border-l border-border flex flex-col">
          <ChatPanel fileId={fileId} />
        </div>
      </div>
    </main>
  )
}
