from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid

from utils.pdf_utils import extract_text_from_pdf
from utils.classifier import classify_document
from utils.summarizer import summarize_document

app = FastAPI()

# Enable local dev from v0
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class SummarizeRequest(BaseModel):
    text: str
    priorities: list[str] = []
    format: str = "bullets"
    depth: str = "quick"

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Handle PDF upload + classification + quick scan preview."""
    file_id = str(uuid.uuid4())
    temp_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Extract text
    full_text = extract_text_from_pdf(temp_path)

    # Classify doc
    doc_type = classify_document(full_text)

    # Quick preview summary
    preview = summarize_document(full_text, depth="quick")

    return {
        "status": "success",
        "file_id": file_id,
        "doc_type": doc_type,
        "full_text": full_text,
        "quick_preview": preview
    }


@app.post("/summarize")
async def refine_summary(req: SummarizeRequest):
    """Accept JSON and return refined summary."""
    summary = summarize_document(
        text=req.text,
        focus_areas=req.priorities,
        output_format=req.format,
        depth=req.depth
    )

    return {"summary": summary}
