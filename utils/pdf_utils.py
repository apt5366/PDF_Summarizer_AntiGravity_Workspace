import fitz  # PyMuPDF
import logging

logger = logging.getLogger("antigravity.pdf_utils")


def extract_text_from_pdf(file_path: str) -> str:
    """
    High-quality extraction using PyMuPDF.
    Preserves correct reading order much better than pypdf.
    Returns a single concatenated text string.
    """

    try:
        doc = fitz.open(file_path)
        blocks = []

        for page in doc:
            text = page.get_text("text")
            if text:
                cleaned = (
                    text.replace("\t", " ")
                        .replace("  ", " ")
                        .strip()
                )
                blocks.append(cleaned)

        final_text = "\n\n".join(blocks)

        # Debug sample
        print("\n========== PDF RAW TEXT SAMPLE ==========\n")
        print(final_text[:2000])
        print("\n=========== END RAW TEXT SAMPLE ==========\n")

        return final_text

    except Exception as e:
        logger.error("PDF extraction error in extract_text_from_pdf: %s", e)
        return ""


def extract_text_by_page(file_path: str) -> list[str]:
    """
    Returns a list of page-level text strings.
    Used for approximate page-level citation matching.
    """

    pages: list[str] = []

    try:
        doc = fitz.open(file_path)

        for page in doc:
            text = page.get_text("text") or ""
            cleaned = (
                text.replace("\t", " ")
                    .replace("  ", " ")
                    .strip()
            )
            pages.append(cleaned)

    except Exception as e:
        logger.error("PDF extraction error in extract_text_by_page: %s", e)
        return []

    return pages
