import json
import sys
import os
import tempfile
from pathlib import Path
from typing import Any, Dict
import re

from cold_strategist.core.llm.ollama_client import OllamaClient
from cold_strategist.ingest_v2.pdf_reader import extract_text
from concurrent.futures import ThreadPoolExecutor
from threading import Lock


# =========================
# CONFIG (AUTHORITATIVE)
# =========================

BASE_DIR = Path(__file__).resolve().parent

WORKSPACE_DIR = BASE_DIR / "workspace"
INPUT_BOOKS_DIR = BASE_DIR / "input" / "books"

# Deterministic model choice — wired to Ollama via existing client
INGESTION_TEMPERATURE = 0.0
INGESTION_MAX_TOKENS = 4096

# Ingestion model for Phase runs (PR / ingestion)
# Use instruction/completion model for Phase-1A (boundary detection)
INGESTION_MODEL = "llama3.1:8b-instruct-q4_0"

# Streaming / merger constants
WINDOW_SIZE = 9000
WINDOW_OVERLAP = 500
MERGE_WINDOW = 300


# =========================
# TEXT CLEANING
# =========================

def clean_extracted_text(text: str) -> str:
    """Clean PDF-extracted text that has been corrupted with extra spaces.
    
    Some PDFs extract with spaces between every character (e.g., "T h e" instead of "The").
    When corruption is detected (>70% single-char words), this aggressively removes inter-character
    spaces and then re-adds spaces at natural boundaries (punctuation, numbers, etc).
    """
    if not text:
        return text
    
    # Sample check: are most "words" single characters?
    lines = text.split('\n')[:100]  
    
    single_char_word_count = 0
    total_word_count = 0
    
    for line in lines:
        if len(line) < 10:
            continue
        
        words = [w for w in line.split(' ') if w]
        if not words:
            continue
        
        total_word_count += len(words)
        single_char_word_count += sum(1 for w in words if len(w) == 1)
    
    if total_word_count == 0:
        return text
    
    corruption_ratio = single_char_word_count / total_word_count
    
    # If >70% of words are single characters, the text is corrupted
    if corruption_ratio > 0.7:
        # Aggressive join: remove most spaces, then add them back only at real boundaries
        words = text.split()  # Split on all whitespace
        
        # Join all non-empty words
        combined = ''.join(w for w in words if w)
        
        # Now carefully re-add spaces at real word boundaries
        result = []
        for i, char in enumerate(combined):
            result.append(char)
            
            if i < len(combined) - 1:
                next_char = combined[i + 1]
                
                # Add space before capital letters (word boundaries)
                if next_char.isupper() and i > 0 and result[-2:] != [' ', '']:
                    # But NOT if the previous char is already a space or punc
                    if result[-1] not in (' ', '\n', '(', '[', '{'):
                        # Also check: if prev is lowercase and next is uppercase, add space
                        if char.islower():
                            result.append(' ')
                
                # Add space after punctuation (word boundaries)
                elif char in '.,;:!?)' and next_char not in (' ', '\n', ')', ']', '}'):
                    result.append(' ')
                
                # Add space after digit followed by non-digit letter
                elif char.isdigit() and next_char.isalpha() and not combined[max(0, i-1)].isdigit():
                    result.append(' ')
        
        return ''.join(result)
    
    return text


# =========================
# PROMPTS (EMBEDDED, AUTHORITATIVE)
# =========================

PHASE1_SYSTEM_PROMPT = '''You are a boundary detection engine.

Your ONLY task is to detect chapter boundaries in the provided text window.

STRICT RULES:
- Do NOT summarize.
- Do NOT paraphrase.
- Do NOT rewrite text.
- Do NOT invent chapters.
- Do NOT infer structure.
- Do NOT output chapter text.
- Do NOT explain your reasoning.

IMPORTANT NOTE:
Some books are structured as numbered laws, principles, or aphorisms (e.g., "Law 1", "Law 2", "Principle I", etc.).
If such a structure is present in the text, treat EACH numbered law/principle as its own chapter.
Do NOT merge multiple numbered items into one chapter.

You MUST:
- Detect ONLY explicit chapter boundaries present in the text.
- A boundary exists ONLY if a chapter heading or section heading is explicitly written.
- Report the EXACT location where the chapter starts.

OUTPUT FORMAT (JSON ONLY):

{
    "boundaries": [
        {
            "type": "chapter_start",
            "title": "<exact heading text>",
            "page": <page_number_if_present_else_null>,
            "char_offset": <absolute_character_offset>,
            "confidence": <0.0–1.0>
        }
    ]
}

If NO boundary exists in the text window, output:

{
    "boundaries": []
}

ABSOLUTE CONSTRAINTS:
- Output ONLY valid JSON.
- If uncertain, return an empty list.
- Silence is preferred over error.

If a boundary exists, you MUST output JSON. Empty output is not permitted.'''


