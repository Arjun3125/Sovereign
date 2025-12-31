from pathlib import Path
from ollama import chat
import time

MAX_CHARS = 6000

PROMPT_TEMPLATE = """
You are extracting durable principles from a book section.

Rules:
- Do NOT summarize.
- Do NOT rewrite stories.
- Extract:
  1. Explicit principles
  2. Implicit rules
  3. Reusable patterns
- Preserve original wording where possible.
- Output as bullet points.
- Cite page numbers if referenced.

TEXT:
{content}
"""


def _load_model_from_config():
  # Try to read model from cold_strategist/config/llm.yaml if present
  try:
    import yaml
    cfg_path = Path(__file__).resolve().parents[2] / "config" / "llm.yaml"
    if cfg_path.exists():
      data = yaml.safe_load(cfg_path.read_text(encoding='utf-8')) or {}
      # prefer explicit ingest_model for chunking/slicing tasks
      return data.get("ingest_model") or data.get("model")
  except Exception:
    pass
  # fallback to reasoning model for ingest
  return "huihui_ai/deepseek-r1-abliterated:8b"


def semantic_slice(section_text: str):
  model = _load_model_from_config()

  def split_for_llm(text: str):
    chunks = []
    current = ""
    for para in text.split("\n\n"):
      if not para:
        continue
      if len(current) + len(para) > MAX_CHARS:
        if current:
          chunks.append(current)
        current = para
      else:
        if current:
          current += "\n\n" + para
        else:
          current = para
    if current:
      chunks.append(current)
    return chunks

  windows = split_for_llm(section_text)
  results = []
  for idx, window in enumerate(windows, start=1):
    print(f"[SEMANTIC] Processing window {idx}/{len(windows)}")

    success = False
    last_exc = None
    for attempt in range(3):
      try:
        response = chat(
          model=model,
          messages=[
            {"role": "system", "content": "Extract principles, heuristics, stories. Do not summarize."},
            {"role": "user", "content": PROMPT_TEMPLATE.format(content=window)},
          ],
        )
        content = response["message"]["content"]
        results.append(content)
        success = True
        print(f"[SEMANTIC] Window {idx} OK")
        break
      except Exception as e:
        last_exc = e
        print(f"[SEMANTIC] Window {idx} attempt {attempt+1} failed: {e}")
        if attempt < 2:
          time.sleep(5)
    if not success:
      print(f"[SEMANTIC] Window {idx} failed after retries: {last_exc}")
      results.append("[LLM_UNAVAILABLE]")

  # Join window outputs conservatively
  return "\n\n".join(results)
