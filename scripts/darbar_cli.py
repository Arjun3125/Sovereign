#!/usr/bin/env python
"""CLI wrapper for run_interactive_decision using the console as ask_fn.

Usage:
  python scripts/darbar_cli.py --use-ollama --ollama-model llama2
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cold_strategist.core.interactive import run_interactive_decision
from cold_strategist.core.gatekeeper import Gatekeeper


def console_ask(q: str) -> str:
    try:
        return input(q + "\n> ")
    except EOFError:
        return ""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("statement", nargs="?", help="Decision statement (if omitted, you will be prompted)")
    p.add_argument("--use-ollama", action="store_true", help="Enable Ollama classification if available")
    p.add_argument("--ollama-model", default=None, help="Ollama model name to use (optional)")
    p.add_argument("--timeout", type=int, default=8, help="Timeout for Ollama calls in seconds")
    args = p.parse_args()

    if args.statement:
        stmt = args.statement
    else:
        stmt = input("Enter decision statement:\n> ")

    # Minimal ministers map for interactive capture: these are stubs exposing required_fields
    class Stub:
        output_shape = {"required_fields": ["risk_profile.hard_loss_cap_percent"]}

    ministers = {"risk": Stub(), "finance": Stub(), "power": Stub(), "operations": Stub(), "truth": Stub()}

    g = Gatekeeper("cli-run")
    # Freeze gatekeeper budget to allow darbar runs if later invoked
    g.max_questions = 0

    res = run_interactive_decision(stmt, ministers, console_ask, gatekeeper=g, use_ollama=args.use_ollama, ollama_model=args.ollama_model, ollama_timeout=args.timeout)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
