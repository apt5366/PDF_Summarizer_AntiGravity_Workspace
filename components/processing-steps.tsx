// components/processing-steps.tsx

export function ProcessingSteps() {
  const steps = [
    "Analyzing document structure...",
    "Identifying key sections and topics...",
    "Extracting financial signals and metrics...",
    "Generating executive summary...",
    "Preparing follow-up questions...",
  ]

  return (
    <div className="mt-8 w-full max-w-xl mx-auto rounded-xl border border-border bg-card/80 shadow-sm p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
          <span className="text-xl">⚙️</span>
        </div>
        <div>
          <p className="text-sm font-medium text-foreground">Processing your document…</p>
          <p className="text-xs text-muted-foreground">
            This usually takes a short while. You can see what the AI is working on below.
          </p>
        </div>
      </div>

      <div className="space-y-2">
        {steps.map((step, idx) => (
          <div key={step} className="flex items-center gap-2 text-sm">
            <span className="h-2 w-2 rounded-full bg-primary animate-pulse" />
            <span className="text-muted-foreground">{step}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
