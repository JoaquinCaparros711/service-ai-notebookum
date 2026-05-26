"""PDF extraction helpers for document uploads."""

from __future__ import annotations

from werkzeug.datastructures import FileStorage

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - import guard for environments without pypdf yet
    PdfReader = None


def is_pdf_upload(uploaded_file: FileStorage) -> bool:
    """Check whether the uploaded file looks like a PDF."""

    filename = (uploaded_file.filename or "").lower()
    mimetype = (uploaded_file.mimetype or "").lower()
    return mimetype == "application/pdf" or filename.endswith(".pdf")


def extract_text_from_pdf(uploaded_file: FileStorage) -> str:
    """Extract all readable text from the uploaded PDF stream."""

    if PdfReader is None:
        raise ValueError("PDF support is not available in this environment")

    uploaded_file.stream.seek(0)
    reader = PdfReader(uploaded_file.stream)
    pages_text = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages_text.append(page_text.strip())

    return "\n".join(pages_text).strip()