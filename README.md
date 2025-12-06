Antigravity Document Summarizer (V0)

Next-generation PDF understanding and summarization engine designed around an Insight-First workflow.

This project demonstrates how modern LLMs can automatically extract structure, context, key themes, and tailored summaries from long unstructured documents with minimal user input.

🚀 Key Features
1. Insight-First Workflow

Upload a PDF → system instantly produces:

Document type classification

Quick extractive summary

AI-detected key themes

Suggested focus areas based on doc type

No manual setup required.

2. Extractive Summarization Engine

Uses a controlled, grounded prompt

Ensures no hallucinations

Prioritizes accuracy and evidence from the document

Supports configurable depth (quick, medium, deep)

Supports multiple formats (bullets, narrative, JSON)

3. Theme-Aware Refinement

Users can:

Click on AI-detected themes

Choose suggested focus areas

Refine the summary based on selected topics

The backend integrates these into a targeted second-pass summarization.

4. Automatic Document Classification

Documents are automatically categorized into canonical types:

Annual report

Quarterly report

Earnings call

Contract / Legal agreement

Market analysis

MOU / SLA

General document

This classification drives downstream theme and focus suggestions.

5. Flexible LLM Backend (Local / Cloud Ready)

The system is architected so the LLM backend can be swapped between:

Local models (e.g., running via Ollama or similar)

Cloud APIs (OpenAI, Anthropic, Gemini)

This allows:

Fast, cheap local development

High-accuracy cloud inference for demos or production

(Backend switching module will be expanded in upcoming updates.)

6. Modern Frontend (Next.js + ShadCN UI)

The UI includes:

PDF upload panel

Summary preview panel

Theme chips

Suggested focus area chips

Format/depth refinement controls

Live refinement output

Designed for clarity and minimal cognitive load.

🧠 Project Architecture
frontend/
  app/
    page.tsx
    components/
      upload-panel.tsx
      preview-panel.tsx
      preview-card.tsx
      suggested-focus-areas.tsx
      focus-areas-chips.tsx
      error-panel.tsx
      refine-controls.tsx
  public/
  styles/

backend/
  main.py                   # FastAPI server
  utils/
    pdf_utils.py            # PDF text extraction
    classifier.py           # Deterministic doc-type classifier
    summarizer.py           # Summary + theme extraction logic
    llm.py                  # Local LLM interface (cloud-ready)

uploads/                    # Temporary PDF storage

⚙️ Tech Stack
Backend

Python

FastAPI

PyMuPDF for PDF parsing

Local LLM interface (cloud-upgradable)

Frontend

Next.js (App Router)

React

TailwindCSS

shadcn/ui components

📡 API Endpoints
POST /upload

Uploads a PDF and returns:

{
  "status": "success",
  "file_id": "...",
  "doc_type": "Annual Report / 10-K",
  "raw_doc_type": "annual_report",
  "full_text": "...",
  "quick_preview": "...",
  "themes": ["Audit & Opinion", "Financial Risks", ...]
}

POST /summarize

Refines the summary based on user-selected areas:

{
  "summary": "..."
}

💻 Running the Project
Backend
cd backend
uvicorn main:app --reload


Backend runs at:

http://127.0.0.1:8000

Frontend
cd frontend
npm install
npm run dev


Frontend runs at:

http://localhost:3000

🖼️ User Interface Flow
1. Upload → Auto Scan

System extracts text

Detects document type

Generates a quick summary

Extracts key themes

2. User Selects Themes or Focus Areas

Themes appear immediately under the summary

Clicking a theme adds it to refinement

3. Refinement

User selects format (bullets, narrative, JSON)

User selects depth (quick, medium, deep)

Summary updates with theme-weighted extraction

🏗️ System Architecture Diagram

                        ┌────────────────────────┐
                        │        Frontend        │
                        │  (Next.js + Tailwind)  │
                        └───────────┬────────────┘
                                    │
                     Upload PDF     │    Get Summary / Themes
                                    ▼
                    ┌────────────────────────────┐
                    │          Backend            │
                    │        (FastAPI)            │
                    ├─────────────┬───────────────┤
                    │             │               │
        ┌───────────▼───┐   ┌─────▼────────┐  ┌──▼────────────────┐
        │  PDF Extractor │   │ Classifier    │  │ Summarizer        │
        │   (PyMuPDF)    │   │ (Rules-based) │  │ + Theme Extractor │
        └───────────────┘   └───────────────┘  └──────┬────────────┘
                                                       │
                                               LLM Request via
                                                       │
                                        ┌────────────────────────────────┐
                                        │         run_llm() Wrapper      │
                                        ├────────────────┬───────────────┤
                                        │                │               │
                                ┌───────▼──────┐  ┌─────▼───────┐  ┌────▼─────────┐
                                │ Local LLM     │  │ OpenAI API   │  │ Claude API   │
                                │ (Ollama)      │  │ (Optional)   │  │ (Optional)    │
                                └───────────────┘  └──────────────┘  └──────────────┘


🎯 Completed Against Employer Requirements

Removed all manual configuration

No persona or ranking steps

Fully automated “Scan First → Ask Later” workflow

Theme-driven refinement

Extractive, grounded summarization

Dynamic UI based on doc type

Replaces wizard UI with Draft-and-Refine pattern

🔮 Next Planned Improvements

Chunk-aware summarization for long documents

Cloud LLM backend toggle

Deep-dive refinement (“Explain more about X”)

Search-inside-document with extracted highlights

Lightweight validation: summary faithfulness check

📄 License

MIT — free to use, modify, and extend.
