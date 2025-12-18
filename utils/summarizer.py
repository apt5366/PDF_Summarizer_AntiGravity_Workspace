# utils/summarizer.py

import logging
import re
import json
from typing import List, Dict, Any, Optional

from utils.llm import run_llm

logger = logging.getLogger("antigravity.summarizer")
logging.basicConfig(level=logging.INFO)


# def enforce_format(text: str, fmt: str) -> str:
#     """
#     Ensure bullet vs narrative formatting is respected.
#     """
#     cleaned = (text or "").strip()

#     if fmt == "bullets":
#         lines = [l.strip("-• ").strip() for l in cleaned.split("\n") if l.strip()]
#         return "\n".join(f"- {l}" for l in lines)

#     # narrative
#     return cleaned

def enforce_format(text: str, fmt: str) -> str:
    """
    Ensure bullet vs narrative formatting is respected.
    Handles stringified lists like ['a', 'b', 'c'] safely.
    """
    cleaned = (text or "").strip()

    if fmt != "bullets":
        return cleaned

    # Remove surrounding brackets if present
    if cleaned.startswith("[") and cleaned.endswith("]"):
        cleaned = cleaned[1:-1]

    # Split on comma ONLY if it looks like a quoted list
    if "','" in cleaned or '", "' in cleaned:
        parts = re.split(r"',\s*'|\",\s*\"", cleaned)
        lines = [p.strip(" '\"") for p in parts if p.strip()]
    else:
        lines = [
            l.strip("-• ").strip()
            for l in cleaned.split("\n")
            if l.strip()
        ]

    return "\n".join(f"- {l}" for l in lines)



# -------------------------------------------------------------------
# Core summarizer (existing) – still used by /summarize endpoint
# -------------------------------------------------------------------

def summarize_document(
    text: str,
    focus_areas: Optional[List[str]] = None,
    output_format: str = "bullets",
    depth: str = "quick",
) -> str:
    """
    High-quality, extractive-first summarization.
    Uses ONLY the provided text. Includes focus-area weighting.
    """
    if focus_areas is None:
        focus_areas = []

    depth_instructions = {
        "quick": "Return ONLY the 4–6 most essential points.",
        "medium": "Return 8–12 key points with moderate detail.",
        "deep": "Return a detailed multi-section summary capturing all major themes.",
    }

    format_instructions = {
        "bullets": "Use concise bullet points.",
        "narrative": "Return a short, well-structured narrative paragraph.",
        "json": "Return a valid JSON object with clearly named fields.",
    }

    if focus_areas:
        focus_block = (
            "The user is specifically interested in the following topics. "
            "Prioritize these FIRST, and expand them with as much extractive detail as possible:\n"
            f"- " + "\n- ".join(focus_areas)
        )
    else:
        focus_block = (
            "No specific focus areas were selected—identify and summarize the strongest themes naturally."
        )

    doc_snippet = text[:14000] if text else ""


    if output_format == "bullets":
        style_block = """
    Write the summary strictly as bullet points.
    - Use '-' for bullets
    - No paragraphs
    - No section headers
    """
    else:
        style_block = """
    Write the summary as a continuous narrative.
    - Use full sentences and paragraphs
    - Do not use bullet points
    """


    prompt = f"""
You are an **EXTRACTIVE summarization model**.

Your job is to summarize ONLY the text provided. 
STRICT RULES:
- DO NOT guess or invent information.
- DO NOT add data that is not explicitly present in the text.
- DO NOT generalize beyond the document.
- If a focus area has no coverage in the text, clearly state: "Not discussed in the document."


{style_block}

Summarization goals:
{focus_block}

Output format:
{format_instructions.get(output_format, "Use bullet points.")}

Depth requirement:
{depth_instructions.get(depth, depth_instructions["quick"])}

-----------------------------------------
DOCUMENT TO SUMMARIZE (BEGIN)
-----------------------------------------
{doc_snippet}
-----------------------------------------
DOCUMENT TO SUMMARIZE (END)
-----------------------------------------

Now return the final summary.
"""

    try:
        out = run_llm(prompt).strip()
        if not out:
            logger.warning("LLM returned empty summary (summarize_document).")
            return "No summary returned by LLM."
        return enforce_format(out, output_format)
    except Exception as e:
        logger.exception("Error calling run_llm in summarize_document(): %s", e)
        raise


# -------------------------------------------------------------------
# EXECUTIVE SUMMARY (narrative, doc-type aware)
# -------------------------------------------------------------------

