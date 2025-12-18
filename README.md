# AI Document Intelligence System

An end-to-end **AI-powered document analysis and summarization platform** designed for long, complex business documents such as financial reports, contracts, research papers, and strategy decks.

The system goes beyond generic summarization by combining **structured user intent**, **LLM-driven analysis**, and an **interactive review workflow** inspired by tools like AlphaSense and Harvey AI.

---

## 🚀 What This Project Does

This application allows users to upload large documents (PDFs) and:

* Automatically analyze document type, themes, and key insights
* Generate **tailored executive summaries** based on explicit structure
* Ask natural-language follow-up questions grounded in the document
* Explore insights, categories, and next-step actions without information overload

Rather than a single "summarize" button, the app focuses on **guided analysis** — helping users decide *what they want to extract* before the LLM generates output.

---

## 🧠 Why This Problem Is Non-Trivial

This project intentionally targets failure modes common in real-world LLM systems:

* **Importance is subjective**: What matters in a document depends heavily on the user’s role and decision context.
* **Long-context degradation**: Feeding entire documents into an LLM leads to attention dilution and shallow reasoning.
* **Lost-in-the-middle effects**: Critical information buried deep in long documents is often ignored by models.
* **Hallucination vs. faithfulness trade-off**: Fluent summaries are not always factually correct.
* **UX directly shapes model behavior**: Poor interfaces lead to poorly constrained prompts and low-quality output.

This system prioritizes *alignment, controllability, and structure* over brute-force context stuffing.

---

## 🧠 Core Design Philosophy

Traditional LLM summarizers fail because they guess what is important.

This system solves that by:

* Separating **structure definition** from **generation**
* Letting users explicitly define *sections* of an executive summary
* Using document signals (themes, insights, doc type) to guide, not overwhelm
* Generating summaries **only after intent is clear**

The result is higher-quality, more relevant summaries for analysts, bankers, investors, and decision-makers.

---

## ✨ Key Features

### 1. Intelligent Document Ingestion

* PDF upload and text extraction
* Page-aware and chunk-aware processing
* Automatic document-type detection (e.g. report, contract, memo)

### 2. Section Builder (Core Feature)

* Users define the **exact structure** of the executive summary
* Each section can include custom instructions or prompts
* System suggests structure using detected themes and insights

### 3. Tailored Executive Summary Generation

* Summary generated only after structure confirmation
* Supports:

  * Bullet-point or narrative style
  * Multiple depth levels (quick, medium, deep)
* Produces analyst-grade summaries aligned with user intent

### 4. Insight & Category Exploration

* Automatically extracted key insights
* High-level categories for fast scanning
* Collapsible UI to reduce cognitive load

### 5. Follow-up Actions & Q&A

* Suggested follow-up questions based on document content
* Interactive chat panel for grounded document Q&A
* Enables iterative exploration without regenerating summaries

### 6. Hybrid LLM Backend

* Supports local and cloud-based LLMs
* Designed to switch between:

  * Local open-source models (via Ollama / HuggingFace)
  * Cloud APIs (OpenAI / others)
* Optimized for long-document workflows

---

## 🤖 Backend ML & LLM Pipeline

The backend follows a **multi-stage, inference-time ML pipeline** designed specifically for long, complex documents where naïve prompting fails.

### 1. Document Ingestion & Preprocessing

* PDFs are parsed with page awareness to preserve document structure
* Text is chunked to balance locality and global context
* Basic normalization is applied prior to analysis

### 2. Lightweight Document Understanding (Pre-LLM)

* Document type is inferred (e.g., financial report, contract, memo)
* High-level themes and candidate insights are extracted
* These signals act as **control metadata**, not final outputs

### 3. User-Defined Structure as a Learning Signal

* The Section Builder defines an explicit output schema
* Each section represents a constrained generation objective
* This transforms a vague summarization task into multiple, well-scoped sub-tasks

### 4. Structured LLM Invocation

* LLM calls are made only after intent and structure are finalized
* Prompts are constructed per section with:

  * Explicit topical scope
  * Style constraints (bullets vs narrative)
  * Depth constraints (quick / medium / deep)
* This reduces hallucinations and improves factual alignment

### 5. Post-processing & Assembly

* Section-level outputs are assembled into a coherent executive summary
* Insights and follow-up actions are generated via separate prompts
* Regeneration occurs only when user intent changes

The pipeline is **model-agnostic** and supports seamless switching between local open-source models and cloud APIs.

**ML Perspective**:

* For *applied ML*, this demonstrates inference-time system design and controllability
* For *research-oriented ML*, it highlights prompt structuring, alignment, and mitigation of long-context failure modes

---

## 🏗️ Architecture Overview

```
┌───────────────────────────┐
│        Frontend           │
│  Next.js + React + TS     │
│                           │
│  • Document upload UI     │
│  • Section Builder        │
│  • Executive Summary UI   │
│  • Insights & Categories  │
│  • Chat-based Q&A         │
└─────────────┬─────────────┘
              │ REST API
              ▼
┌───────────────────────────┐
│          Backend          │
│        FastAPI (Py)       │
│                           │
│  • PDF ingestion          │
│  • Doc-type detection     │
│  • Theme & insight extract│
│  • Summary orchestration  │
│  • Follow-up generation   │
│  • LLM abstraction layer  │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│        LLM Layer          │
│                           │
│  • Local models (Ollama)  │
│  • Cloud APIs (optional)  │
│  • Prompt-structured gen  │
└───────────────────────────┘
```

