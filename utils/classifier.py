from utils.llm import run_llm

LABELS = [
    "Legal Contract",
    "Automotive Checklist",
    "Consumer Guide",
    "Business Document",
    "Financial Report",
    "Technical Manual",
    "HR Policy",
    "Marketing Document",
    "Other"
]

def classify_document(text: str) -> str:
    """
    Force the LLM to return exactly one label from LABELS.
    """

    prompt = f"""
You are a document classifier. 

Classify the document into EXACTLY ONE of these categories:
{", ".join(LABELS)}

Rules:
- ONLY answer with the category name.
- No sentences. No explanation. Just the label.

Document Text:
{text[:3000]}  # limit for classification
"""

    result = run_llm(prompt)
    result = result.strip()

    # sanitize
    for lbl in LABELS:
        if lbl.lower() in result.lower():
            return lbl

    return "Other"
