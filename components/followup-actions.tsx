// components/followup-actions.tsx
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { followUpAction } from "@/lib/api"
import { useDocument } from "@/context/DocumentContext"
import type { AskResponse } from "@/types/api"

interface FollowupActionsProps {
  fileId: string
  actions: string[]
}

export function FollowupActions({ fileId, actions }: FollowupActionsProps) {
  const { addChatMessage } = useDocument()
  const [loading, setLoading] = useState<string | null>(null)

  const handleAction = async (action: string) => {
    if (loading) return
    setLoading(action)

    // 🔍 DEBUG LOG
    console.log("FOLLOWUP DEBUG → sending:", { fileId, action })

    // Show selected action in chat as user question
    addChatMessage({
      id: Date.now().toString(),
      type: "question",
      content: action,
      timestamp: new Date(),
    })

    try {
      const result: AskResponse = await followUpAction(fileId, action)

      if (result.status === "error") {
        addChatMessage({
          id: (Date.now() + 1).toString(),
          type: "answer",
          content: result.message || "The backend reported an error for this follow-up.",
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
      console.error("FOLLOWUP DEBUG → caught error:", err)
      addChatMessage({
        id: (Date.now() + 2).toString(),
        type: "answer",
        content: "Error running follow-up. Please try again.",
        timestamp: new Date(),
      })
    }

    setLoading(null)
  }

  if (!actions || actions.length === 0) return null

  return (
    <div className="flex flex-col gap-3 mb-8">
      <h2 className="text-lg font-medium text-foreground">Suggested Actions</h2>
      <div className="flex flex-col gap-2">
        {actions.map((action) => (
          <Button
            key={action}
            onClick={() => handleAction(action)}
            disabled={loading === action}
            variant="outline"
            className="justify-start h-auto py-2 px-4 text-sm"
          >
            {loading === action ? "Loading…" : action}
          </Button>
        ))}
      </div>
    </div>
  )
}
