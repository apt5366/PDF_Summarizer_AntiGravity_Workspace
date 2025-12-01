from utils.llm import run_llm

def summarize_document(text: str, focus_areas=None, output_format="bullets", depth="quick"):
    """
    Summarize using local LLM. Configurable format and depth.
    """

    focus_str = ", ".join(focus_areas) if focus_areas else "General Overview"

    depth_map = {
        "quick": "100-150 words, concise bullet points",
        "medium": "200-300 words, more detail",
        "deep": "400-600 words, very detailed analysis"
    }

    format_map = {
        "bullets": "Return bullet points only.",
        "bullets_table": "Return bullet points followed by a simple 2-column table.",
        "narrative": "Return a well-structured narrative.",
        "json": "Return JSON only."
    }

    prompt = f"""
Summarize the document below.

Focus Areas: {focus_str}
Depth: {depth_map.get(depth, "150 words")}
Format Instruction: {format_map.get(output_format, "bullets only")}

Document:
{text[:8000]}

Begin summary now.
"""

    return run_llm(prompt, max_tokens=2048)
