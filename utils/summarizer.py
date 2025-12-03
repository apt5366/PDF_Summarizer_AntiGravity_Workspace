from utils.llm import run_llm


def summarize_document(
    text: str,
    focus_areas: list[str] = None,
    output_format: str = "bullets",
    depth: str = "quick"
):
    """
    High-quality, extractive-first summarization.
    Uses ONLY the provided text. Includes focus-area weighting.
    """
    if focus_areas is None:
        focus_areas = []

    # ----------------------------------------------------
    # FORMAT TEMPLATES
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # FOCUS WEIGHTING
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # FINAL PROMPT
    # ----------------------------------------------------
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
{text[:8000]}
-----------------------------------------
DOCUMENT TO SUMMARIZE (END)
-----------------------------------------

Now return the final summary.
"""

    summary = run_llm(prompt).strip()
    return summary



# ==========================================================
#   NEW FEATURE: AUTOMATIC KEY THEME EXTRACTION (Step 2)
# ==========================================================

def extract_key_themes(text: str):
    """
    Extract the 3–6 key themes from the document.
    Must be EXTRACTIVE — no hallucinations.
    """

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
{text[:8000]}
-----------------------------------------
DOCUMENT (END)
-----------------------------------------
"""

    result = run_llm(theme_prompt)
    return result.strip()
