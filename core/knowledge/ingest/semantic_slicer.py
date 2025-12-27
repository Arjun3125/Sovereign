from typing import List, Dict, Callable, Tuple
import hashlib
import re

# Allowed semantic labels (STRICT)
ALLOWED_LABELS = {"story", "analogy", "principle", "example", "warning", "failure_case", "context"}


class SemanticSliceError(Exception):
    pass


def semantic_slice(
    section_text: str,
    llm_call: Callable[[str], str],
    max_chunk_chars: int = 1200,
    overlap_chars: int = 200,
) -> List[Dict]:
    """
    Slice a long section into semantic retrieval chunks using an LLM
    with strict guardrails. The LLM ONLY returns split boundaries + labels.

    Args:
        section_text: Raw text of a chapter/section (verbatim)
        llm_call: function(prompt: str) -> str (LLM response)
        max_chunk_chars: target maximum characters per slice
        overlap_chars: overlap to preserve narrative continuity

    Returns:
        List of dicts:
          - chunk_id
          - label
          - start
          - end
          - text (verbatim)
    """
    if not section_text or len(section_text) < max_chunk_chars:
        # Single chunk fallback
        return [_make_chunk(section_text, 0, len(section_text), "context")]

    prompt = _build_prompt(section_text, max_chunk_chars)
    response = llm_call(prompt)

    splits = _parse_llm_response(response)
    _validate_splits(splits, section_text)

    chunks: List[Dict] = []
    for i, (label, start, end) in enumerate(splits):
        s = max(0, start - overlap_chars)
        e = min(len(section_text), end + overlap_chars)
        chunk_text = section_text[s:e].strip()

        chunks.append(_make_chunk(chunk_text, s, e, label))

    return _dedupe_and_order(chunks)


# -------------------------
# Guardrail internals
# -------------------------

def _build_prompt(section_text: str, max_chunk_chars: int) -> str:
    """
    Prompt that constrains the LLM to ONLY propose split points and labels.
    """
    return f"""
You are a STRUCTURAL TEXT SLICER.
You MUST NOT summarize, paraphrase, interpret, or modify text.

Task:
- Propose split boundaries ONLY.
- Each split must be labeled from this exact set:
  {sorted(ALLOWED_LABELS)}
- Each chunk target size: <= {max_chunk_chars} characters (approx).
- Preserve narrative continuity (do not split mid-sentence if avoidable).

Output format (STRICT, one per line):
<label>|<start_index>|<end_index>

Rules:
- Indices refer to character positions in the ORIGINAL text below.
- No commentary. No extra text. No examples.
- Do NOT repeat or rewrite the text.
- Use as few chunks as possible while respecting size.

TEXT (do not modify):
<<<BEGIN>>>
{section_text}
<<<END>>>
""".strip()


def _parse_llm_response(response: str) -> List[Tuple[str, int, int]]:
    """
    Parse LLM response into (label, start, end).
    """
    lines = [l.strip() for l in response.splitlines() if l.strip()]
    splits: List[Tuple[str, int, int]] = []

    for line in lines:
        parts = line.split("|")
        if len(parts) != 3:
            raise SemanticSliceError(f"Invalid line format: {line}")

        label, start, end = parts
        label = label.strip()
        if label not in ALLOWED_LABELS:
            raise SemanticSliceError(f"Invalid label: {label}")

        try:
            start_i = int(start)
            end_i = int(end)
        except ValueError:
            raise SemanticSliceError(f"Invalid indices: {line}")

        if start_i < 0 or end_i <= start_i:
            raise SemanticSliceError(f"Invalid span: {line}")

        splits.append((label, start_i, end_i))

    if not splits:
        raise SemanticSliceError("No valid splits returned by LLM")

    return splits


def _validate_splits(splits: List[Tuple[str, int, int]], text: str) -> None:
    """
    Validate splits do not exceed bounds and do not overlap incorrectly.
    """
    text_len = len(text)
    last_end = 0

    for label, start, end in splits:
        if end > text_len:
            raise SemanticSliceError("Split exceeds text length")
        if start < last_end:
            # Allow small overlap only if contiguous slicing was intended
            if start + 5 < last_end:
                raise SemanticSliceError("Non-contiguous or overlapping splits")
        last_end = end


def _make_chunk(text: str, start: int, end: int, label: str) -> Dict:
    """
    Create a chunk with a deterministic ID and verbatim text.
    """
    chunk_id = _hash_id(text, start, end, label)
    return {
        "chunk_id": chunk_id,
        "label": label,
        "start": start,
        "end": end,
        "text": text,  # VERBATIM
    }


def _hash_id(text: str, start: int, end: int, label: str) -> str:
    h = hashlib.sha256()
    h.update(label.encode("utf-8"))
    h.update(str(start).encode("utf-8"))
    h.update(str(end).encode("utf-8"))
    h.update(text[:128].encode("utf-8"))  # small prefix only
    return h.hexdigest()[:16]


def _dedupe_and_order(chunks: List[Dict]) -> List[Dict]:
    """
    Remove duplicates (by chunk_id) and order by start index.
    """
    seen = {}
    for c in chunks:
        seen[c["chunk_id"]] = c
    ordered = sorted(seen.values(), key=lambda x: x["start"])
    return ordered


# -------------------------
# Smoke test helper
# -------------------------

if __name__ == "__main__":
    # Minimal fake LLM for smoke testing
    def fake_llm(prompt: str) -> str:
        # Example: split into two chunks
        return "context|0|400\nprinciple|400|800"

    sample = "A" * 900
    chunks = semantic_slice(sample, fake_llm)
    for c in chunks:
        print(c["label"], c["start"], c["end"], len(c["text"]))
