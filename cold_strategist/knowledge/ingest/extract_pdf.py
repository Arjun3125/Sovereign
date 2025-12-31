from pathlib import Path


def extract_pdf(pdf_path: Path, out_path: Path):
    """Extract text from PDF preserving page numbers.

    Tries `pdfplumber` first; falls back to `PyPDF2` if available. If neither
    is installed or the file is unreadable, logs a skip and returns False.
    """
    out = []
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                out.append({"page": i + 1, "text": text.strip()})
    except Exception:
        # fallback to PyPDF2
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(str(pdf_path))
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text() or ""
                except Exception:
                    text = ""
                out.append({"page": i + 1, "text": text.strip()})
        except Exception as e:
            # Could be missing libraries or a corrupt PDF; skip this file.
            print(f"[SKIP] {pdf_path.name}: {e}")
            return False

    if not out:
        print(f"[SKIP] {pdf_path.name}: no text extracted")
        return False

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n\n".join(f"[PAGE {p['page']}]\n{p['text']}" for p in out), encoding="utf-8")
    return True
