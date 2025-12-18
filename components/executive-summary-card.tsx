import { Card } from "@/components/ui/card"

interface ExecutiveSummaryCardProps {
  title: string
  docType: string
  summary: string
  themes: string[]
}

/**
 * Improved Executive Summary Card:
 * - Full-width readability
 * - Better spacing for multi-section outputs
 * - Recognizes section titles and bolds them
 * - Supports bullets, paragraphs, etc.
 */
export function ExecutiveSummaryCard({
  title,
  docType,
  summary,
  themes,
}: ExecutiveSummaryCardProps) {
  // Split summary into paragraphs or bullet blocks
  const sections = summary
    .split(/\n{2,}/) // break on blank lines
    .map((s) => s.trim())
    .filter(Boolean)

  const renderParagraph = (text: string, idx: number) => {
    const isHeader =
      /^[A-Za-z].*[:：]$/.test(text) || // ends with colon
      text.length < 60 && text === text.toUpperCase() // uppercase short headers

    return (
      <div key={idx} className="mb-4">
        {isHeader ? (
          <h3 className="font-semibold text-foreground mb-1">{text.replace(/[:：]$/, "")}</h3>
        ) : text.startsWith("-") || text.startsWith("•") ? (
          <ul className="list-disc list-inside space-y-1">
            {text
              .split(/\n+/)
              .map((line, i) => line.replace(/^[-•]\s*/, ""))
              .map((item, j) => (
                <li key={j} className="text-sm leading-relaxed">
                  {item}
                </li>
              ))}
          </ul>
        ) : (
          <p className="text-sm leading-relaxed whitespace-pre-line">{text}</p>
        )}
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6 w-full mb-12">
      {/* Title Block */}
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">{title}</h1>
        <p className="text-sm text-muted-foreground">{docType}</p>
      </div>

      {/* Summary Block */}
      <Card className="p-6 shadow-md border rounded-xl">
        <h2 className="text-xl font-semibold mb-4">Executive Summary</h2>

        <div className="space-y-4">
          {sections.length > 0
            ? sections.map((p, i) => renderParagraph(p, i))
            : (
              <p className="text-sm text-muted-foreground">
                No summary available.
              </p>
            )}
        </div>
      </Card>

      {/* Themes */}
      {themes.length > 0 && (
        <div className="flex flex-col gap-2">
          <h3 className="text-sm font-medium">Key Themes</h3>
          <div className="flex flex-wrap gap-2">
            {themes.map((theme) => (
              <span
                key={theme}
                className="px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-xs font-medium"
              >
                {theme}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
