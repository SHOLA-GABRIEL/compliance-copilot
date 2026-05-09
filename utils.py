"""
utils.py
PDF text extraction and text preprocessing utilities.
"""

import io
import re
from typing import Generator


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract plain text from PDF bytes using pypdf.
    Falls back to an error message if extraction fails.
    """
    try:
        import pypdf

        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)

        full_text = "\n\n".join(pages)
        return _clean_text(full_text)

    except ImportError:
        # pypdf not installed — try pdfminer
        return _extract_with_pdfminer(pdf_bytes)
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def _extract_with_pdfminer(pdf_bytes: bytes) -> str:
    """Fallback extraction using pdfminer.six."""
    try:
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams
        import io as _io

        output = _io.StringIO()
        extract_text_to_fp(
            _io.BytesIO(pdf_bytes),
            output,
            laparams=LAParams(),
            output_type="text",
            codec="utf-8",
        )
        return _clean_text(output.getvalue())
    except Exception as e:
        return f"[PDF extraction fallback error: {e}]"


def _clean_text(text: str) -> str:
    """Normalize whitespace and remove junk characters."""
    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)
    # Remove control characters (except newlines/tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks for LLM processing.
    Returns a list of string chunks.
    """
    words = text.split()
    chunks = []
    i = 0
    chunk_words = chunk_size // 5  # rough words-per-chunk estimate

    while i < len(words):
        end = i + chunk_words
        chunk = " ".join(words[i:end])
        chunks.append(chunk)
        i += chunk_words - (overlap // 5)  # step back for overlap

    return chunks


def truncate_for_context(text: str, max_chars: int = 14000) -> str:
    """
    Intelligently truncate policy text to fit in context window.
    Preserves beginning (scope/purpose) and end (appendices often have controls).
    """
    if len(text) <= max_chars:
        return text

    half = max_chars // 2
    start = text[:half]
    end   = text[-half:]
    return start + "\n\n[... document truncated for analysis ...]\n\n" + end
