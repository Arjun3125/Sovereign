"""PDF reader for ingest_v2.

Supports:
- Direct .txt file reading
- PDF parsing via PyPDF2 (if available)
- Fallback to .txt sibling file
"""
from pathlib import Path


def extract_text(pdf_path: str) -> str:
    """Extract text from PDF or text file.
    
    Args:
        pdf_path: Path to PDF or .txt file
    
    Returns:
        Extracted text as string
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If extraction fails
    """
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")
    
    # If it's already a .txt file, read it directly
    if p.suffix.lower() == '.txt':
        return p.read_text(encoding='utf-8')
    
    # Try to find a .txt sibling file first
    txt_path = p.with_suffix('.txt')
    if txt_path.exists():
        return txt_path.read_text(encoding='utf-8')
    
    # Try PyPDF2 for PDF parsing
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            text = '\n'.join(text_parts)
            if text and len(text.strip()) > 50:
                return text
    except ImportError:
        pass  # PyPDF2 not available
    except Exception as e:
        # PDF parsing failed, try other methods
        pass
    
    # Try pdfplumber as alternative
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text_parts = []
            for page in pdf.pages:
                text_parts.append(page.extract_text() or '')
            text = '\n'.join(text_parts)
            if text and len(text.strip()) > 50:
                return text
    except ImportError:
        pass  # pdfplumber not available
    except Exception as e:
        pass
    
    # If all else fails, raise an error with helpful message
    raise ValueError(
        f"Could not extract text from {pdf_path}. "
        f"Options:\n"
        f"1. Install PyPDF2: pip install PyPDF2\n"
        f"2. Install pdfplumber: pip install pdfplumber\n"
        f"3. Create a .txt file with the same name: {txt_path}"
    )
