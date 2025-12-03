from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid

from utils.pdf_utils import extract_text_from_pdf
from utils.classifier import classify_document
from utils.summarizer import summarize_document

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
    - Quick summary generation
    """
    file_id = str(uuid.uuid4())
    temp_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    # Save uploaded file
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Extract full text
    full_text = extract_text_from_pdf(temp_path)

    # Raw classifier output (canonical form)
    raw_doc_type = classify_document(full_text)

    # Human-readable label for UI
    doc_type = DOC_TYPE_DISPLAY.get(raw_doc_type, "Other")

    # Quick scan summary
    preview = summarize_document(full_text, depth="quick")

    return {
        "status": "success",
        "file_id": file_id,
        "file_name": file.filename,    # <-- Added
        "doc_type": doc_type,
        "raw_doc_type": raw_doc_type,  # <-- Helpful for debugging/UI logic
        "full_text": full_text,
        "quick_preview": preview
    }


@app.post("/summarize")
async def refine_summary(req: SummarizeRequest):
    """Return refined summary using the selected focus areas."""
    summary = summarize_document(
        text=req.text,
        focus_areas=req.priorities,
        output_format=req.format,
        depth=req.depth
    )
    return {"summary": summary}
