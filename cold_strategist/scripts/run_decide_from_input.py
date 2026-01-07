#!/usr/bin/env python
"""Run the Sovereign decision engine on a plain text input file.

This is a thin test harness that loads minister constraints, uses a
deterministic FakeLLM for predictable outputs, and calls `decide()`.
"""
import argparse
import json
from pathlib import Path

from cold_strategist.core.decision_engine import decide
from cold_strategist.core.ministers import load_all_ministers


class FakeLLM:
    """Deterministic fake LLM that returns structured minister outputs.

    It inspects the prompt header to find the minister id and returns a
    simple JSON content matching expected shape (confidence + proceed flag).
    """

    def generate(self, prompt: str):
        # Extract minister id from prompt header
        minister_line = [l for l in prompt.splitlines() if l.strip().startswith("You are the Minister of")]
        if minister_line:
            header = minister_line[0]
            parts = header.split()
            minister = parts[-1].strip().strip('.').lower()
        else:
            minister = "unknown"

        # Simple deterministic heuristics per minister id
        if minister == "risk":
            return {"content": {"confidence": 0.85, "proceed": False, "note": "high risk"}}
        if minister == "power":
            return {"content": {"confidence": 0.7, "proceed": True, "note": "leverage favors action"}}
        if minister == "truth":
            return {"content": {"confidence": 0.6, "proceed": False, "note": "evidence weak"}}
        if minister == "timing":
            return {"content": {"confidence": 0.65, "proceed": False, "note": "no urgent window"}}

        # Default: signal silence
        return {"content": {"silence": True, "confidence": 0.5}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to decision text file")
    ap.add_argument("--trace", action="store_true", help="Show trace/audit")
    args = ap.parse_args()

    infile = Path(args.input)
    if not infile.exists():
        print(json.dumps({"error": f"input file not found: {infile}"}))
        raise SystemExit(2)

    text = infile.read_text(encoding="utf-8")

    ministers = load_all_ministers()
    llm = FakeLLM()

    result = decide(text, None, ministers, llm, mode="FAST_READ_ONLY")

    if args.trace:
        print(json.dumps(result, indent=2))
    else:
        # Print compact output
        print(json.dumps({"decision": result.get("decision"), "disagreement": result.get("disagreement")}))


if __name__ == "__main__":
    main()
