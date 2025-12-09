# utils/analysis_engine.py

import logging
import json
import re
from typing import Dict, Any, List, Optional

from utils.pdf_utils import extract_text_from_pdf, extract_text_by_page
from utils.classifier import classify_document
from utils.summarizer import (
    summarize_document,
    extract_key_themes,
    generate_executive_summary,
    extract_key_insights,
    suggest_follow_up_actions,
    generate_full_analysis,
)
from utils.llm import run_llm

logger = logging.getLogger("antigravity.analysis_engine")


def _normalize_themes(themes: Any) -> List[str]:
    """Normalize themes into a clean list of up to 6 short strings."""
    if themes is None:
        return []

    if isinstance(themes, str):
        lines = [line.strip(" -\t\n\r") for line in themes.splitlines() if line.strip()]
        themes_list = lines
    elif isinstance(themes, list):
        themes_list = themes
    else:
        themes_list = []

    clean: List[str] = []
    for t in themes_list:
        if not isinstance(t, str):
            continue
        s = t.strip()
        if not s:
            continue
        if len(s) > 80:
            s = s[:80].rsplit(" ", 1)[0] + "…"
        clean.append(s)
        if len(clean) >= 6:
            break

    if not clean:
        clean = ["No clear themes identified"]

    return clean


# ---------------------- Excerpt → page matching --------------------


def _match_excerpts_to_pages(
    excerpts: List[str],
    page_texts: List[str],
) -> List[Dict[str, Any]]:
    """
    Very simple heuristic:
    - For each excerpt, search for it in each page's text.
    - If not found, try matching the first ~80 chars.
    - Return list of { "excerpt": str, "page": int | None }.
    """
    results: List[Dict[str, Any]] = []

    for ex in excerpts:
        ex_clean = (ex or "").strip()
        if not ex_clean:
            continue

        found_page: Optional[int] = None

        # Try full excerpt first
        for i, page_txt in enumerate(page_texts):
            if ex_clean and ex_clean in page_txt:
                found_page = i + 1  # 1-indexed
                break

        # Try partial if not found
        if found_page is None and len(ex_clean) > 40:
            probe = ex_clean[:80]
            for i, page_txt in enumerate(page_texts):
                if probe in page_txt:
                    found_page = i + 1
                    break

        results.append(
            {
                "excerpt": ex_clean,
                "page": found_page,
            }
        )

    return results


# -------------------------------------------------------------------
# MAIN ANALYSIS PIPELINE FOR /upload (FAST PATH)
# -------------------------------------------------------------------

