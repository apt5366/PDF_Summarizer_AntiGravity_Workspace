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
import { SectionBuilder, type Section } from "@/components/section-builder"

import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion"

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

  // Custom section builder state
  const [sections, setSections] = useState<Section[]>([])

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
    if (sections.length > 0) return
    setSelectedFocus((prev) =>
      prev.includes(key)
        ? prev.filter((k) => k !== key)
        : [...prev, key]
    )
  }

  // --------------------------------------------------
  // Build priorities (sections only)
  // --------------------------------------------------
  const buildPriorities = (): string[] => {
    const out: string[] = []

    if (sections.length > 0) {
      sections.forEach((s, idx) => {
        const header = `SECTION ${idx + 1}: ${s.title}`
        if (s.prompt?.trim()) {
          out.push(`${header} — ${s.prompt.trim()}`)
        } else {
          out.push(header)
        }
      })
    } else {
      if (selectedFocus.includes("risks"))
        out.push("Risks, mitigations, downside scenarios")
      if (selectedFocus.includes("financials"))
        out.push("Revenue, margins, profitability, cash flow")
      if (selectedFocus.includes("strategy"))
        out.push("Strategy, growth drivers, roadmap, expansion plans")
      if (selectedFocus.includes("management"))
        out.push("Management commentary, tone, key messages")
      if (selectedFocus.includes("metrics"))
        out.push("Key metrics, KPIs, ratios, operational numbers")
    }

    return out
  }

  // --------------------------------------------------
  // Generate summary
  // --------------------------------------------------
  const handleGenerateSummary = async () => {
    if (!document.full_text) return

    setIsSummarizing(true)
    setSummaryError(null)

    const payload: SummarizeOptions = {
      text: document.full_text,
      priorities: buildPriorities(),
      format,
      depth,
    }

    try {
      const result = await refineSummary(payload)

      if (result.status === "error") {
        setSummaryError(result.message || "Could not generate summary.")
      } else {
        setCustomSummary(result.narrative)
      }
    } catch (err) {
      console.error("Error generating summary:", err)
      setSummaryError("Unexpected error while generating summary.")
    } finally {
      setIsSummarizing(false)
    }
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="flex h-screen">

        {/* LEFT PANEL */}
        <div className="flex-1 overflow-y-auto p-8 border-r border-border">
          <div className="space-y-6">

            {/* HEADER */}
            <div>
              <h1 className="text-2xl font-bold">
                Executive Summary Structure
              </h1>
              <p className="text-muted-foreground mt-1">
                Customize the structure and content of the executive summary.
              </p>
            </div>

            {/* SECTION BUILDER (NON-COLLAPSIBLE) */}
            <Card className="p-6">
              <div className="mb-3">
                <h2 className="text-lg font-semibold">Custom sections</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Define the exact structure of the executive summary.
                </p>
              </div>

              <SectionBuilder
                rawDocType={
                  document.raw_doc_type ?? document.doc_type ?? null
                }
                themes={document.themes ?? []}
                categories={document.categories as any}
                insights={document.key_insights as any}
                initialSections={[]}
                onChange={setSections}
              />
            </Card>

            {/* CONTROLS */}
            <Card className="p-6 space-y-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-xl font-semibold">
                    What do you want from this document?
                  </h2>
                  <p className="text-sm text-muted-foreground mt-1">
                    Build a tailored summary based on your selected sections.
                  </p>
                </div>
                <div className="hidden md:block text-xs text-muted-foreground">
                  {document.raw_doc_type &&
                    `Detected: ${document.raw_doc_type}`}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
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
                  <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
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
                  <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Depth
                  </label>
                  <select
                    className="border border-border rounded-md px-2 py-1 text-sm bg-background"
                    value={depth}
                    onChange={(e) =>
                      setDepth(
                        e.target.value as "quick" | "medium" | "deep"
                      )
                    }
                  >
                    <option value="quick">Quick skim</option>
                    <option value="medium">Standard</option>
                    <option value="deep">Deep dive</option>
                  </select>
                </div>
              </div>

              {summaryError && (
                <p className="text-xs text-red-500 mt-2">
                  {summaryError}
                </p>
              )}

              <div className="flex items-center justify-between mt-4">
                <div className="text-xs text-muted-foreground">
                  We won’t generate the summary until you confirm.
                </div>
                <Button
                  onClick={handleGenerateSummary}
                  disabled={isSummarizing}
                  size="sm"
                >
                  {isSummarizing
                    ? "Generating…"
                    : "Generate tailored summary"}
                </Button>
              </div>
            </Card>

            {/* SUMMARY */}
            {customSummary ? (
              <ExecutiveSummaryCard
                title={document.file_name ?? ""}
                docType={
                  document.doc_type_display ??
                  document.doc_type ??
                  ""
                }
                summary={customSummary}
                themes={document.themes ?? []}
              />
            ) : (
              <Card className="p-4">
                <p className="text-sm text-muted-foreground">
                  No summary generated yet. Configure your settings above
                  and click{" "}
                  <span className="font-medium">
                    Generate tailored summary
                  </span>.
                </p>
              </Card>
            )}

            {/* INSIGHTS (COLLAPSIBLE) */}
            {document.key_insights?.length > 0 && (
              <Accordion type="single" collapsible>
                <AccordionItem value="insights">
                  <AccordionTrigger className="text-lg font-semibold">
                    Key insights
                  </AccordionTrigger>
                  <AccordionContent>
                    <InsightList insights={document.key_insights} />
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            )}

            {/* CATEGORIES */}
            {document.categories?.length > 0 && (
              <CategoryAccordion categories={document.categories} />
            )}

            <FollowupActions
              fileId={fileId}
              actions={document.follow_up_actions ?? []}
            />
          </div>
        </div>

        {/* RIGHT CHAT */}
        <div className="w-96 bg-card border-l border-border flex flex-col">
          <ChatPanel fileId={fileId} />
        </div>
      </div>
    </main>
  )
}
