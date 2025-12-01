from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils.pdf_utils import extract_text_from_pdf
from classifier import classify_document
from summarizer import summarize_document

app = FastAPI(title="DocScanner Backend")

class SummarizeRequest(BaseModel):
    text: str
    priorities: Optional[List[str]] = None

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF allowed.")
    
    try:
        content = await file.read()
        text = extract_text_from_pdf(content)
        
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
            
        classification_result = classify_document(text)
        
        return {
            "doc_type": classification_result.get("doc_type"),
            "summary": classification_result.get("summary"),
            "key_sections": classification_result.get("key_sections"),
            "full_text": text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize(request: SummarizeRequest):
    try:
        summary = summarize_document(request.text, request.priorities)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