PHASE1_USER_TEMPLATE = '''[WINDOW_START_OFFSET = {absolute_char_offset}]

The following is a continuous excerpt from a book.
Page numbers may be included.

Detect whether a chapter starts in this window.

{text_window}
'''


PHASE2_SYSTEM_PROMPT = '''You are a doctrine extraction engine.

Your task is to extract doctrine from ONE complete chapter of a book.

STRICT RULES:
- Use ONLY the provided chapter text.
- Do NOT summarize the chapter.
- Do NOT add external knowledge.
- Do NOT merge or generalize ideas.
- Do NOT return empty doctrine unless the chapter truly contains none.

You MUST:
- Select relevant domains from the allowed list.
- Extract doctrine in ALL required fields.
- Use clear, atomic sentences.
- Return ONLY plain strings (no objects, no metadata).

At minimum, the output MUST contain:
- At least ONE domain
- At least ONE principle OR rule
- At least ONE claim OR warning

If you violate the schema, the output will be rejected.
Output MUST be valid JSON and MUST match the schema exactly.'''


PHASE2_USER_TEMPLATE = '''ALLOWED DOMAINS:
- Strategy
- Power
- Conflict & Force
- Deception
- Psychology
- Leadership
- Organization & Discipline
- Intelligence & Information
- Timing
- Risk & Survival
- Resources & Logistics
- Law & Order
- Morality & Legitimacy
- Diplomacy & Alliances
- Adaptation & Change

CHAPTER INPUT:

Chapter Index: {chapter_index}
Chapter Code: {chapter_code}

<<<CHAPTER_TEXT_START>>>
{chapter_text}
<<<CHAPTER_TEXT_END>>>

Return ONLY valid JSON using this schema:

{
  "chapter_index": {chapter_index},
  "chapter_title": "{chapter_title}",
  "domains": [],
  "principles": [],
  "rules": [],
  "claims": [],
  "warnings": [],
  "cross_references": []
}
'''


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        hard_fail(f"Failed to read prompt file {path}: {exc}")


def save_json(path: Path, obj: Any) -> None:
    atomic_write_text(path, json.dumps(obj, indent=2, ensure_ascii=False))


