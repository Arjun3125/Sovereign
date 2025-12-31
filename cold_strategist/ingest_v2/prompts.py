"""Prompt templates for Ingest V2.

These strings are exact copies of the user's PROMPT SET for DOMAIN_CLASSIFICATION
and MEMORY_EXTRACTION. They are intended to be passed to an LLM client when
moving from dry-run to PHASE 1/2.
"""

DOMAIN_CLASSIFICATION_SYSTEM = """
You are a JSON generator.

You must output a single valid JSON object.
The first character of your response MUST be '{'.
Do not include explanations.
Do not include markdown.
Do not include text outside JSON.
"""

DOMAIN_CLASSIFICATION_USER = """
TASK: DOMAIN_CLASSIFICATION

DOMAINS (fixed list — choose from these ONLY):
- grand_strategy
- power
- optionality
- psychology
- diplomacy
- conflict
- truth
- risk
- timing
- data_judgment
- operations
- technology
- adaptation
- legitimacy
- narrative

RULES:
- Choose ALL domains that apply.
- Overlap is allowed.
- If no domain fits perfectly, choose the closest one.
- NEVER invent new domains.
- MUST return at least one domain.
- Output MUST be valid JSON.
- No extra text. No markdown.

CHAPTER_ID: {{chapter_id}}
CHAPTER_TITLE: {{chapter_title}}

CHAPTER_TEXT:
{{chapter_text}}

EXPECTED OUTPUT (STRICT)
{
  "chapter_id": "01",
  "domains": ["strategy", "power"]
}
"""


MEMORY_EXTRACTION_SYSTEM = """
You are a JSON generator.

You must output a single valid JSON object.
The first character of your response MUST be '{'.
Do not include explanations.
Do not include markdown.
Do not include text outside JSON.
"""

MEMORY_EXTRACTION_USER = """
TASK: MEMORY_EXTRACTION

DOMAIN: {{domain}}

INSTRUCTIONS:
- Extract ONLY what a person should REMEMBER after reading this chapter.
- Focus strictly on the given domain.
- Do NOT summarize the chapter.
- Do NOT tell stories.
- Do NOT invent.
- Do NOT combine multiple ideas into one.
- If multiple distinct memory items exist, list all of them.
- If only one exists, list one.
- If none exist for this domain, return an empty list.
- Output MUST be valid JSON.
- No extra text. No markdown.

CHAPTER_ID: {{chapter_id}}
CHAPTER_TITLE: {{chapter_title}}

CHAPTER_TEXT:
{{chapter_text}}

EXPECTED OUTPUT (STRICT)
{
  "chapter_id": "01",
  "domain": "deception",
  "memory_items": [
    "Victory depends on shaping the opponent’s perception before engagement.",
    "Open strength provokes resistance; concealed intent enables control."
  ]
}
"""
