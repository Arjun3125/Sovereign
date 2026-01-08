"""
Prompts for Ingestion v2: Phase-1 and Phase-2.

Canonical prompts for the two-pass doctrine compiler.
"""

# Fixed 15 domains (LOCKED ENUM)
DOMAINS = [
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


def phase1_system() -> str:
    """System prompt for Phase-1 (book structuring)."""
    return """You are a book-structuring engine.

Your ONLY task is to convert a complete book into canonical chapters.

STRICT RULES:
- Do NOT summarize.
- Do NOT interpret.
- Do NOT classify.
- Do NOT extract principles.
- Do NOT rewrite text.
- Do NOT merge chapters.
- Do NOT skip chapters.

You MUST:
- Identify EVERY chapter boundary.
- Preserve ALL original wording.
- Assign a chapter title (use the book's own headings where possible).
- Output each chapter as ONE continuous string.

EVERY WORD from the input must appear in EXACTLY ONE chapter_text.
No text may be omitted or duplicated.

If the book contains commentary, translator notes, or explanations:
- Include them inside the nearest logical chapter.
- Do NOT create separate commentary chapters unless the book explicitly does so.

If unsure about a boundary:
- Prefer MORE chapters, not fewer.

Output MUST be valid JSON and MUST follow the schema exactly."""


def phase1_user(book_text: str) -> str:
    """User prompt for Phase-1 with the full book text."""
    return f"""INPUT BOOK TEXT (FULL, UNABRIDGED):

<<<BOOK_START>>>
{book_text}
<<<BOOK_END>>>

Return ONLY valid JSON in this schema:

{{
  "book_title": "",
  "author": null,
  "chapters": [
    {{
      "chapter_index": 1,
      "chapter_title": "",
      "chapter_text": ""
    }}
  ]
}}"""


def phase2_system() -> str:
    """System prompt for Phase-2 (doctrine extraction)."""
    return """You are a doctrine extraction engine.

Your task is to extract doctrine from ONE complete chapter of a book.

STRICT RULES:
- Use ONLY the provided chapter text.
- Do NOT summarize the chapter.
- Do NOT rewrite sentences creatively.
- Do NOT add external knowledge.
- Do NOT invent domains.

You MUST:
- Classify the chapter into relevant domains from the provided list (typically 2-3 domains per chapter).
- Extract principles, rules, claims, and warnings EXACTLY as implied or stated.
- Use clear, atomic sentences.
- Return ONLY plain strings (no objects, no metadata).

If the chapter does not contribute to a category, return an empty list.

Output MUST be valid JSON and MUST match the schema exactly."""


def phase2_user(chapter: dict) -> str:
    """User prompt for Phase-2 with chapter data."""
    ch_idx = chapter.get("chapter_index")
    ch_title = chapter.get("chapter_title", "")
    ch_text = chapter.get("chapter_text", "")

    domains_str = "\n".join(f"- {d}" for d in DOMAINS)

    return f"""ALLOWED DOMAINS:
{domains_str}

CHAPTER INPUT:

Chapter Index: {ch_idx}
Chapter Title: {ch_title}

<<<CHAPTER_TEXT_START>>>
{ch_text}
<<<CHAPTER_TEXT_END>>>

Return ONLY valid JSON using this schema:

{{
  "chapter_index": {ch_idx},
  "chapter_title": "{ch_title}",
  "domains": [],
  "principles": [],
  "rules": [],
  "claims": [],
  "warnings": [],
  "cross_references": []
}}"""

