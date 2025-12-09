# main.py

from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import logging
import traceback
from typing import Optional, List, Dict, Any

from utils.analysis_engine import analyze_pdf, answer_question
from utils.summarizer import summarize_document

# -------------------------------------------------------------------
# FastAPI + CORS setup
# -------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("antigravity")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------------------------------------------------
# Human-friendly names for UI
# -------------------------------------------------------------------

DOC_TYPE_DISPLAY: Dict[str, str] = {
    "contract": "Legal Contract",
    "annual_report": "Annual Report / 10-K",
    "quarterly_report": "Quarterly Earnings / 10-Q",
    "earnings_call": "Earnings Call Transcript",
    "market_analysis": "Market Analysis Report",
    "mou": "Memorandum of Understanding (MoU)",
    "sla": "Service Terms / SLA",
    "general": "Other",
}


class SummarizeRequest(BaseModel):
    text: str
    priorities: List[str] = []
    format: str = "bullets"  # "bullets" | "narrative" | "json"
    depth: str = "quick"     # "quick" | "medium" | "deep"


# -------------------------------------------------------------------
# /upload — core “scan and understand” endpoint
# -------------------------------------------------------------------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Handles:
    - PDF upload
    - Analysis via analyze_pdf()
    """
    file_id = str(uuid.uuid4())
    temp_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    # Save uploaded file
    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        logger.error("Error saving uploaded PDF: %s\n%s", e, traceback.format_exc())
        return {
            "status": "error",
            "message": "Failed to save uploaded PDF.",
        }

    # Run core analysis via engine
    try:
        analysis = analyze_pdf(temp_path)
    except Exception as e:
        logger.error("Unexpected error in analyze_pdf(): %s\n%s", e, traceback.format_exc())
        return {
            "status": "error",
            "message": "Internal error during document analysis.",
        }

    if analysis.get("status") != "success":
        return analysis

    raw_doc_type = analysis["raw_doc_type"]
    doc_type_label = DOC_TYPE_DISPLAY.get(raw_doc_type, "Other")

    return {
        "status": "success",
        "file_id": file_id,
        "file_name": file.filename,
        "doc_type": doc_type_label,
        "raw_doc_type": raw_doc_type,
        "full_text": analysis["full_text"],
        "quick_preview": analysis["quick_preview"],
        "executive_summary": analysis["executive_summary"],
        "key_insights": analysis["key_insights"],
        "follow_up_actions": analysis["follow_up_actions"],
        "themes": analysis["themes"],
        "categories": analysis.get("categories", []),
    }


# -------------------------------------------------------------------
# /summarize — refinement endpoint
# -------------------------------------------------------------------

@app.post("/summarize")
async def refine_summary(req: SummarizeRequest):
    """
    Refine / customize a summary given raw text and focus areas.
    """
    try:
        summary = summarize_document(
            text=req.text,
            focus_areas=req.priorities,
            output_format=req.format,
            depth=req.depth,
        )
    except Exception as e:
        logger.error("Error in summarize_document (refine): %s\n%s", e, traceback.format_exc())
        summary = "Summary unavailable due to internal error."
    return {"summary": summary}


# -------------------------------------------------------------------
# /ask — Q&A endpoint with citations (chat-style)
# -------------------------------------------------------------------

@app.post("/ask")
async def ask_question(payload: dict = Body(...)):
    """
    Q&A endpoint for "Ask Anything" chat mode.

    Accepts flexible payloads such as:
    - { "file_id": "...", "question": "..." }
    - { "fileId": "...", "question": "..." }
    """
    logger.info("ASK raw payload: %s", payload)

    file_id = payload.get("file_id") or payload.get("fileId")
    question = payload.get("question") or payload.get("query") or payload.get("prompt")
    doc_type = payload.get("doc_type") or payload.get("docType")

    if not file_id:
        return {
            "status": "error",
            "message": "Missing file_id in request body.",
        }

    if not question or not str(question).strip():
        return {
            "status": "error",
            "message": "Missing question in request body.",
        }

    pdf_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    if not os.path.exists(pdf_path):
        return {
            "status": "error",
            "message": f"No PDF found for file_id={file_id}.",
        }

    try:
        result = answer_question(
            file_path=pdf_path,
            question=str(question),
            doc_type=doc_type,
        )
    except Exception as e:
        logger.error("Unexpected error in answer_question(): %s\n%s", e, traceback.format_exc())
        return {
            "status": "error",
            "message": "Internal error while answering question.",
        }

    return result


# -------------------------------------------------------------------
# /followup — follow-up actions endpoint
# -------------------------------------------------------------------

@app.post("/followup")
async def run_followup(payload: dict = Body(...)):
    """
    Thin wrapper around the same core Q&A engine for follow-up buttons.

    Accepts both:
    - { "file_id": "...", "action": "Show me all risks..." }
    - { "file_id": "...", "question": "Show me all risks..." }
    - (and camelCase variants)
    """
    logger.info("FOLLOWUP raw payload: %s", payload)

    file_id = payload.get("file_id") or payload.get("fileId")
    action = payload.get("action") or payload.get("question")

    doc_type = payload.get("doc_type") or payload.get("docType")

    if not file_id:
        return {
            "status": "error",
            "message": "Missing file_id in follow-up request.",
        }

    if not action or not str(action).strip():
        return {
            "status": "error",
            "message": "No follow-up action text provided.",
        }

    pdf_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    if not os.path.exists(pdf_path):
        return {
            "status": "error",
            "message": f"No PDF found for file_id={file_id}.",
        }

    question_text = str(action).strip()
    logger.info("FOLLOWUP resolved question for file_id=%s: %s", file_id, question_text)

    try:
        result = answer_question(
            file_path=pdf_path,
            question=question_text,
            doc_type=doc_type,
        )
        if isinstance(result, dict):
            result.setdefault("meta", {})
            if isinstance(result["meta"], dict):
                result["meta"]["source"] = "followup"
    except Exception as e:
        logger.error("Unexpected error in followup/answer_question(): %s\n%s", e, traceback.format_exc())
        return {
            "status": "error",
            "message": "Internal error while running follow-up.",
        }

    return result