def analyze_pdf(file_path: str) -> Dict[str, Any]:
    """
    Main analysis pipeline for /upload.

    NEW FAST ARCHITECTURE:
    - 1 LLM call via generate_full_analysis() returns:
        quick_preview, executive_summary, themes,
        key_insights, categories, follow_up_actions
    - We then map excerpts/snippets to page numbers.

    Returns a dict with:
    - status
    - raw_doc_type
    - full_text
    - quick_preview
    - executive_summary
    - key_insights  (with pages)
    - follow_up_actions
    - themes
    - categories    (with snippets + pages)
    """
    full_text = extract_text_from_pdf(file_path)
    text_len = len(full_text or "")
    logger.info("PDF extracted: %d chars", text_len)

    if not full_text:
        return {"status": "error", "message": "No text could be extracted from the PDF."}

    # Classification (rule-based + optional LLM fallback inside classify_document)
    raw_doc_type = classify_document(full_text)
    logger.info("Classifier labeled document as: %s", raw_doc_type)

    # Page-level texts for citations
    page_texts = extract_text_by_page(file_path)

    # ------------------ FAST PATH: ONE LLM CALL ---------------------
    try:
        fa = generate_full_analysis(full_text, doc_type=raw_doc_type)
    except Exception as e:
        logger.error("generate_full_analysis failed, falling back to legacy calls: %s", e, exc_info=True)
        fa = None

    if fa is not None:
        quick_preview = fa.get("quick_preview") or ""
        executive_summary = fa.get("executive_summary") or ""

        # Themes
        themes = _normalize_themes(fa.get("themes"))

        # Key insights + page mapping
        key_insights_raw = fa.get("key_insights") or []
        key_insights: List[Dict[str, Any]] = []
        ki_excerpts: List[str] = []

        if isinstance(key_insights_raw, list):
            for item in key_insights_raw:
                if not isinstance(item, dict):
                    continue
                title = (item.get("title") or "").strip()
                summary = (item.get("summary") or "").strip()
                excerpt = (item.get("source_excerpt") or "").strip()
                if not title and not summary and not excerpt:
                    continue
                ki_excerpts.append(excerpt)
                key_insights.append(
                    {
                        "title": title or "Insight",
                        "summary": summary or excerpt or "No summary available.",
                        "source_excerpt": excerpt,
                        # page will be filled after matching
                        "page": None,
                    }
                )

        # Map key_insights excerpts to pages
        if key_insights and page_texts:
            ki_citations = _match_excerpts_to_pages(
                [ki["source_excerpt"] for ki in key_insights],
                page_texts,
            )
            for ki, cit in zip(key_insights, ki_citations):
                ki["page"] = cit.get("page") or 0  # 0 if unknown

        # Categories: map snippet_texts → snippets[{text, page}]
        categories_raw = fa.get("categories") or []
        categories: List[Dict[str, Any]] = []

        if isinstance(categories_raw, list):
            for cat in categories_raw:
                if not isinstance(cat, dict):
                    continue
                key = (cat.get("key") or "").strip() or "category"
                title = (cat.get("title") or "").strip() or "Category"
                summary = (cat.get("summary") or "").strip()
                snippet_texts = cat.get("snippet_texts") or []
                if not isinstance(snippet_texts, list):
                    snippet_texts = []

                # map snippet_texts to pages
                snippets_with_pages: List[Dict[str, Any]] = []
                if page_texts and snippet_texts:
                    cit_list = _match_excerpts_to_pages(snippet_texts, page_texts)
                    for ex, cit in zip(snippet_texts, cit_list):
                        snippets_with_pages.append(
                            {
                                "text": cit.get("excerpt") or ex,
                                "page": cit.get("page") or 0,
                            }
                        )
                categories.append(
                    {
                        "key": key,
                        "title": title,
                        "summary": summary,
                        "snippets": snippets_with_pages,
                    }
                )

        # Follow up actions
        follow_up_actions_raw = fa.get("follow_up_actions") or []
        follow_up_actions: List[str] = []
        if isinstance(follow_up_actions_raw, list):
            for q in follow_up_actions_raw:
                if isinstance(q, str) and q.strip():
                    follow_up_actions.append(q.strip())

        logger.info("Extracted themes: %s", themes)
        logger.info("Key insights count: %d", len(key_insights))
        logger.info(
            "Categories summarized (fast path): %s",
            [c["key"] for c in categories],
        )
        logger.info("Follow-up actions: %s", follow_up_actions)

    else:
        # ------------------ LEGACY FALLBACK PATH -------------------
        logger.info("Using legacy multi-call pipeline as fallback.")

        # Quick preview
        try:
            quick_preview = summarize_document(full_text, depth="quick")
        except Exception as e:
            logger.error("Error in summarize_document(quick): %s", e, exc_info=True)
            quick_preview = "Quick preview unavailable due to internal error."

        # Executive summary
        try:
            executive_summary = generate_executive_summary(
                text=full_text,
                doc_type=raw_doc_type,
            )
        except Exception as e:
            logger.error("Error in generate_executive_summary(): %s", e, exc_info=True)
            executive_summary = quick_preview

        # Key insights
        try:
            key_insights_no_page = extract_key_insights(
                text=full_text,
                doc_type=raw_doc_type,
            )
        except Exception as e:
            logger.error("Error in extract_key_insights(): %s", e, exc_info=True)
            key_insights_no_page = []

        # Map to pages using source_excerpt
        key_insights: List[Dict[str, Any]] = []
        if key_insights_no_page and page_texts:
            citations = _match_excerpts_to_pages(
                [ki.get("source_excerpt", "") for ki in key_insights_no_page],
                page_texts,
            )
            for base, cit in zip(key_insights_no_page, citations):
                ki = dict(base)
                ki["page"] = cit.get("page") or 0
                key_insights.append(ki)
        else:
            for base in key_insights_no_page:
                ki = dict(base)
                ki["page"] = 0
                key_insights.append(ki)

        # Themes
        try:
            themes_raw = extract_key_themes(full_text)
        except Exception as e:
            logger.error("Error in extract_key_themes(): %s", e, exc_info=True)
            themes_raw = []
        themes = _normalize_themes(themes_raw)

        # Follow-up actions (rule-based)
        follow_up_actions = suggest_follow_up_actions(
            doc_type=raw_doc_type,
            insights=key_insights,
        )

        # Legacy fallback has no structured categories
        categories: List[Dict[str, Any]] = []

        logger.info("Extracted themes (legacy): %s", themes)
        logger.info("Key insights count (legacy): %d", len(key_insights))
        logger.info("Follow-up actions (legacy): %s", follow_up_actions)

    return {
        "status": "success",
        "raw_doc_type": raw_doc_type,
        "full_text": full_text,
        "quick_preview": quick_preview,
        "executive_summary": executive_summary,
        "key_insights": key_insights,
        "follow_up_actions": follow_up_actions,
        "themes": themes,
        "categories": categories,
    }


