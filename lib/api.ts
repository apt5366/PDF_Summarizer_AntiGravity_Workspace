// lib/api.ts
import type { UploadResponse, AskResponse } from "@/types/api"

const API_BASE = "http://localhost:8000"

/**
 * Unified JSON handler.
 * Returns:
 *  - { status: "success", ...real data... }
 *  - { status: "error", message: string }
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
      message:
        json?.message ??
        json?.detail ??
        "Server reported an error.",
    }
  }

  // force guarantee: backend MUST include status
  if (!json.status) {
    return {
      status: "error",
      message: "Backend returned malformed response.",
    }
  }

  return json
}

// ------------------------------
// Upload PDF
// ------------------------------
export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append("file", file)

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  })

  return safeJSON(res)
}

// ------------------------------
// Freeform Question
// ------------------------------
export async function askQuestion(
  fileId: string,
  question: string
): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      file_id: fileId,
      question,
    }),
  })

  return safeJSON(res)
}

// ------------------------------
// Follow-up Action
// ------------------------------
export async function followUpAction(
  fileId: string,
  action: string
): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/followup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      file_id: fileId,
      action,
    }),
  })

  return safeJSON(res)
}