def atomic_write_text(path: Path, text: str) -> None:
    """Write text to `path` atomically using a temp file and os.replace.

    Ensures the parent directory exists. Uses a tempfile in the same
    directory to avoid cross-filesystem rename issues, then replaces
    the destination atomically. Falls back to direct write on PermissionError.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # Create a temp file in the same directory for atomic replace
    fd, tmp = tempfile.mkstemp(dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        # atomic replace (works on Windows and POSIX)
        try:
            os.replace(tmp, str(path))
        except PermissionError:
            # Fallback: clean up temp and do direct write
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass
            print(f"[atomic_write_text] PermissionError on atomic replace; falling back to direct write: {path}")
            path.write_text(text, encoding="utf-8")
    except Exception:
        # clean up temp file if something went wrong
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
        raise


def normalize_whitespace(s: str) -> str:
    return " ".join(s.split())


def hard_fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(1)


def ensure_not_exists(path: Path) -> None:
    if path.exists():
        hard_fail(f"Pipeline violation: output file already exists: {path}")


def extract_first_json(text: str) -> str | None:
    """
    Deterministically extract the first valid JSON object from text.
    Returns the JSON substring or None if not found.
    """
    if not text:
        return None
    t = text.strip()
    if t.startswith("{") and t.endswith("}"):
        return t

    stack = []
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if start is None:
                start = i
            stack.append("{")
        elif ch == "}":
            if stack:
                stack.pop()
                if not stack and start is not None:
                    return text[start:i + 1]
    return None


ROMAN_RE = re.compile(r'^[IVXLCDM]+\.?$')


def is_roman(s: str) -> bool:
    if not s:
        return False
    s = s.strip().upper().replace(" ", "")
    return bool(ROMAN_RE.match(s))


def normalize_title(candidate: str, chapter_text: str) -> Dict[str, str]:
    """Return normalized title and roman metadata.

    Rules:
    - Strip lines >80 chars
    - Reject titles containing ebook/publishing/ISBN
    - Prefer roman numerals alone (kept as roman metadata)
    - Otherwise prefer next non-empty uppercase line in chapter_text
    """
    bad_tokens = ("ebook", "publishing", "isbn")
    # Clean candidate
    if candidate:
        lines = [l.strip() for l in candidate.splitlines() if l.strip()]
        # choose first short line under 80 chars
        for l in lines:
            if len(l) > 80:
                continue
            low = l.lower()
            if any(t in low for t in bad_tokens):
                continue
            # if Roman numeral only, record as roman metadata and find better title
            if is_roman(l):
                roman = l.strip().rstrip('.')
                # try to find next uppercase header in chapter_text
                header = _find_uppercase_header(chapter_text)
                return {"title": header or roman, "roman": roman}
            return {"title": l, "roman": None}

    # Candidate missing or rejected — scan chapter_text for uppercase header
    header = _find_uppercase_header(chapter_text)
    if header:
        # if header is roman, keep as roman and try next header
        if is_roman(header):
            roman = header.strip().rstrip('.')
            alt = _find_uppercase_header(chapter_text, skip=header)
            return {"title": alt or roman, "roman": roman}
        return {"title": header, "roman": None}

    return {"title": candidate or None, "roman": None}


def _find_uppercase_header(text: str, skip: str = None) -> str | None:
    for line in text.splitlines():
        l = line.strip()
        if not l or (skip and l == skip):
            continue
        # reject long lines
        if len(l) > 80:
            continue
        # must be mostly uppercase and short
        letters = [c for c in l if c.isalpha()]
        if not letters:
            continue
        up_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        if up_ratio > 0.6 and len(l) < 80:
            low = l.lower()
            if any(t in low for t in ("ebook", "publishing", "isbn")):
                continue
            return l
    return None


# Canonical minister domains
CANONICAL_DOMAINS = [
    "Strategy",
    "Power",
    "Conflict & Force",
    "Deception",
    "Psychology",
    "Leadership",
    "Organization & Discipline",
    "Intelligence & Information",
    "Timing",
    "Risk & Survival",
    "Resources & Logistics",
    "Law & Order",
    "Morality & Legitimacy",
    "Diplomacy & Alliances",
    "Adaptation & Change",
]

DOMAIN_RULES = {
    "Deception": ["deception", "feign", "mislead", "appear", "conceal", "bait", "spy", "spies"],
    "Intelligence & Information": ["spy", "information", "knowledge", "signals", "reports"],
    "Timing": ["delay", "haste", "before", "after", "moment", "time"],
    "Risk & Survival": ["danger", "ruin", "destruction", "exhausted", "loss"],
    "Organization & Discipline": ["discipline", "order", "command", "control", "formation"],
    "Psychology": ["fear", "morale", "confidence", "anger", "temper"],
    "Resources & Logistics": ["supplies", "provisions", "plunder", "resources"],
}


def refine_domains(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministically refine and correct domains based on doctrine text.

    - Ensures only canonical domains are used
    - Infers additional domains from keywords
    - Removes 'Strategy' if others present
    - Enforces presence of Deception/Intelligence when related keywords found
    """
    # Safely extract text from all doctrine fields, handling both strings and dicts
    def extract_text_items(items):
        result = []
        for item in (items or []):
            if isinstance(item, dict):
                if "claim" in item:
                    result.append(str(item["claim"]))
                elif "principle" in item:
                    result.append(str(item["principle"]))
            elif isinstance(item, str):
                result.append(item)
        return result
    
    all_text = (
        extract_text_items(parsed.get("principles") or []) +
        extract_text_items(parsed.get("rules") or []) +
        extract_text_items(parsed.get("claims") or []) +
        extract_text_items(parsed.get("warnings") or [])
    )
    text = " ".join(all_text).lower()

    inferred = set()
    for d in parsed.get("domains", []) or []:
        if d in CANONICAL_DOMAINS:
            inferred.add(d)

    for domain, keywords in DOMAIN_RULES.items():
        for k in keywords:
            if k in text:
                inferred.add(domain)
                break

    # Strategy is allowed only if no other domain fits
    if inferred and inferred != {"Strategy"}:
        inferred.discard("Strategy")

    # Enforce domain minimums: if deception/spy words present, ensure Deception or Intelligence present
    if any(k in text for k in ("deception", "spy", "spies", "mislead")):
        if not ("Deception" in inferred or "Intelligence & Information" in inferred):
            inferred.add("Deception")

    # Ensure deterministic ordering
    parsed["domains"] = sorted([d for d in CANONICAL_DOMAINS if d in inferred])
    return parsed


# =========================
# OLLAMA CALL
# =========================


def ollama_generate(client: OllamaClient, system_prompt: str, user_prompt: str) -> str:
    # Deterministic raw generation via /api/generate for ingestion tasks
    return client.generate_raw(
        prompt=user_prompt,
        system=system_prompt,
        temperature=INGESTION_TEMPERATURE,
        max_tokens=INGESTION_MAX_TOKENS,
        top_p=1.0,
        stream=False,
    )


# =========================
# PHASE 1 — BOOK → CHAPTERS
# =========================


