// types/api.ts
// ------------------------------------------------------------
// Strong TypeScript definitions for backend API responses
// ------------------------------------------------------------

export interface DocumentCategory {
  key: string
  title: string
  summary: string
  snippets: Array<{
    text: string
    page: number | null
  }>
}

export interface KeyInsight {
  title: string
  summary: string
  source_excerpt: string
  page?: number | null // optional (backend sometimes attaches page)
}

// Not used directly yet (backend returns string[]), but kept for future
export interface FollowUpAction {
  action: string
}

export interface UploadResponse {
  status: "success" | "error"
  file_id: string
  file_name: string
  raw_doc_type: string

  // Some backends send doc_type, some doc_type_display — we support both
  doc_type?: string
  doc_type_display?: string

  quick_preview: string
  executive_summary: string
  categories: DocumentCategory[]
  key_insights: KeyInsight[]
  follow_up_actions: string[]
  themes: string[]
  full_text: string

  // Optional across all responses:
  message?: string
}

// ------------------------------------------------------------
// Ask response for /ask and /followup
// ------------------------------------------------------------

export interface AskResponse {
  status: "success" | "error"

  // Success fields
  answer?: string
  supporting_excerpts?: Array<{
    excerpt: string
    page: number | null
  }>

  // Error case (backend sends message)
  message?: string
}

// ------------------------------------------------------------
// Chat message for frontend chat panel
// ------------------------------------------------------------
export interface ChatMessage {
  id: string
  type: "question" | "answer"
  content: string
  excerpts?: Array<{
    excerpt: string
    page: number | null
  }>
  timestamp: Date
}
