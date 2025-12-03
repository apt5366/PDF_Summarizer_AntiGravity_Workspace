import re
from utils.llm import run_llm

CANONICAL_TYPES = {
    "contract": "contract",
    "annual_report": "annual_report",
    "quarterly_report": "quarterly_report",
    "earnings_call": "earnings_call",
    "market_analysis": "market_analysis",
    "mou": "mou",
    "sla": "sla",
    "general": "general",
}


# -------------------------------------------------------
# DEBUG logging helper
# -------------------------------------------------------
def debug(msg: str):
    print(f"\n🔍 [CLASSIFIER] {msg}\n")


# -------------------------------------------------------
# 1. DETERMINISTIC FAST RULE CLASSIFIER
# -------------------------------------------------------
def fast_rule_classifier(text: str) -> str | None:
    """Very fast keyword classifier — returns a label OR None."""
    t = text.lower()

    # CONTRACTS
    keywords_contract = [
        "agreement", "contract", "consultant agrees", "consultant shall",
        "scope of work", "scope of services", "indemnify", "hold harmless",
        "reimbursable expenses", "compensation is agreed"
    ]
    if any(k in t for k in keywords_contract):
        debug("✔ Rule match: CONTRACT")
        return "contract"

    # ANNUAL REPORTS (audited statements)
    keywords_annual = [
        "annual report", "auditor's report", "audited financial statements",
        "true and fair view", "frs 102", "non-statutory financial statements",
        "fiscal year", "corporate information"
    ]
    if any(k in t for k in keywords_annual):
        debug("✔ Rule match: ANNUAL REPORT")
        return "annual_report"

    # QUARTERLY REPORTS
    keywords_quarterly = [
        "quarterly report", "quarter ended", "three months ended",
        "q1", "q2", "q3", "q4",
        "qoq", "quarter-over-quarter", "financial summary for the quarter",
        "anticipated revenue growth for q"
    ]
    if any(k in t for k in keywords_quarterly):
        debug("✔ Rule match: QUARTERLY REPORT")
        return "quarterly_report"

    # EARNINGS CALLS
    keywords_call = [
        "earnings call", "operator:", "prepared remarks",
        "question-and-answer session", "welcome everyone to the call"
    ]
    if any(k in t for k in keywords_call):
        debug("✔ Rule match: EARNINGS CALL")
        return "earnings_call"

    # MARKET ANALYSIS
    keywords_market = [
        "market size", "industry outlook", "industry growth",
        "tam", "sam", "som", "competitive landscape",
        "swot analysis"
    ]
    if any(k in t for k in keywords_market):
        debug("✔ Rule match: MARKET ANALYSIS")
        return "market_analysis"

    # MOU
    if "memorandum of understanding" in t or "mou" in t:
        debug("✔ Rule match: MOU")
        return "mou"

    # SLA
    keywords_sla = [
        "service level agreement", "sla", "warranty",
        "security policy", "compliance policy", "terms and conditions"
    ]
    if any(k in t for k in keywords_sla):
        debug("✔ Rule match: SLA")
        return "sla"

    debug("❌ Rule-based classifier found NOTHING")
    return None



# -------------------------------------------------------
# 2. LLM FALLBACK CLASSIFIER
# -------------------------------------------------------
def llm_classifier(text: str) -> str:
    """Ask the local LLM to classify when rules cannot."""
    prompt = f"""
You are a document classifier.  
Return EXACTLY ONE category below as plain text:

contract  
annual_report  
quarterly_report  
earnings_call  
market_analysis  
mou  
sla  
general  

Output ONLY the category. Nothing else.

Document text:
{text[:4000]}
"""

    debug("🤖 Calling LLM classifier…")

    raw = run_llm(prompt).strip().lower()
    debug(f"🤖 LLM RAW OUTPUT: {raw}")

    # sanitize output
    for key in CANONICAL_TYPES:
        if key in raw:
            debug(f"✔ LLM classified as: {key}")
            return key

    debug("⚠ LLM output did not match any label. Returning GENERAL.")
    return "general"



# -------------------------------------------------------
# 3. HYBRID PIPELINE
# -------------------------------------------------------
def classify_document(text: str) -> str:
    """Try fast rules → fallback to LLM."""
    debug("========================================")
    debug("📄 NEW DOCUMENT RECEIVED FOR CLASSIFICATION")
    debug(f"📏 TEXT LENGTH: {len(text)} characters")

    # 1. Rule-based classification
    rule_label = fast_rule_classifier(text)
    if rule_label:
        debug(f"🏁 FINAL LABEL (RULES): {rule_label}")
        return CANONICAL_TYPES[rule_label]

    # 2. LLM fallback
    llm_label = llm_classifier(text)
    debug(f"🏁 FINAL LABEL (LLM): {llm_label}")

    return CANONICAL_TYPES.get(llm_label, "general")
