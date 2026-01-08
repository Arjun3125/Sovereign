import json
import sys
from cold_strategist.core.llm.ollama_client import OllamaClient
from cold_strategist.core.ministers import load_all_ministers
from cold_strategist.core.decision_engine import decide

QUESTION = "Should I aggressively expand my project now, or consolidate and wait?"
BOOK_CONTEXT = [
    "Commitment precedes constraint.",
    "Expansion increases exposure.",
    "Timing asymmetry matters.",
    "Early dominance vs premature lock-in."
]


def main():
    try:
        client = OllamaClient()
    except Exception as e:
        print(json.dumps({"error": f"Failed to initialize OllamaClient: {str(e)}"}))
        sys.exit(1)

    ministers = load_all_ministers()
    if not ministers:
        print(json.dumps({"error": "No ministers loaded"}))
        sys.exit(2)

    result = decide(QUESTION, BOOK_CONTEXT, ministers, client, mode="FAST_READ_ONLY")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
