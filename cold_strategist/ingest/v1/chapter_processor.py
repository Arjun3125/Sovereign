from .llm_client import call_llm

MAX_CHARS = 20000  # safe for most 32k-context models


def split_text(text: str):
    if len(text) <= MAX_CHARS:
        return [text]

    parts = []
    buffer = ""

    for para in text.split("\n\n"):
        if len(buffer) + len(para) < MAX_CHARS:
            buffer += para + "\n\n"
        else:
            parts.append(buffer)
            buffer = para + "\n\n"

    if buffer:
        parts.append(buffer)

    return parts


def build_prompt(chapter_index, title, text_part):
    return f"""
You are a doctrine ingestion engine.

Rules:
- NO summarization
- NO external knowledge
- NO moral framing
- Extract only what the author explicitly states

Return STRICT JSON:
{{
  "principles": [],
  "claims": [],
  "rules": [],
  "warnings": [],
  "cross_references": []
}}

Chapter {chapter_index}: {title}

TEXT:
{text_part}
"""


def process_chapter(chapter):
    parts = split_text(chapter.text)
    outputs = []

    for part in parts:
        prompt = build_prompt(chapter.index, chapter.title, part)
        outputs.append(call_llm(prompt))

    return outputs
