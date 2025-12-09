// context/DocumentContext.tsx
"use client"

import type React from "react"
import { createContext, useContext, useState } from "react"
import type { UploadResponse, ChatMessage } from "@/types/api"

interface DocumentContextType {
  document: UploadResponse | null
  setDocument: (doc: UploadResponse) => void
  chatMessages: ChatMessage[]
  addChatMessage: (message: ChatMessage) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined)

export function DocumentProvider({ children }: { children: React.ReactNode }) {
  const [document, setDocumentState] = useState<UploadResponse | null>(null)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const setDocument = (doc: UploadResponse) => {
    setDocumentState(doc)
    // reset chat thread when a new document is loaded
    setChatMessages([])
  }

  const addChatMessage = (message: ChatMessage) => {
    setChatMessages((prev) => [...prev, message])
  }

  return (
    <DocumentContext.Provider
      value={{
        document,
        setDocument,
        chatMessages,
        addChatMessage,
        isLoading,
        setIsLoading,
      }}
    >
      {children}
    </DocumentContext.Provider>
  )
}

export function useDocument() {
  const context = useContext(DocumentContext)
  if (!context) {
    throw new Error("useDocument must be used within DocumentProvider")
  }
  return context
}