def validate_phase1_schema(parsed: Dict[str, Any]) -> None:
    if not isinstance(parsed, dict):
        hard_fail("Phase-1 output must be a JSON object")
    for key in ("book_title", "chapters"):
        if key not in parsed:
            hard_fail(f"Phase-1 missing required key: {key}")
    if not isinstance(parsed["chapters"], list) or len(parsed["chapters"]) == 0:
        hard_fail("Phase-1 chapters must be a non-empty list")
    for ch in parsed["chapters"]:
        # chapter_title is intentionally optional — we prefer a deterministic chapter_code instead
        if not all(k in ch for k in ("chapter_index", "chapter_text")):
            hard_fail("Phase-1 chapter entries must contain chapter_index and chapter_text")


def annotate_boundaries(text: str) -> str:
    """Add non-destructive boundary markers (===BOUNDARY===) to annotate obvious list structures.
    
    This helps the LLM recognize numbered laws, principles, chapters, etc. without
    modifying the actual text content.
    """
    patterns = [
        r"\bLAW\s+\d+\b",
        r"\bLaw\s+\d+\b",
        r"\bCHAPTER\s+\d+\b",
        r"\bChapter\s+\d+\b",
        r"\bPRINCIPLE\s+[IVX]+\b",
        r"\bPrinciple\s+[IVX]+\b",
    ]
    annotated = text
    for p in patterns:
        annotated = re.sub(p, r"\n\n===BOUNDARY===\n\n\g<0>", annotated)
    return annotated


def phase1a_scan_windows(client: OllamaClient, book_text: str, *, window_size: int = WINDOW_SIZE, overlap: int = WINDOW_OVERLAP) -> list:
    """Scan book_text in sliding windows and collect pointer-only boundaries.

    Returns a list of boundary dicts as reported by the model. Robustly logs
    non-JSON or empty responses for debugging.
    """
    text_len = len(book_text)
    step = max(1, window_size - overlap)
    boundaries = []

    windows = []
    for start in range(0, text_len, step):
        end = min(start + window_size, text_len)
        windows.append((start, end, book_text[start:end]))

    total_windows = len(windows)
    for idx, (start, end, wtext) in enumerate(windows, start=1):
        user_prompt = PHASE1_USER_TEMPLATE.format(absolute_char_offset=start, text_window=wtext)
        try:
            raw_output = ollama_generate(client, PHASE1_SYSTEM_PROMPT, user_prompt)
        except Exception as exc:
            print(f"[Phase-1A] window {idx}/{total_windows} error: {exc}")
            continue

        if not raw_output or not raw_output.strip():
            print(f"[Phase-1A] window {idx}/{total_windows} empty response; ignoring")
            continue

        try:
            parsed = json.loads(raw_output)
        except Exception:
            print(f"[Phase-1A] window {idx}/{total_windows} returned non-JSON (start={start}): {raw_output[:300]}")
            continue

        if not isinstance(parsed, dict) or "boundaries" not in parsed:
            print(f"[Phase-1A] window {idx}/{total_windows} invalid schema; ignoring")
            continue

        found = 0
        for b in parsed.get("boundaries", []) or []:
            try:
                off = int(b.get("char_offset", 0))
            except Exception:
                continue
            if off < start or off > end:
                continue
            b["char_offset"] = off
            try:
                b["confidence"] = float(b.get("confidence", 0.0))
            except Exception:
                b["confidence"] = 0.0
            boundaries.append(b)
            found += 1

        print(f"[Phase-1A] window {idx}/{total_windows} scanned, found {found} boundaries")

    return boundaries


def check_under_segmentation(consolidated: list, book_text: str) -> bool:
    """Check if a list-structured book (e.g., 48 Laws) is under-segmented.
    
    Returns True if under-segmentation is detected (for retry logic).
    """
    # Count numbered laws/principles in the raw text
    law_count = len(re.findall(r"\b(?:Law|Chapter|Principle)\s+\d+", book_text, re.IGNORECASE))
    boundary_count = len(consolidated)
    
    # If we found many numbered items but very few boundaries, it's likely under-segmented
    if law_count >= 30 and boundary_count < (law_count * 0.7):
        return True
    return False


def consolidate_boundaries(boundaries: list, *, min_gap: int = 50) -> list:
    """Consolidate, sort, deduplicate and validate pointer list.

    Strategy: sort by offset, merge entries within `min_gap` choosing highest confidence.
    """
    if not boundaries:
        return []
    # ensure numeric confidence
    for b in boundaries:
        try:
            b["confidence"] = float(b.get("confidence", 0.0))
        except Exception:
            b["confidence"] = 0.0

    boundaries = sorted(boundaries, key=lambda x: x["char_offset"])
    consolidated = [boundaries[0]]
    for b in boundaries[1:]:
        last = consolidated[-1]
        if abs(b["char_offset"] - last["char_offset"]) <= min_gap:
            # pick the one with higher confidence
            if b["confidence"] > last.get("confidence", 0):
                consolidated[-1] = b
        else:
            consolidated.append(b)

    # enforce monotonic increasing offsets
    consolidated = sorted(consolidated, key=lambda x: x["char_offset"])
    return consolidated


