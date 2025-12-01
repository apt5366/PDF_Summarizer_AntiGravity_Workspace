from pypdf import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    """
    Clean text extraction from PDF.
    Keeps paragraphs, removes broken newlines.
    """
    try:
        reader = PdfReader(file_path)
        raw_text = []

        for page in reader.pages:
            text = page.extract_text()
            if not text:
                continue

            # Fix broken words + excessive newlines
            cleaned = (
                text.replace("\n", " ")
                    .replace("  ", " ")
                    .strip()
            )
            raw_text.append(cleaned)

        return "\n\n".join(raw_text)

    except Exception as e:
        return f"[PDF ERROR] {str(e)}"
