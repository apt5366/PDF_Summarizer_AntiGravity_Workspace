// components/section-builder.tsx
"use client"

import React, { useState, useMemo } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export type Section = {
  id: string
  title: string
  prompt?: string
}

interface SectionBuilderProps {
  rawDocType?: string | null
  themes?: string[] | null
  categories?: Array<{ key?: string; title?: string }> | null
  insights?: Array<{ title?: string }> | null
  initialSections?: Section[]
  onChange?: (sections: Section[]) => void
}

function uid() {
  return Math.random().toString(36).slice(2, 9)
}

/* ---------- Suggestions ---------- */

function makeSuggestions(
  rawDocType?: string | null,
  themes?: string[] | null
): Section[] {
  const t = (themes || []).map(x => x.toLowerCase())

  const base: Section[] = [
    {
      id: uid(),
      title: "Financial performance",
      prompt: "Revenue, margins, profitability, operating cash flow, key numbers."
    },
    {
      id: uid(),
      title: "Strategy & growth drivers",
      prompt: "Expansion plans, GTM, product roadmap, growth narrative."
    },
    {
      id: uid(),
      title: "Key metrics & ratios",
      prompt: "KPIs, ratios, operational metrics pulled out explicitly."
    },
    {
      id: uid(),
      title: "Management commentary",
      prompt: "Management tone, priorities, and strategic messaging."
    },
    {
      id: uid(),
      title: "Risks & considerations",
      prompt: "Material risks, uncertainties, and downside considerations."
    }
  ]

  return base
}

/* ---------- Component ---------- */

export function SectionBuilder({
  rawDocType,
  themes,
  initialSections = [],
  onChange
}: SectionBuilderProps) {
  const [sections, setSections] = useState<Section[]>(
    initialSections.length > 0
      ? initialSections
      : makeSuggestions(rawDocType, themes)
  )

  const pushChange = (next: Section[]) => {
    setSections(next)
    onChange?.(next)
  }

  const addSection = () => {
    pushChange([...sections, { id: uid(), title: "New section", prompt: "" }])
  }

  const removeSection = (id: string) => {
    pushChange(sections.filter(s => s.id !== id))
  }

  const update = (id: string, patch: Partial<Section>) => {
    pushChange(sections.map(s => (s.id === id ? { ...s, ...patch } : s)))
  }

  const move = (id: string, dir: -1 | 1) => {
    const idx = sections.findIndex(s => s.id === id)
    if (idx < 0) return
    const copy = [...sections]
    const target = idx + dir
    if (target < 0 || target >= copy.length) return
    ;[copy[idx], copy[target]] = [copy[target], copy[idx]]
    pushChange(copy)
  }

  const reset = () => {
    pushChange(makeSuggestions(rawDocType, themes))
  }

  return (
    <Card className="p-0 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold">Custom sections</h3>
          <p className="text-xs text-muted-foreground">
            These will be used to generate a structured executive summary.
          </p>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={reset}>
            Auto-suggest
          </Button>
          <Button size="sm" onClick={addSection}>
            Add
          </Button>
        </div>
      </div>

      {/* Scrollable body */}
      <div className="max-h-[420px] overflow-y-auto px-4 py-4 space-y-3">
        {sections.map((s, i) => (
          <div
            key={s.id}
            className="border rounded-md p-3 bg-background"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <div className="text-sm font-medium">
                  {i + 1}. {s.title}
                </div>

                <input
                  value={s.prompt || ""}
                  onChange={e => update(s.id, { prompt: e.target.value })}
                  placeholder="Section hint (optional)"
                  className="mt-2 w-full text-sm px-2 py-1 border rounded-md"
                />
              </div>

              <div className="flex flex-col gap-1">
                <Button size="icon" variant="outline" onClick={() => move(s.id, -1)}>↑</Button>
                <Button size="icon" variant="outline" onClick={() => move(s.id, 1)}>↓</Button>
                <Button size="icon" variant="destructive" onClick={() => removeSection(s.id)}>✕</Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
