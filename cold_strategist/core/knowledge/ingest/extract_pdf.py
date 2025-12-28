from pathlib import Path
from typing import Optional
import re

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


def extract_pdf_text(
    pdf_path: str | Path,
    output_txt: Optional[str | Path] = None,
) -> str:
    """
    Extract raw text from a PDF file without interpretation.

    Args:
        pdf_path: Path to source PDF
        output_txt: Optional path to write extracted text

    Returns:
        Extracted raw text as a string
    """
    if not HAS_PYPDF2:
        # Fallback: try .txt file alongside PDF
        pdf_path = Path(pdf_path)
        txt_path = pdf_path.with_suffix('.txt')
        if txt_path.exists():
            return txt_path.read_text(encoding='utf-8')
        raise ImportError(
            "PyPDF2 is required for PDF extraction. Install with: pip install PyPDF2"
        )
    
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    pages_text = []

    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages_text.append(text)

    raw_text = "\n\n".join(pages_text)

    # Minimal normalization only (do NOT summarize or rewrite)
    raw_text = _normalize_whitespace(raw_text)

    if output_txt:
        output_txt = Path(output_txt)
        output_txt.parent.mkdir(parents=True, exist_ok=True)
        output_txt.write_text(raw_text, encoding="utf-8")

    return raw_text


def _normalize_whitespace(text: str) -> str:
    """
    Normalize excessive whitespace while preserving content.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <input.pdf> [output.txt]")
        sys.exit(1)

    pdf = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None

    text = extract_pdf_text(pdf, out)
    print(f"Extracted {len(text)} characters.")
