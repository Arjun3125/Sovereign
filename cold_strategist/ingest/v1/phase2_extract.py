import json
from typing import Dict, Any

from cold_strategist.core.ministers import load_all_ministers, MinisterConstraint
from cold_strategist.core.prompt_builder import build_minister_prompt
from cold_strategist.core.validator import validate_output


def _call_llm(llm, prompt: str) -> Any:
    if hasattr(llm, "generate"):
        # Use named parameter to avoid positional-model mismatch in OllamaClient
        return llm.generate(prompt=prompt)
    if callable(llm):
        return llm(prompt)
    raise RuntimeError("Unsupported LLM interface: provide object with .generate() or a callable")


def extract_doctrine(chapter_text: str, llm, ministers: Dict[str, MinisterConstraint] = None, path: str = None) -> Dict[str, Any]:
    results = {}
    if ministers is None:
        ministers = load_all_ministers(path)

    for minister_id, minister in ministers.items():
        prompt = build_minister_prompt(minister, chapter_text)

        try:
            raw = _call_llm(llm, prompt)
        except Exception:
            continue

        # DEBUG: show raw LLM output for developer inspection
        try:
            print(f"\n--- {minister_id.upper()} RAW LLM OUTPUT ---")
            if hasattr(raw, "text"):
                print(raw.text)
            elif isinstance(raw, dict):
                print(raw)
            else:
                print(str(raw))
        except Exception:
            pass

        parsed = None
        if isinstance(raw, dict) and "parsed" in raw:
            parsed = raw.get("parsed")
        elif isinstance(raw, dict) and "content" in raw:
            parsed = raw.get("content")
        else:
            parsed = raw

        if isinstance(parsed, str):
            try:
                parsed_obj = json.loads(parsed)
            except Exception:
                parsed_obj = None
        elif isinstance(parsed, dict):
            parsed_obj = parsed
        else:
            parsed_obj = None

        verdict = validate_output(minister, parsed_obj if parsed_obj is not None else parsed)

        if verdict != "OK":
            try:
                print(f"{minister_id} -> DISCARDED ({verdict})")
            except Exception:
                pass

        if verdict == "OK":
            results[minister_id] = parsed_obj
        elif verdict == "SILENCE":
            continue
        else:
            continue

    return results


if __name__ == "__main__":
    class DummyLLM:
        def generate(self, prompt: str):
            return json.dumps({"silence": True})

    ministers = load_all_ministers()
    sample = "Sample chapter text about preparing before action and long-term positioning."
    out = extract_doctrine(sample, DummyLLM(), ministers=ministers)
    print("Phase-2 extract results:", out)