The system is intentionally designed so that **UI-defined structure directly controls LLM behavior**, avoiding monolithic prompts and enabling future agentic retrieval.

### Frontend

* **Next.js (App Router)**
* TypeScript + React
* Component-driven UI
* Focus on clarity, progressive disclosure, and analyst workflows

Key frontend modules:

* Document viewer & state management
* Section Builder UI
* Executive Summary display
* Insight & category panels
* Chat-based Q&A interface

### Backend

* **FastAPI (Python)**
* Modular pipeline design

Key backend components:

* PDF text extraction utilities
* Document classification engine
* Summarization and refinement pipeline
* Insight and theme extraction
* Follow-up action generation
* LLM abstraction layer for backend switching

---

## 🔄 Typical User Flow

1. Upload a document (PDF)
2. System analyzes document type and internal structure
3. User defines or edits executive summary sections
4. User selects summary style and depth
5. Executive summary is generated
6. User explores insights, categories, and follow-up actions
7. User asks questions via chat for deeper analysis

---

## 🧩 Example Use Cases

* Financial analysts reviewing annual reports
* Investors scanning pitch decks or earnings transcripts
* Consultants summarizing strategy documents
* Legal or business users extracting obligations and risks
* Founders quickly understanding large internal documents

---

## 🛠️ Tech Stack

**Frontend**

* Next.js (App Router)
* React
* TypeScript
* Tailwind CSS / shadcn UI

**Backend**

* Python
* FastAPI
* Pydantic

**AI / LLM**

* Local open-source LLMs (via Ollama / HuggingFace)
* Optional cloud LLM APIs
* Extractive-first, structure-driven prompting

**Design Emphasis (for AI/ML Engineers)**

* Long-context handling via prioritization instead of brute-force context stuffing
* UI-driven prompt constraints
* Clean separation between *intent definition* and *generation*
* Architected for extension into agentic RAG and evaluation loops

---

## 🖼️ UI Preview

> Screenshots / demo GIFs coming soon.

![Recording 2025-12-18 152413](https://github.com/user-attachments/assets/25592234-6a00-4ece-a2d9-f180b8d10087)

![GIF_Section_builder_correct_size](https://github.com/user-attachments/assets/b2bb5528-b6b4-404c-b31e-1e245ace9e95)


![GIF_Gen_Summary_nd_key_insights_low_res](https://github.com/user-attachments/assets/e85e83bc-7ddb-4817-8023-21737d5c8143)

![Chat_feature_GIF_low_res](https://github.com/user-attachments/assets/2d537600-95d4-491d-929f-41c21e11bd05)


Planned views:
* Intro Page to insert PDF
* Section Builder (structure definition)
* Generated executive summary & Insight exploration panel
* Chat-based document Q&A

---

## ▶️ Setup & Run Locally

### Prerequisites

* Node.js (18+)
* Python (3.10+)
* Git
* Optional: Ollama or access to a cloud LLM API

---

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload
```

The backend will start at: [http://localhost:8000](http://localhost:8000)

---

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at: [http://localhost:3000](http://localhost:3000)

---

### LLM Configuration

The system has been tested primarily with **Mistral-Instruct** for local inference, while remaining fully **model-agnostic** and compatible with other open-source or cloud-hosted LLMs.

The backend supports switching between local and cloud models via environment variables.

**Local inference**

```bash
export LLM_BACKEND=local
export LOCAL_LLM_MODEL=mistral:instruct
```

**Cloud inference**

```bash
export LLM_BACKEND=openai
export OPENAI_API_KEY=your_key_here
```

---

## 📌 Current Status

* Core functionality complete and working end-to-end
* Focused on correctness, structure, and user intent
* Designed to evolve toward:

  * Section-based retrieval (agentic RAG)
  * Citations and provenance
  * More opinionated, inference-first UX modes

---

## 🚧 Scope Boundary

This project focuses on solving **alignment, structure, and user intent definition** for long-document summarization.

Advanced capabilities such as full agentic retrieval, citation grounding, multimodal table understanding, and automated evaluation are intentionally treated as *extensions*, not shortcuts. This keeps the core system debuggable, interpretable, and product-aligned.

---

## 🧭 Future Improvements

* Retrieval-per-section (agentic RAG loop)
* Page-level citations and references
* Table and chart understanding
* Evaluation and consistency checks
* Further UX simplification for non-technical users

---

## 👤 Author

**Ayush Tiwari**

Built as a full-stack, LLM-heavy systems project with a strong emphasis on:

* Ambiguity-driven product design
* Long-document reasoning constraints
* Practical trade-offs between UX simplicity and model controllability

This project demonstrates how AI/ML engineers can move beyond demos toward **production-oriented document intelligence systems**.

---

## 📄 License

This project is intended for learning, experimentation, and demonstration purposes.
