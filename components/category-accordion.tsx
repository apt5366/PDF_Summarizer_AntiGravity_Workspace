// components/category-accordion.tsx
"use client"

import { useState } from "react"
import type { DocumentCategory } from "@/types/api"
import { Card } from "@/components/ui/card"

interface CategoryAccordionProps {
  categories: DocumentCategory[]
}

export function CategoryAccordion({ categories }: CategoryAccordionProps) {
  const [expandedKey, setExpandedKey] = useState<string | null>(null)

  if (!categories || categories.length === 0) return null

  return (
    <div className="flex flex-col gap-3 mb-8">
      <h2 className="text-lg font-medium text-foreground">Document Analysis</h2>

      {categories.map((category) => {
        const shortPreview =
          category.summary.length > 80
            ? `${category.summary.slice(0, 77)}…`
            : category.summary

        return (
          <Card key={category.key} className="overflow-hidden">
            <button
              type="button"
              onClick={() =>
                setExpandedKey(expandedKey === category.key ? null : category.key)
              }
              className="w-full px-4 py-3 text-left hover:bg-muted transition-colors flex items-center justify-between"
            >
              <div>
                <h3 className="font-medium text-foreground">{category.title}</h3>
                <p className="text-xs text-muted-foreground mt-1">{shortPreview}</p>
              </div>
              <span className="text-muted-foreground ml-4 flex-shrink-0">
                {expandedKey === category.key ? "−" : "+"}
              </span>
            </button>

            {expandedKey === category.key && (
              <div className="px-4 py-3 border-t border-border bg-muted/30">
                <p className="text-sm text-foreground mb-3 whitespace-pre-wrap">
                  {category.summary}
                </p>

                {category.snippets && category.snippets.length > 0 && (
                  <div className="flex flex-col gap-2">
                    <p className="text-xs font-medium text-muted-foreground">
                      Supporting snippets:
                    </p>
                    {category.snippets.map((snippet, idx) => (
                      <div
                        key={idx}
                        className="text-xs bg-background p-2 rounded border border-border"
                      >
                        <p className="text-foreground mb-1">{snippet.text}</p>
                        {typeof snippet.page === "number" && (
                          <p className="text-muted-foreground">
                            Page {snippet.page}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </Card>
        )
      })}
    </div>
  )
}
