// lib/api.ts
import type { UploadResponse, AskResponse } from "@/types/api"

const API_BASE = "http://localhost:8000"

/**
 * Unified JSON handler.
 * Never throw except on network failures.
 * Always return normalized error structure.
 */
async function safeJSON(response: Response) {
  let json: any = {}

  try {
    json = await response.json()
  } catch {
    return {
      status: "error",
      message: "Invalid JSON received from backend.",
    }
  }

  if (!response.ok) {
    return {
      status: "error",
      message: json?.message ?? json?.detail ?? "Server reported an error.",
    }
  }

  return json
}

// --------------------------------------------------
// Upload PDF
// --------------------------------------------------
export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append("file", file)

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  })

  return safeJSON(res)
}

// --------------------------------------------------
// Ask question (/ask)
// --------------------------------------------------
export async function askQuestion(
  fileId: string,
  question: string
): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ file_id: fileId, question }),
  })

  return safeJSON(res)
}

// --------------------------------------------------
// Follow-up (/followup)
// --------------------------------------------------
export async function followUpAction(
  fileId: string,
  action: string
): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/followup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ file_id: fileId, action }),
  })

  return safeJSON(res)
}

// --------------------------------------------------
// Structured summarization (/summarize)
// --------------------------------------------------

export interface SummarizeOptions {
  text: string
  priorities: string[]
  format: "bullets" | "narrative" | "json"
  depth: "quick" | "medium" | "deep"
}

/**
 * TRUE discriminated union.
 * Matches backend reality exactly.
 */
export type SummarizeResponse =
  | {
      status: "success"
      narrative: string
    }
  | {
      status: "error"
      message: string
    }

export async function refineSummary(
  options: SummarizeOptions
): Promise<SummarizeResponse> {
  const res = await fetch(`${API_BASE}/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  })

  const json = await safeJSON(res)

  if (json.status === "success" && typeof json.narrative === "string") {
    return {
      status: "success",
      narrative: json.narrative,
    }
  }

  return {
    status: "error",
    message: json.message || "Failed to generate summary.",
  }
}
