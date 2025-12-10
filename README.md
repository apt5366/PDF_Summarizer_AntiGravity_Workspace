AI Document Intelligence Platform

Context-Aware Summaries • Insight Extraction • Ask-Anything Chat • Follow-Up Reasoning

This project is a full-stack AI system that uploads a PDF, analyzes it using an LLM-driven extraction pipeline, and provides highly relevant summaries, insights, and follow-ups tailored to the user's intent.
Designed for analysts, bankers, researchers, and operators who need fast, trustworthy document understanding with zero friction.

🌟 Key Features
1. Smart PDF Ingestion & Classification

Extracts text using PyMuPDF

Classifies the document by type

Auto-detects structure, sections, themes, and potential personas

Works with earnings reports, 10-K/10-Q, contracts, pitch decks, strategy docs, etc.

2. Insight-First Document Analysis

After upload, the system automatically generates:

A clean executive summary

3–5 key insights with page-mapped citations

Key themes

Suggested follow-up actions tailored to the document type

Structured categories (Financials, Risks, Strategy, etc.)

This allows any analyst to understand a document at a glance.

3. Guided Summary Customization (Redesign Flow)

Instead of forcing a generic summary, the system:

Detects doc type, persona, and internal signals

Suggests what the summary should focus on (risks, catalysts, financials, obligations, etc.)

Lets the user choose what they care about

Generates the final executive summary only after user confirmation

This dramatically increases user trust and relevance.

4. Ask-Anything Chat Mode

Users can ask natural questions like:

“What are the key risks?”

“Summarize financial performance in one paragraph.”

“What guidance is given for next quarter?”

The backend:

Retrieves relevant chunks

Asks the LLM using an extractive prompt

Returns an answer + supporting citations + page numbers

5. Instant Follow-Up Actions

From the first scan, the system surfaces helpful follow-ups such as:

Show me all risks

Extract key metrics

Summarize financial performance

Explain strategic initiatives

Click → Answer → Cited excerpts → Done.

6. Local or Cloud LLM Support

The backend supports:

Local models via Ollama (mistral, mistral:instruct, etc.)

Cloud LLMs (OpenAI, Anthropic, etc.)
Switchable via environment variable.

🏗️ System Architecture

frontend/
  ├─ app/
  │   └─ document/[file_id]/
  │        ├─ page.tsx
  │        └─ client-page.tsx
  ├─ components/
  │   ├─ executive-summary-card.tsx
  │   ├─ insight-list.tsx
  │   ├─ category-accordion.tsx
  │   ├─ followup-actions.tsx
  │   └─ chat-panel.tsx
  ├─ context/
  │   └─ DocumentContext.tsx
  └─ lib/
      └─ api.ts

backend/
  ├─ main.py                  ← FastAPI entrypoint
  ├─ utils/
  │   ├─ analysis_engine.py   ← Full analysis pipeline
  │   ├─ summarizer.py        ← Summary, insights, themes
  │   ├─ classifier.py        ← Doc type classifier
  │   ├─ pdf_utils.py         ← PDF text extraction
  │   └─ llm.py               ← Local/Cloud LLM abstraction
  └─ uploads/                 ← Temporary file storage


Tech Stack
Frontend (Next.js 14 + TypeScript)

Next.js App Router

Client-side React components

Context-based state management

Shadcn UI for consistent styling

Fetch-based API client

Backend (FastAPI + Python)

FastAPI with CORS

PyMuPDF for PDF extraction

Custom LLM abstraction layer

Local LLM execution via Ollama

JSON-based response models

Multi-step or single-step LLM pipelines

🧠 Analysis Pipeline Overview
Upload → Extract → Classify → Analyze → Suggest → Interact

Text extraction

Document classification (rule-based + optional LLM fallback)

Full analysis generation

Key insight extraction

Theme detection

Structured category summaries

Follow-up questions generation

Chat-based Q&A with citations

The system can fall back to a multi-call pipeline if the fast JSON path fails.

🔧 Running the System Locally
Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

Frontend
cd frontend
npm install
npm run dev

Ollama (for local LLMs)
ollama serve
ollama pull mistral


Switch the backend model:

export LLM_BACKEND=local
export LLM_MODEL=mistral:instruct

🗺️ Roadmap
Near-Term Enhancements

Guided “summary preference” step before generating executive summary

Persona-based analysis (Banker, VC, Operator, Lawyer, etc.)

Section-by-section reconstruction for structured documents

Multi-document comparison (e.g., Q1 → Q2 drift)

Future Extensions

User libraries & historical analysis

Competitive benchmarks (e.g., peers in the same industry)

Financial metric extraction & normalization

Auto-generated charts from financial tables
