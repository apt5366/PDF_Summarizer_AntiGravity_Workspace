import type { KeyInsight } from "@/types/api"
import { Card } from "@/components/ui/card"

interface InsightListProps {
  insights: KeyInsight[]
}

export function InsightList({ insights }: InsightListProps) {
  return (
    <div className="flex flex-col gap-3 mb-8">
      <h2 className="text-lg font-medium text-foreground">Key Insights</h2>
      <div className="flex flex-col gap-3">
        {insights.map((insight, idx) => (
          <Card key={idx} className="p-4">
            <h3 className="font-medium text-foreground mb-2">{insight.title}</h3>
            <p className="text-sm text-foreground mb-2">{insight.summary}</p>
            <div className="bg-muted p-2 rounded text-xs text-muted-foreground mb-2">
              <p>{insight.source_excerpt}</p>
            </div>
            <p className="text-xs font-medium text-muted-foreground">Page {insight.page}</p>
          </Card>
        ))}
      </div>
    </div>
  )
}
