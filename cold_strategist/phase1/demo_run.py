import os
from cold_strategist.phase1.phase1_prompt import PROMPT, validate_response
from cold_strategist.phase1.llm_client import call_llm


def run_demo(situation: str):
    # Build full prompt
    full = PROMPT + "\n\nSITUATION:\n" + situation + "\n\nRespond with a single JSON object."

    raw = call_llm(full)
    print("=== RAW LLM OUTPUT ===")
    print(raw)

    # Validate
    try:
        validated = validate_response(raw)
        print("=== VALIDATED RESPONSE ===")
        # Pydantic v1 vs v2 compatibility for JSON output
        try:
            if hasattr(validated, "model_dump_json"):
                print(validated.model_dump_json(indent=2))
            else:
                print(validated.json(indent=2))
        except Exception:
            # Fallback to manual dump
            try:
                data = validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
            except Exception:
                data = validated.__dict__
            import json as _json

            print(_json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print("Validation failed:", e)


if __name__ == "__main__":
    # Example: read situation from env var or fallback
    situation = os.getenv("PHASE1_SITUATION", "An escalation in the northern sector with unclear actors.")
    run_demo(situation)