def build_chapters_from_boundaries(boundaries: list, book_text: str) -> Dict[str, Any]:
    """Create chapter structures (with start/end offsets and chapter_text) from boundaries.

    If no boundaries found, emit a single chapter covering the full book.
    """
    if not boundaries:
        return {
            "book_title": None,
            "author": None,
            "chapters": [
                {"chapter_index": 1, "chapter_title": None, "start_offset": 0, "end_offset": len(book_text), "chapter_text": book_text}
            ]
        }

    starts = [b for b in boundaries if b.get("type") == "chapter_start"]
    if not starts:
        # fallback: treat first boundary as start
        starts = boundaries

    starts = sorted(starts, key=lambda x: x["char_offset"])
    chapters = []
    for i, s in enumerate(starts):
        start_off = s["char_offset"]
        end_off = starts[i+1]["char_offset"] if i+1 < len(starts) else len(book_text)
        text_slice = book_text[start_off:end_off]

        # Normalize title deterministically and capture roman metadata
        candidate = s.get("title")
        normalized = normalize_title(candidate, text_slice)
        # DO NOT expose a human-readable chapter title here — provide a deterministic code instead
        chapter_code = f"C{i+1:03d}"
        roman = normalized.get("roman")

        chapters.append({
            "chapter_index": i+1,
            "chapter_code": chapter_code,
            "chapter_title": None,
            "heading_roman": roman,
            "start_offset": start_off,
            "end_offset": end_off,
            "chapter_text": text_slice,
        })

    return {"book_title": None, "author": None, "chapters": chapters}


def heuristic_find_headings(text: str) -> list:
    """Simple deterministic fallback to find likely chapter headings in the raw text.

    Looks for lines that are all-caps, lines starting with 'Chapter' or a leading
    numeral/roman followed by a dot. Returns a list of boundary dicts.
    """
    candidates = []
    for m in re.finditer(r"(?m)^(?:Chapter\b|CHAPTER\b|[0-9]{1,2}\\.|[IVXLCDM]{1,4}\\.)\s*(.*)$", text):
        start = m.start()
        title = m.group(0).strip()
        candidates.append({"type": "chapter_start", "title": title, "char_offset": start, "confidence": 0.5})

    # Also scan for short uppercase header lines as a second-pass
    if not candidates:
        for i, line in enumerate(text.splitlines()):
            l = line.strip()
            if not l or len(l) > 80:
                continue
            letters = [c for c in l if c.isalpha()]
            if not letters:
                continue
            up_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
            if up_ratio > 0.7 and len(l) > 3:
                # compute char offset by summing prior lines
                prior = "\n".join(text.splitlines()[:i])
                offset = len(prior) + (1 if prior else 0)
                candidates.append({"type": "chapter_start", "title": l, "char_offset": offset, "confidence": 0.4})

    return candidates


# =========================
# PHASE 2 — CHAPTER → DOCTRINE
# =========================


def validate_phase2_schema(parsed: Dict[str, Any], chapter_index: int) -> bool:
    """Validate Phase-2 output schema. Return True if valid, False if should skip.
    
    Relaxed validation: accept chapter if it has domains + at least ONE of:
    principles, rules, claims, or warnings. Initialize missing optional fields.
    """
    if not isinstance(parsed, dict):
        print(f"WARNING: Phase-2 (chapter {chapter_index}) not a JSON object; skipping")
        return False
    
    # Initialize missing optional fields
    for k in ("domains", "principles", "rules", "claims", "warnings", "cross_references"):
        if k not in parsed:
            parsed[k] = []
    
    # Core requirement: must have at least one domain
    if not parsed.get("domains"):
        print(f"WARNING: Phase-2 empty domains (chapter {chapter_index}); skipping")
        return False
    
    # Content requirement: must have at least ONE of principles, rules, claims, warnings
    has_content = (parsed.get("principles") or parsed.get("rules") or 
                   parsed.get("claims") or parsed.get("warnings"))
    
    if not has_content:
        print(f"WARNING: Phase-2 no doctrine content (chapter {chapter_index}); skipping")
        return False
    
    # All checks passed — accept with relaxed requirements
    return True


