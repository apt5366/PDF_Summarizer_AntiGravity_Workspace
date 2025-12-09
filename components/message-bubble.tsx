// components/message-bubble.tsx
import type { ChatMessage } from "@/types/api"

interface MessageBubbleProps {
  message: ChatMessage
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isQuestion = message.type === "question"

  return (
    <div className={`flex mb-4 ${isQuestion ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
          isQuestion ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
        }`}
      >
        <p className="text-sm break-words whitespace-pre-wrap">{message.content}</p>

        {message.excerpts && message.excerpts.length > 0 && (
          <div className="mt-2 text-xs space-y-1 border-t border-current border-opacity-20 pt-2 opacity-80">
            {message.excerpts.map((excerpt, idx) => {
              const preview =
                excerpt.excerpt.length > 160
                  ? `${excerpt.excerpt.slice(0, 157)}…`
                  : excerpt.excerpt

              return (
                <div key={idx}>
                  {typeof excerpt.page === "number" && (
                    <p className="font-medium">Page {excerpt.page}</p>
                  )}
                  <p className="opacity-90">{preview}</p>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