def generate_executive_summary(text: str, doc_type: Optional[str] = None) -> str:
    """
    Generate a concise, narrative-style executive summary suitable
    as the main thing a banker/analyst sees after upload.
    """
    doc_snippet = text[:16000] if text else ""
    type_hint = doc_type or "document"

    prompt = f"""
You are generating an EXECUTIVE SUMMARY for a professional user
(e.g., banker, analyst, or investor) who has just uploaded a {type_hint}.

STRICT RULES:
- Be factual and extractive. Use ONLY information in the text.
- Do NOT speculate or add external knowledge.
- Aim for 3–6 short paragraphs (6–10 lines total).
- Emphasize the most valuation-relevant or decision-relevant points
  (financial position, key risks, outlook, obligations, material events),
  adapted appropriately to the document type.

Output:
- A single narrative block of text. No bullet points.
- Clear, plain English, ready for display in a UI as an executive summary.

-----------------------------------------
DOCUMENT (BEGIN)
-----------------------------------------
{doc_snippet}
-----------------------------------------
DOCUMENT (END)
-----------------------------------------
"""

    try:
        out = run_llm(prompt).strip()
        if not out:
            logger.warning("LLM returned empty executive summary.")
            return "No executive summary returned by LLM."
        return out
    except Exception as e:
        logger.exception("Error calling run_llm in generate_executive_summary(): %s", e)
        raise


# -------------------------------------------------------------------
# THEME EXTRACTION HELPERS (unchanged)
# -------------------------------------------------------------------

def _parse_bulleted_text_to_list(raw: str) -> List[str]:
    if not raw:
        return []

    normalized = raw.replace("•", "-").replace("\u2022", "-")
    lines = [l.strip() for l in normalized.splitlines() if l.strip()]
    themes: List[str] = []

    bullet_re = re.compile(r"^(?:[-\u2022*]|\d+[\).])\s*(.+)$")

    for line in lines:
        m = bullet_re.match(line)
        if m:
            themes.append(m.group(1).strip())
            continue

        if ":" in line and len(line) < 200:
            _, right = line.split(":", 1)
            parts = [p.strip() for p in re.split(r",|;|\band\b", right) if p.strip()]
            themes.extend(parts)
            continue

        if "," in line and len(line) < 200:
            parts = [p.strip() for p in line.split(",") if p.strip()]
            themes.extend(parts)
            continue

        if len(line.split()) <= 8:
            themes.append(line)

    cleaned: List[str] = []
    for t in themes:
        s = re.sub(r'^[\-\d\).\s]+', '', t).strip()
        s = s.strip('"\'' )
        if s and s.lower() not in (x.lower() for x in cleaned):
            cleaned.append(s)
    return cleaned


def _simple_freq_fallback(text: str, max_items: int = 6) -> List[str]:
    if not text:
        return []

    stop = {
        "the", "and", "of", "to", "in", "a", "for", "is", "with",
        "that", "on", "as", "are", "by", "this", "an", "be", "or",
        "has", "at", "from", "was", "it", "their", "which", "its",
    }

    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    freq: Dict[str, int] = {}
    for w in words:
        if w in stop:
            continue
        freq[w] = freq.get(w, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda x: -x[1])
    themes = [w for w, _ in sorted_words[:max_items]]
    return [t.title() for t in themes if t]


def _strip_parenthetical(s: str) -> str:
    return re.sub(r'\s*\(.*?\)\s*', ' ', s).strip()


def _shorten_to_n_words(s: str, n: int = 5) -> str:
    parts = re.split(r'\s+', s)
    if len(parts) <= n:
        return s
    return " ".join(parts[:n]).rstrip(' ,;:') + "…"


def _friendly_map(s: str) -> str:
    low = s.lower()
    if "compli" in low or "frs" in low or "companies act" in low or "sorp" in low:
        return "Regulatory Compliance"
    if "audit" in low or "auditor" in low or "independent" in low:
        return "Audit & Opinion"
    if "true and fair" in low or "fair view" in low:
        return "Financial Reporting"
    if "going concern" in low:
        return "Going Concern"
    if "director" in low or "governance" in low:
        return "Governance / Directors"
    if "risk" in low:
        return "Risk Factors"
    return s


def _normalize_and_dedupe(items: List[str], max_items: int = 6) -> List[str]:
    seen = set()
    out: List[str] = []
    for raw in items:
        text = raw.strip()
        if not text:
            continue
        text = _strip_parenthetical(text)
        text = re.sub(r'[^\w\s\-\&\/]', '', text)
        text = _shorten_to_n_words(text, n=5)
        text = _friendly_map(text)
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
        if len(out) >= max_items:
            break
    return out