def phase2_doctrine(client: OllamaClient, chapter: Dict[str, Any]) -> Dict[str, Any] | None:
    user_prompt = (
        PHASE2_USER_TEMPLATE
        .replace("{chapter_index}", str(chapter["chapter_index"]))
        .replace("{chapter_code}", chapter.get("chapter_code") or f"C{chapter['chapter_index']:03d}")
        .replace("{chapter_text}", chapter["chapter_text"])
    )

    raw_output = ollama_generate(client, PHASE2_SYSTEM_PROMPT, user_prompt)

    json_text = extract_first_json(raw_output)
    if not json_text:
        # Log the raw output for debugging, but don't fail - return None to skip
        print(f"[Phase-2] Chapter {chapter['chapter_index']} - no JSON found (skipping)")
        print(f"[Phase-2] Raw output (first 300 chars): {raw_output[:300]}")
        return None

    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError as exc:
        print(f"[Phase-2] Chapter {chapter['chapter_index']} - JSON parse error: {exc} (skipping)")
        return None

    if not validate_phase2_schema(parsed, chapter["chapter_index"]):
        return None  # Already logged by validate_phase2_schema
    
    # Mark derived claims explicitly: convert string claims to objects with derived=true
    claims = parsed.get("claims", []) or []
    new_claims = []
    for c in claims:
        if isinstance(c, dict) and "claim" in c:
            new_claims.append(c)
        else:
            new_claims.append({"claim": c, "derived": True})
    parsed["claims"] = new_claims

    return parsed


# =========================
# MAIN INGESTION PIPELINE
# =========================


