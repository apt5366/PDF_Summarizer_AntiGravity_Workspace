from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import logging
import traceback

from utils.pdf_utils import extract_text_from_pdf
from utils.classifier import classify_document
from utils.summarizer import summarize_document, extract_key_themes

# basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("antigravity")

app = FastAPI()

# CORS for local V0 testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ----------------------------
# Human-friendly names for UI
# ----------------------------
DOC_TYPE_DISPLAY = {
    "contract": "Legal Contract",
    "annual_report": "Annual Report / 10-K",
    "quarterly_report": "Quarterly Earnings / 10-Q",
    "earnings_call": "Earnings Call Transcript",
    "market_analysis": "Market Analysis Report",
    "mou": "Memorandum of Understanding (MoU)",
    "sla": "Service Terms / SLA",
    "general": "Other"
}


class SummarizeRequest(BaseModel):
    text: str
    priorities: list[str] = []
    format: str = "bullets"
    depth: str = "quick"


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Handles:
    - PDF upload
    - Text extraction
    - Deterministic classification
    - Key theme extraction
    - Quick summary generation
    """
    file_id = str(uuid.uuid4())
    temp_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    # Save uploaded file
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Extract full text
    full_text = extract_text_from_pdf(temp_path)
    logger.info("PDF extracted: %d chars", len(full_text or ""))

    # Raw classifier output (canonical form)
    raw_doc_type = classify_document(full_text)
    logger.info("Classifier labeled document as: %s", raw_doc_type)

    # Human-readable label for UI
    doc_type = DOC_TYPE_DISPLAY.get(raw_doc_type, "Other")

    # Quick scan summary (defensive — wrap in try/except to avoid crashing the endpoint)
    try:
        preview = summarize_document(full_text, depth="quick")
    except Exception as e:
        logger.error("Error in summarize_document(): %s\n%s", e, traceback.format_exc())
        preview = "Summary unavailable due to internal error."

    # NEW: Extract key themes for UI insight (ensure always returns a list)
    try:
        themes = extract_key_themes(full_text)
        if not isinstance(themes, list):
            # safety — convert string fallback to list splitting lines
            if isinstance(themes, str):
                themes = [line.strip(" -\t\n\r") for line in themes.splitlines() if line.strip()]
            else:
                themes = []
    except Exception as e:
        logger.error("Error in extract_key_themes(): %s\n%s", e, traceback.format_exc())
        themes = []

    # Enforce sensible constraints: list of short strings, limit 6
    clean_themes = []
    for t in themes:
        if not isinstance(t, str):
            continue
        s = t.strip()
        if not s:
            continue
        # keep it short
        if len(s) > 80:
            s = s[:80].rsplit(" ", 1)[0] + "…"
        clean_themes.append(s)
        if len(clean_themes) >= 6:
            break

    # final fallback: if no themes, provide an explicit message so UI knows it's intentional
    if not clean_themes:
        clean_themes = ["No clear themes identified"]

    logger.info("Extracted themes: %s", clean_themes)

    return {
        "status": "success",
        "file_id": file_id,
        "file_name": file.filename,
        "doc_type": doc_type,
        "raw_doc_type": raw_doc_type,
        "full_text": full_text,
        "quick_preview": preview,
        "themes": clean_themes,  # reliable list now
    }


@app.post("/summarize")
async def refine_summary(req: SummarizeRequest):
    """Return refined summary using the selected focus areas."""
    try:
        summary = summarize_document(
            text=req.text,
            focus_areas=req.priorities,
            output_format=req.format,
            depth=req.depth
        )
    except Exception as e:
        logger.error("Error in summarize_document (refine): %s\n%s", e, traceback.format_exc())
        summary = "Summary unavailable due to internal error."
    return {"summary": summary}
