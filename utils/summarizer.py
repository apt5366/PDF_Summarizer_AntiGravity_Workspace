import logging
import re
from typing import List
from utils.llm import run_llm

logger = logging.getLogger("antigravity.summarizer")
logging.basicConfig(level=logging.INFO)


def summarize_document(
    text: str,
    focus_areas: List[str] = None,
    output_format: str = "bullets",
    depth: str = "quick"
):
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

    prompt = f"""
You are an **EXTRACTIVE summarization model**.

Your job is to summarize ONLY the text provided. 
STRICT RULES:
- DO NOT guess or invent information.
- DO NOT add data that is not explicitly present in the text.
- DO NOT generalize beyond the document.
- If a focus area has no coverage in the text, clearly state: "Not discussed in the document."

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
        return out
    except Exception as e:
        logger.exception("Error calling run_llm in summarize_document(): %s", e)
        raise


# -------------------------
# Helper parsing & fallbacks
# -------------------------
def _parse_bulleted_text_to_list(raw: str) -> List[str]:
    if not raw:
        return []

    normalized = raw.replace("•", "-").replace("\u2022", "-")
    lines = [l.strip() for l in normalized.splitlines() if l.strip()]
    themes = []

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

    cleaned = []
    for t in themes:
        s = re.sub(r'^[\-\d\).\s]+', '', t).strip()
        s = s.strip('"\'' )  # remove surrounding quotes
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
    freq = {}
    for w in words:
        if w in stop:
            continue
        freq[w] = freq.get(w, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda x: -x[1])
    themes = [w for w, _ in sorted_words[:max_items]]
    return [t.title() for t in themes if t]


# -------------------------
# Post-processing utilities
# -------------------------
def _strip_parenthetical(s: str) -> str:
    # remove parenthetical content like "(FRS 102, Companies Act 2014)"
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
        return "Financial Presentation"
    if "going concern" in low:
        return "Going Concern"
    if "director" in low or "governance" in low:
        return "Governance / Directors"
    if "risk" in low:
        return "Risk Factors"
    return s


def _normalize_and_dedupe(items: List[str], max_items: int = 6) -> List[str]:
    seen = set()
    out = []
    for raw in items:
        text = raw.strip()
        if not text:
            continue
        text = _strip_parenthetical(text)
        text = re.sub(r'[^\w\s\-\&\/]', '', text)  # remove stray punctuation except - & /
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


# -------------------------
# Main theme extraction
# -------------------------
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

    # If the LLM returned some items, normalize and dedupe them
    if parsed:
        processed = _normalize_and_dedupe(parsed, max_items=6)
        # If normalization produced fewer than 3, attempt to supplement with original parsed items
        if len(processed) < 3:
            supplement = [p for p in parsed if p.lower() not in (x.lower() for x in processed)]
            processed.extend(supplement[: (3 - len(processed))])
        if len(processed) >= 1:
            return processed[:6]

    # If nothing usable from LLM, fallback to simple frequency-based themes
    fallback = _simple_freq_fallback(text, max_items=6)
    if fallback:
        # Apply friendly mapping and shorting to fallback tokens as well
        fallback = _normalize_and_dedupe(fallback, max_items=6)
        return fallback[:6]

    return []