def run(book_path: Path, *, probe: bool = False, probe_window: bool = False) -> None:
    if not book_path.exists():
        hard_fail("Book file not found")

    book_id = book_path.stem
    book_workspace = WORKSPACE_DIR / book_id
    book_workspace.mkdir(parents=True, exist_ok=True)

    raw_text_path = book_workspace / "00_raw_text.txt"
    chapters_path = book_workspace / "01_chapters.json"
    doctrine_path = book_workspace / "02_principles.json"
    phase1_state = book_workspace / "phase1_state.json"
    phase2_state = book_workspace / "phase2_state.json"

    print("[INGEST] Loading book...")
    # Support PDF and txt via project's extractor
    if book_path.suffix.lower() == ".pdf":
        book_text = extract_text(str(book_path))
    else:
        book_text = book_path.read_text(encoding="utf-8")
    
    # Clean corrupted PDF extraction (handle excessive spaces)
    book_text = clean_extracted_text(book_text)

    if not raw_text_path.exists():
        atomic_write_text(raw_text_path, book_text)
        print(f"[INGEST] Wrote raw text: {raw_text_path}")
    else:
        print(f"[INGEST] Raw text already present: {raw_text_path} - resuming")

    # Track simple progress counting for user feedback
    total_files = 3
    completed_files = 1 if raw_text_path.exists() else 0
    print(f"[INGEST] Progress: {completed_files}/{total_files} files written ({int(completed_files/total_files*100)}%) - {raw_text_path.name}")

    # If probe mode requested, run a single-window probe and dump raw LLM output for inspection
    if probe:
        print("[INGEST] Running Phase-1 single-window probe (raw response will be dumped)...")
        client = OllamaClient(model=INGESTION_MODEL)
        window_text = book_text[0:WINDOW_SIZE]
        probe_dump = book_workspace / "phase1_probe_raw.txt"
        try:
            raw = client.generate(
                prompt=PHASE1_USER_TEMPLATE.format(absolute_char_offset=0, text_window=window_text),
                system=PHASE1_SYSTEM_PROMPT,
                temperature=INGESTION_TEMPERATURE,
                max_tokens=INGESTION_MAX_TOKENS,
                debug_dump=str(probe_dump),
            )
        except Exception as exc:
            print(f"[INGEST] Probe call raised: {exc}")
        print(f"[INGEST] Probe dump written to: {probe_dump}")
        print("[INGEST] Probe complete - inspect the dump and rerun without --probe to continue ingestion.")
        return

    # Probe-window: pin Phase-1A to an instruction model and strict generation params
    if probe_window:
        print("[INGEST] Running Phase-1 single-window strict probe (pinned model, tuned params)...")
        # Pin to recommended instruction model for pointer detection
        probe_model = "llama3.1:8b-instruct-q4_0"
        client = OllamaClient(model=probe_model)
        window_text = book_text[0:WINDOW_SIZE]
        probe_dump = book_workspace / "phase1_probe_raw.txt"
        try:
            raw = client.generate(
                model=probe_model,
                prompt=PHASE1_USER_TEMPLATE.format(absolute_char_offset=0, text_window=window_text),
                system=PHASE1_SYSTEM_PROMPT,
                temperature=0.0,
                max_tokens=256,
                top_p=1.0,
                stream=False,
                debug_dump=str(probe_dump),
            )
        except Exception as exc:
            print(f"[INGEST] Probe-window call raised: {exc}")
        print(f"[INGEST] Probe dump written to: {probe_dump}")
        print("[INGEST] Probe-window complete - inspect the dump. If successful, rerun without --probe-window to continue ingestion.")
        return

    print("[INGEST] Phase-1A: Boundary detection (pointer-only)...")
    client = OllamaClient(model=INGESTION_MODEL)
    
    # Layer 2: Annotate boundaries (add ===BOUNDARY=== markers for structure hints)
    annotated_book_text = annotate_boundaries(book_text)

    # If chapters already exist, skip Phase-1 and load existing chapters (resume)
    if chapters_path.exists():
        print(f"[INGEST] Found existing chapters: {chapters_path} - skipping Phase-1")
        chapters_json = json.loads(chapters_path.read_text(encoding="utf-8"))
    else:
        # resumable Phase-1A window scanner with checkpointing
        raw_boundaries = []
        # load state if exists
        if phase1_state.exists():
            try:
                state = json.loads(phase1_state.read_text(encoding="utf-8"))
                last_done = int(state.get("last_completed_window", -1))
                raw_boundaries = state.get("boundaries", [])
            except Exception:
                last_done = -1
                raw_boundaries = []
        else:
            last_done = -1

        step = max(1, WINDOW_SIZE - WINDOW_OVERLAP)
        text_len = len(annotated_book_text)
        windows = []
        for i, start in enumerate(range(0, text_len, step)):
            end = min(start + WINDOW_SIZE, text_len)
            windows.append((i, start, annotated_book_text[start:end]))

        total_windows = len(windows)
        for idx, start, wtext in windows:
            if idx <= last_done:
                continue
            user_prompt = PHASE1_USER_TEMPLATE.format(absolute_char_offset=start, text_window=wtext)
            try:
                raw_output = ollama_generate(client, PHASE1_SYSTEM_PROMPT, user_prompt)
            except Exception as exc:
                print(f"[Phase-1A] window {idx} FAILED: resumable stop: {exc}")
                break

            json_text = extract_first_json(raw_output)
            if not json_text:
                print(f"[Phase-1A] window {idx} returned no JSON; stopping resumable run")
                break

            try:
                parsed = json.loads(json_text)
            except Exception as exc:
                print(f"[Phase-1A] window {idx} JSON parse error: {exc}")
                break

            found = 0
            for b in parsed.get("boundaries", []) or []:
                try:
                    off = int(b.get("char_offset", 0))
                except Exception:
                    continue
                if off < start or off > start + WINDOW_SIZE:
                    continue
                b["char_offset"] = off
                try:
                    b["confidence"] = float(b.get("confidence", 0.0))
                except Exception:
                    b["confidence"] = 0.0
                raw_boundaries.append(b)
                found += 1

            # checkpoint after each successful window (atomic)
            state = {"last_completed_window": idx, "boundaries": raw_boundaries}
            atomic_write_text(phase1_state, json.dumps(state, indent=2, ensure_ascii=False))

            print(f"[Phase-1A] window {idx+1}/{total_windows} complete, found {found} boundaries")

        consolidated = consolidate_boundaries(raw_boundaries)
        print(f"[Phase-1B] Consolidated {len(consolidated)} boundaries")
        
        # Layer 3: Check for under-segmentation and retry if needed
        if check_under_segmentation(consolidated, book_text):
            print(f"[Phase-1B] WARNING: Possible under-segmentation detected (found {len(consolidated)} boundaries but book contains many numbered items).")
            print(f"[Phase-1B] Retrying Phase-1A with emphasis on numbered structure...")
            # Reset state and add explicit reminder to the prompt
            raw_boundaries = []
            phase1_state_retry = book_workspace / "phase1_state_retry.json"
            
            retry_reminder = "\n\nREMINDER: This book appears to contain numbered items (Law/Chapter/Principle). Ensure EACH numbered item is its own chapter."
            
            for idx, start, wtext in windows:
                user_prompt = PHASE1_USER_TEMPLATE.format(absolute_char_offset=start, text_window=wtext)
                try:
                    raw_output = ollama_generate(client, PHASE1_SYSTEM_PROMPT + retry_reminder, user_prompt)
                except Exception as exc:
                    print(f"[Phase-1A retry] window {idx} FAILED: {exc}")
                    break
                
                json_text = extract_first_json(raw_output)
                if not json_text:
                    continue
                
                try:
                    parsed = json.loads(json_text)
                except Exception:
                    continue
                
                for b in parsed.get("boundaries", []) or []:
                    try:
                        off = int(b.get("char_offset", 0))
                    except Exception:
                        continue
                    if off < start or off > start + WINDOW_SIZE:
                        continue
                    b["char_offset"] = off
                    try:
                        b["confidence"] = float(b.get("confidence", 0.0))
                    except Exception:
                        b["confidence"] = 0.0
                    raw_boundaries.append(b)
            
            consolidated = consolidate_boundaries(raw_boundaries)
            print(f"[Phase-1B retry] Re-consolidated to {len(consolidated)} boundaries")
        
        chapters_json = build_chapters_from_boundaries(consolidated, book_text)
        save_json(chapters_path, chapters_json)
        completed_files += 1
        print(f"[INGEST] Progress: {completed_files}/{total_files} files written ({int(completed_files/total_files*100)}%) - {chapters_path.name}")

    print("[INGEST] Phase-2: Extracting doctrine...")
    doctrine = {
        "book_title": chapters_json.get("book_title"),
        "author": chapters_json.get("author"),
        "chapters": [],
    }

    chapters = chapters_json.get("chapters", [])
    total_chapters = len(chapters)
    if total_chapters == 0:
        hard_fail("No chapters found after Phase-1")

    # Phase-2 resumable loop
    # load or initialize state
    if phase2_state.exists():
        try:
            pstate = json.loads(phase2_state.read_text(encoding="utf-8"))
            last_completed_chapter = int(pstate.get("last_completed_chapter", 0))
        except Exception:
            last_completed_chapter = 0
    else:
        last_completed_chapter = 0

    # load existing doctrine if present (append-only)
    if doctrine_path.exists():
        try:
            doctrine = json.loads(doctrine_path.read_text(encoding="utf-8"))
        except Exception:
            doctrine = {"book_title": chapters_json.get("book_title"), "author": chapters_json.get("author"), "chapters": []}

    for ch in chapters:
        idx = ch["chapter_index"]
        if idx <= last_completed_chapter:
            print(f"Skipping chapter {idx} (already completed)")
            continue

        # Skip chapters that are too small (likely fragments/corrupted)
        ch_text = ch.get("chapter_text", "")
        if len(ch_text) < 200:
            print(f"Skipping chapter {idx} (text too small: {len(ch_text)} chars)")
            last_completed_chapter = idx
            # Save progress
            atomic_write_text(phase2_state, json.dumps({"last_completed_chapter": last_completed_chapter}))
            continue

        code = ch.get("chapter_code") or f"C{ch['chapter_index']:03d}"
        print(f"  > Chapter {ch['chapter_index']} [{code}]")
        try:
            result = phase2_doctrine(client, ch)
        except Exception as exc:
            print(f"[Phase-2] chapter {idx} FAILED: resumable stop: {exc}")
            break

        # If result is None, chapter was skipped (already logged)
        if result is None:
            last_completed_chapter = idx
            atomic_write_text(phase2_state, json.dumps({"last_completed_chapter": idx}, indent=2, ensure_ascii=False))
            save_json(doctrine_path, doctrine)
            print(f"[Phase-2] Chapter progress: {idx}/{total_chapters} ({int(idx/total_chapters*100)}%)")
            continue

        # Validate schema; skip chapter if invalid
        if not validate_phase2_schema(result, idx):
            print(f"  (skipped due to schema validation)")
            # Still mark as completed so we don't retry
            atomic_write_text(phase2_state, json.dumps({"last_completed_chapter": idx}, indent=2, ensure_ascii=False))
            save_json(doctrine_path, doctrine)
            last_completed_chapter = idx
            continue

        # Post-process: tag derived claims and refine domains deterministically
        result = refine_domains(result)

        # append and checkpoint atomically
        doctrine.setdefault("chapters", []).append(result)
        # checkpoint chapter index atomically
        atomic_write_text(phase2_state, json.dumps({"last_completed_chapter": idx}, indent=2, ensure_ascii=False))
        save_json(doctrine_path, doctrine)

        last_completed_chapter = idx
        print(f"[Phase-2] Chapter progress: {idx}/{total_chapters} ({int(idx/total_chapters*100)}%)")

    # If we've appended all chapters, mark completion
    completed_files = 3 if doctrine_path.exists() else completed_files
    if doctrine_path.exists():
        print(f"[INGEST] Progress: {completed_files}/{total_files} files written ({int(completed_files/total_files*100)}%) - {doctrine_path.name}")

    print("[INGEST] INGESTION COMPLETE")
    print(f"[INGEST] Workspace: {book_workspace}")


# =========================
# ENTRYPOINT
# =========================


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Run ingestion pipeline")
    p.add_argument("book", help="Path to book (pdf or txt)")
    p.add_argument("--probe", action="store_true", help="Run single-window Phase-1 probe and dump raw response")
    p.add_argument("--probe-window", action="store_true", help="Run strict single-window Phase-1 probe pinned to an instruction model")
    args = p.parse_args()

    run(Path(args.book), probe=args.probe)