def extract_key_themes(text: str) -> List[str]:
    if not text:
        return []

    doc_snippet = text[:14000]

    theme_prompt = f"""
You are an expert at identifying high-level themes in documents.

TASK:
Extract ONLY the major themes present in the following text.
Return 3–6 themes MAX.

STRICT RULES:
- Themes must come DIRECTLY from the document.
- DO NOT invent topics that are not mentioned.
- Keep theme names short (2–5 words).
- Each theme must reflect an actual repeated concept or section.

FORMAT:
Return as a simple bullet list:
- Theme 1
- Theme 2
- Theme 3
...

-----------------------------------------
DOCUMENT (BEGIN)
-----------------------------------------
{doc_snippet}
-----------------------------------------
DOCUMENT (END)
-----------------------------------------
"""

    try:
        raw = run_llm(theme_prompt)
        raw = (raw or "").strip()
        logger.info("LLM returned (themes): %s", raw[:2000])
    except Exception as e:
        logger.exception("LLM call failed in extract_key_themes(): %s", e)
        raw = ""

    parsed = _parse_bulleted_text_to_list(raw)
    parsed = [p for p in parsed if p][:6]

    if parsed:
        processed = _normalize_and_dedupe(parsed, max_items=6)
        if len(processed) < 3:
            supplement = [p for p in parsed if p.lower() not in (x.lower() for x in processed)]
            processed.extend(supplement[: (3 - len(processed))])
        if processed:
            return processed[:6]

    fallback = _simple_freq_fallback(text, max_items=6)
    if fallback:
        fallback = _normalize_and_dedupe(fallback, max_items=6)
        return fallback[:6]

    return []


# -------------------------------------------------------------------
# KEY INSIGHTS (existing helper – still useful)
# -------------------------------------------------------------------

