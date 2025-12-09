// components/chat-panel.tsx
"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { askQuestion } from "@/lib/api"
import { useDocument } from "@/context/DocumentContext"
import type { AskResponse } from "@/types/api"
import { MessageBubble } from "./message-bubble"

interface ChatPanelProps {
  fileId: string
}

export function ChatPanel({ fileId }: ChatPanelProps) {
  const { chatMessages, addChatMessage, isLoading } = useDocument()
  const [input, setInput] = useState("")
  const [sending, setSending] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [chatMessages])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || sending || isLoading) return

    const question = input.trim()
    setInput("")
    setSending(true)

    // 🔍 DEBUG LOG
    console.log("CHAT DEBUG → sending:", { fileId, question })

    // add user question to chat
    addChatMessage({
      id: Date.now().toString(),
      type: "question",
      content: question,
      timestamp: new Date(),
    })

    try {
      const result: AskResponse = await askQuestion(fileId, question)

      if (result.status === "error") {
        addChatMessage({
          id: (Date.now() + 1).toString(),
          type: "answer",
          content: result.message || "The backend reported an error answering this question.",
          timestamp: new Date(),
        })
      } else {
        addChatMessage({
          id: (Date.now() + 1).toString(),
          type: "answer",
          content: result.answer || "",
          excerpts: result.supporting_excerpts,
          timestamp: new Date(),
        })
      }
    } catch (err) {
      console.error("CHAT DEBUG → caught error:", err)
      addChatMessage({
        id: (Date.now() + 2).toString(),
        type: "answer",
        content: "Error processing question. Please try again.",
        timestamp: new Date(),
      })
    }

    setSending(false)
  }

  return (
    <Card className="h-full flex flex-col bg-card">
      <div className="px-4 py-3 border-b border-border">
        <h3 className="font-medium text-foreground">Ask Anything</h3>
        <p className="text-xs text-muted-foreground">
          Ask focused questions about this document.
        </p>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <p className="text-sm text-center">
              Start by asking something like:
              <br />
              <span className="italic">
                “What are the main risks?” or “Summarize financial performance.”
              </span>
            </p>
          </div>
        ) : (
          chatMessages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}
      </div>

      <form onSubmit={handleSend} className="border-t border-border p-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={isLoading ? "Document is still loading..." : "Ask a question..."}
          disabled={sending || isLoading}
          className="flex-1 px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <Button type="submit" disabled={sending || isLoading || !input.trim()} size="sm">
          {sending ? "Sending…" : "Send"}
        </Button>
      </form>
    </Card>
  )
}
