import re


def normalize(text: str) -> str:
    """Normalize text for comparison: lowercase, remove punctuation, deduplicate spaces.
    
    Pure mechanical normalization. No interpretation.
    
    Args:
        text: Raw text to normalize.
        
    Returns:
        Normalized text.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
