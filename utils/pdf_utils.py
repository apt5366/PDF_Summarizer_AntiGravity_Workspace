import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> str:
    """
    High-quality extraction using PyMuPDF.
    Preserves correct reading order much better than pypdf.
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

        print("\n========== PDF RAW TEXT SAMPLE ==========\n")
        print(final_text[:2000])
        print("\n=========== END RAW TEXT SAMPLE ==========\n")

        return final_text

    except Exception as e:
        return f"[PDF ERROR] {str(e)}"
