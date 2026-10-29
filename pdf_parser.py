import pymupdf as fitz  # PyMuPDF


def extract_text_from_pdf(file):
    """Extract text from a PDF file object (open file or Streamlit upload).

    Text is read in reading order (sorted blocks), like most ATS parsers do.
    """
    data = file.read()
    if hasattr(file, "seek"):
        file.seek(0)

    parts = []
    with fitz.open(stream=data, filetype="pdf") as doc:
        for page in doc:
            parts.append(page.get_text("text", sort=True))

    return "\n".join(parts).strip()