# ---------------------- Q&A + citations -----------------------------


def answer_question(
    file_path: str,
    question: str,
    doc_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Core engine for /ask and /followup.

    Returns:
    {
      "status": "success",
      "answer": "...",
      "supporting_excerpts": [
        { "excerpt": "...", "page": 3 },
        ...
      ]
    }
    """
    full_text = extract_text_from_pdf(file_path)
    if not full_text:
        return {
            "status": "error",
            "message": "Could not extract text for Q&A.",
        }

    page_texts = extract_text_by_page(file_path)
    type_hint = doc_type or "document"

    qa_prompt = f"""
You are an assistant answering questions about a single {type_hint}.

USER QUESTION:
{question}

RULES:
- Use ONLY the document text below.
- If the answer is not clearly stated, say:
  "The document does not provide a clear answer."
- Be concise (4–8 sentences).
- Provide up to 3 short supporting excerpts, quoted verbatim from the text.

Return JSON exactly in this format:
{{
  "answer": "<short answer>",
  "supporting_excerpts": [
    "<quote 1>",
    "<quote 2>"
  ]
}}

DOCUMENT:
{full_text[:16000]}
"""

    try:
        raw = run_llm(qa_prompt)
        raw = (raw or "").strip()
        logger.info("LLM returned (Q&A raw): %s", raw[:2000])
    except Exception as e:
        logger.error("Error calling LLM in answer_question(): %s", e, exc_info=True)
        return {
            "status": "error",
            "message": "LLM error while answering question.",
        }

    answer_text = "The document does not provide a clear answer."
    supporting_excerpts: List[str] = []

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        json_str = match.group(0) if match else raw
        data = json.loads(json_str)

        answer_text = (data.get("answer") or answer_text).strip()
        se = data.get("supporting_excerpts") or []
        supporting_excerpts = [str(x).strip() for x in se if str(x).strip()]
    except Exception as e:
        logger.warning("Failed to parse JSON from Q&A output: %s", e)

    citations = _match_excerpts_to_pages(supporting_excerpts, page_texts)

    return {
        "status": "success",
        "answer": answer_text,
        "supporting_excerpts": citations,
    }
