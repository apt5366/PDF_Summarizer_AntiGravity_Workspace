import { Card } from "@/components/ui/card"

interface ExecutiveSummaryCardProps {
  title: string
  docType: string
  summary: string
  themes: string[]
}

export function ExecutiveSummaryCard({ title, docType, summary, themes }: ExecutiveSummaryCardProps) {
  return (
    <div className="flex flex-col gap-4 mb-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-foreground">{title}</h1>
        <p className="text-sm text-muted-foreground">{docType}</p>
      </div>

      <Card className="p-4">
        <h2 className="text-lg font-medium text-foreground mb-3">Executive Summary</h2>
        <p className="text-sm leading-relaxed text-foreground">{summary}</p>
      </Card>

      {themes.length > 0 && (
        <div className="flex flex-col gap-2">
          <h3 className="text-sm font-medium text-foreground">Key Themes</h3>
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
