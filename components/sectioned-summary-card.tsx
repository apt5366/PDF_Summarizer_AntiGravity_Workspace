// components/sectioned-summary-card.tsx
import { Card } from "@/components/ui/card"

interface SectionedSummaryCardProps {
  sections: Record<string, string>
}

export function SectionedSummaryCard({ sections }: SectionedSummaryCardProps) {
  const keys = Object.keys(sections)

  return (
    <div className="flex flex-col gap-6 mb-10">
      {keys.map((title, idx) => (
        <Card key={idx} className="p-6">
          <h2 className="text-lg font-semibold text-foreground mb-3">
            {title}
          </h2>

          <div className="text-sm whitespace-pre-wrap leading-relaxed text-foreground">
            {sections[title]}
          </div>
        </Card>
      ))}
    </div>
  )
}