def extract_key_insights(text: str, doc_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns a list of dictionaries like:
    {
      "title": "Audit opinion is unqualified",
      "summary": "Auditors expressed an unqualified opinion ...",
      "source_excerpt": "\"In our opinion, the accompanying ...\""
    }
    """
    if not text:
        return []

    doc_snippet = text[:16000]
    type_hint = doc_type or "document"

    prompt = f"""
You are an assistant generating KEY INSIGHTS for a professional user
(e.g. banker, analyst, investor) who has uploaded a {type_hint}.

TASK:
- Identify the 3–6 most important insights or findings in this document.
- For each insight, provide:
  - a short TITLE (2–7 words),
  - a 1–3 sentence SUMMARY (purely extractive),
  - a short SOURCE_EXCERPT copied verbatim from the document
    that supports this insight (1–3 sentences max).

STRICT RULES:
- Use ONLY information from the document.
- NO hallucinations, NO external facts.
- SOURCE_EXCERPT must be copied from the text (you may trim for brevity).
- Focus on decision-relevant information:
  - financial position, key risks, guidance/outlook,
    audit opinion, major obligations, etc. depending on document type.

OUTPUT FORMAT (valid JSON):
{{
  "insights": [
    {{
      "title": "...",
      "summary": "...",
      "source_excerpt": "..."
    }},
    ...
  ]
}}

-----------------------------------------
DOCUMENT (BEGIN)
-----------------------------------------
{doc_snippet}
-----------------------------------------
DOCUMENT (END)
-----------------------------------------
"""

    try:
        raw = run_llm(prompt)
        raw = (raw or "").strip()
        logger.info("LLM returned (key_insights raw): %s", raw[:2000])
    except Exception as e:
        logger.exception("LLM call failed in extract_key_insights(): %s", e)
        return []

    # Try to parse JSON robustly
    data: Dict[str, Any] = {}
    try:
        # Sometimes model wraps JSON in backticks or text; try to extract
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            raw_json = json_match.group(0)
        else:
            raw_json = raw
        data = json.loads(raw_json)
    except Exception as e:
        logger.warning("Failed to parse JSON from key_insights output: %s", e)
        return []

    insights_raw = data.get("insights") or []
    results: List[Dict[str, Any]] = []

    for item in insights_raw:
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip()
        summary = (item.get("summary") or "").strip()
        excerpt = (item.get("source_excerpt") or "").strip()

        if not title and not summary:
            continue

        results.append(
            {
                "title": title or "Insight",
                "summary": summary or excerpt or "No summary available.",
                "source_excerpt": excerpt,
            }
        )
        if len(results) >= 6:
            break

    return results


# -------------------------------------------------------------------
# FOLLOW-UP ACTION SUGGESTIONS (rule-based)
# -------------------------------------------------------------------

def suggest_follow_up_actions(
    doc_type: Optional[str],
    insights: List[Dict[str, Any]],
) -> List[str]:
    """
    Returns a small list (3–5) of suggested follow-up actions/questions
    the UI can show as buttons. Purely rule-based for now.
    """
    base_actions: List[str] = []

    key = (doc_type or "").lower()

    if key in {"annual_report", "quarterly_report", "earnings_call", "market_analysis"}:
        base_actions.extend(
            [
                "Show me all key risks",
                "Summarize financial performance",
                "Extract key metrics and ratios",
                "What guidance or outlook is discussed?",
            ]
        )
        if key == "earnings_call":
            base_actions.append("Summarize management sentiment and tone")
    elif key in {"contract", "mou", "sla"}:
        base_actions.extend(
            [
                "Summarize parties and obligations",
                "Show payment terms and fees",
                "Summarize termination and renewal conditions",
                "Highlight key risks and liabilities",
            ]
        )
    else:
        base_actions.extend(
            [
                "Give me a more detailed summary",
                "Highlight the main risks or concerns",
                "Show any important numbers or metrics",
            ]
        )

    # Add 1–2 insight-derived questions, if any
    for ins in insights[:2]:
        t = ins.get("title", "").strip()
        if not t:
            continue
        base_actions.append(f"Show more detail about: {t}")

    # Deduplicate while preserving order
    seen = set()
    final_actions: List[str] = []
    for q in base_actions:
        if q in seen:
            continue
        seen.add(q)
        final_actions.append(q)
        if len(final_actions) >= 6:
            break

    return final_actions

# ================================================================
# 🔥 NEW: Structured Section-by-Section Summarizer (/summarize)
# ================================================================


def generate_structured_section_summary(
    text: str,
    priorities: List[str],
    output_format: str = "bullets",
    depth: str = "medium",
) -> Dict[str, Any]:

    if not text:
        return {"status": "error", "message": "Empty document text."}

    doc_snippet = text[:24000]

    depth_rules = {
        "quick": "Write 2–4 sentences per section.",
        "medium": "Write 4–7 sentences per section.",
        "deep": "Write 2–3 short paragraphs per section.",
    }

    format_rules = {
        "bullets": (
            "Each section value MUST be a single STRING.\n"
            "Use '- ' for bullets inside the string.\n"
            "DO NOT return arrays, JSON, or nested objects."
        ),
        "narrative": (
            "Each section value MUST be a single STRING.\n"
            "Plain sentences only. NO bullets, NO JSON."
        ),
    }

    readable_plan = "\n".join(f"- {p}" for p in priorities)

    prompt = f"""
You are an EXTRACTIVE summarization model.

STRICT RULES:
- Use ONLY information in the document.
- NO speculation.
- If missing: write exactly "Not discussed in the document."

SECTION PLAN (YOU MUST RETURN ALL OF THESE):
{readable_plan}

IMPORTANT:
You MUST return an entry for EVERY section listed above.

FORMAT RULES:
{format_rules.get(output_format)}

DEPTH:
{depth_rules.get(depth)}

OUTPUT (JSON ONLY):
{{
  "sections": {{
    "Section Title": "Text only",
    "Another Section": "Text only"
  }}
}}

DOCUMENT:
{doc_snippet}
"""

    try:
        raw = run_llm(prompt)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group(0))
    except Exception:
        return {
            "status": "success",
            "sections": {"Summary": raw.strip()}
        }

    sections = data.get("sections", {})
    normalized = {}

    for k, v in sections.items():
        text = str(v).strip()
        text = re.sub(r'^[{\[]|[}\]]$', '', text)
        normalized[k] = text

    return {"status": "success", "sections": normalized}




# ================================================================
# Wrapper used by FastAPI (/summarize)
# ================================================================

def handle_summarize_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = generate_structured_section_summary(
        text=payload.get("text"),
        priorities=payload.get("priorities", []),
        output_format=payload.get("format", "bullets"),
        depth=payload.get("depth", "medium"),
    )

    if result.get("status") != "success":
        return result

    fmt = payload.get("format", "bullets")
    sections = result.get("sections", {})

    combined = []
    seen = set()

    for title, content in sections.items():
        content = content.strip()
        if not content or content.lower().startswith("not discussed"):
            continue

        if fmt == "bullets":
            combined.append(f"{title}:")
            combined.append(enforce_format(content, "bullets"))
        else:
            title_l = title.lower()
            text = content

            # Soft conclusion cue (Option B)
            if "conclusion" in title_l or "overall" in title_l or "summary" in title_l:
                text = f"Overall, {text[0].lower() + text[1:]}" if text else text

            if text not in seen:
                combined.append(text)
                seen.add(text)            

    narrative = (
        "\n".join(combined) if fmt == "bullets"
        else " ".join(s.rstrip(".") + "." for s in combined)
    )

    return {"status": "success", "narrative": narrative.strip()}


# -------------------------------------------------------------------
# NEW: SINGLE-SHOT FULL ANALYSIS (fast path for /upload)
# -------------------------------------------------------------------

def generate_full_analysis(text: str, doc_type: Optional[str] = None) -> Dict[str, Any]:
    """
    One LLM call that returns:
      - quick_preview (short bullet summary)
      - executive_summary (narrative)
      - themes (list[str])
      - key_insights (list[dict])
      - categories (list[dict])
      - follow_up_actions (list[str])

    This is the core of the "fast 3-call" architecture:
    /upload now uses this instead of 10+ separate LLM calls.
    """
    if not text:
        return {
            "quick_preview": "",
            "executive_summary": "",
            "themes": [],
            "key_insights": [],
            "categories": [],
            "follow_up_actions": [],
        }

    doc_snippet = text[:16000]
    type_hint = doc_type or "document"

    prompt = f"""
You are an assistant helping a professional user (banker / analyst / investor)
understand a single {type_hint} document quickly.

You must return a SINGLE JSON object capturing ALL of these fields:

{{
  "quick_preview": "4-6 bullet points, as a single string (you may format with '- ' bullets)",
  "executive_summary": "3-6 short paragraphs of narrative text (plain text, no bullets)",

  "themes": [
    "Short theme name 1",
    "Short theme name 2",
    "Short theme name 3"
  ],

  "key_insights": [
    {{
      "title": "2-7 word title",
      "summary": "1-3 sentence extractive summary based ONLY on the document.",
      "source_excerpt": "Short verbatim quote from the document that supports this insight (1-3 sentences)."
    }}
  ],

  "categories": [
    {{
      "key": "growth_drivers",      // stable machine-readable key
      "title": "Growth Drivers",    // label for UI
      "summary": "2-5 sentence summary of this aspect.",
      "snippet_texts": [
        "Short verbatim snippet from document relevant to this category",
        "Another snippet if useful"
      ]
    }}
  ],

  "follow_up_actions": [
    "User-friendly suggested follow-up question 1",
    "User-friendly suggested follow-up question 2"
  ]
}}

STRICT RULES:
- Use ONLY the provided document text. No external facts.
- Be conservative: if something is unclear, say less rather than hallucinate.
- Themes must be short (2-5 words).
- key_insights.source_excerpt and categories[*].snippet_texts[*]
  MUST be copied from the document (you may trim for brevity).
- Make follow_up_actions concrete and useful, like:
  - "Show me all key risks"
  - "Summarize financial performance"
  - "Extract key metrics and ratios"
  - "What guidance or outlook is discussed?"

Return ONLY valid JSON. No markdown, no commentary.

-----------------------------------------
DOCUMENT (BEGIN)
-----------------------------------------
{doc_snippet}
-----------------------------------------
DOCUMENT (END)
-----------------------------------------
"""

    try:
        raw = run_llm(prompt)
        raw = (raw or "").strip()
        logger.info("LLM returned (full_analysis raw): %s", raw[:2000])
    except Exception as e:
        logger.exception("LLM call failed in generate_full_analysis(): %s", e)
        raise

    # Robust JSON extraction
    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        json_str = match.group(0) if match else raw
        data = json.loads(json_str)
    except Exception as e:
        logger.error("Failed to parse JSON from full_analysis output: %s", e)
        raise

    # Normalize shapes a bit
    quick_preview = (data.get("quick_preview") or "").strip()
    executive_summary = (data.get("executive_summary") or "").strip()

    themes = data.get("themes") or []
    if not isinstance(themes, list):
        themes = []

    key_insights = data.get("key_insights") or []
    if not isinstance(key_insights, list):
        key_insights = []

    categories = data.get("categories") or []
    if not isinstance(categories, list):
        categories = []

    follow_up_actions = data.get("follow_up_actions") or []
    if not isinstance(follow_up_actions, list):
        follow_up_actions = []

    return {
        "quick_preview": quick_preview,
        "executive_summary": executive_summary,
        "themes": themes,
        "key_insights": key_insights,
        "categories": categories,
        "follow_up_actions": follow_up_actions,
    }
