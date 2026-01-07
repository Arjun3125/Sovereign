import sys
import json
import argparse

from cold_strategist.core.llm.ollama_client import OllamaClient
from cold_strategist.ingestion.phase2_extract import extract_doctrine
from cold_strategist.core.ministers import load_all_ministers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("chapter", nargs="?", help="path to chapter file")
    parser.add_argument("--debug-strategy", action="store_true", help="use hard-coded strategy paragraph for quick test")
    args = parser.parse_args()

    if args.chapter:
        try:
            with open(args.chapter, "r", encoding="utf-8") as f:
                chapter = f.read()
        except Exception as e:
            print(json.dumps({"error": f"failed to read chapter: {str(e)}"}))
            sys.exit(2)
    else:
        chapter = "Sample chapter text about preparing before action and long-term positioning."

    if args.debug_strategy:
        chapter = """
Victory belongs to those who secure advantage before conflict begins.
Those who enter war without preparation invite defeat.
"""

    # STEP 1 CHECK: confirm ministers load
    ministers = load_all_ministers()
    print("LOADED MINISTERS:", list(ministers.keys()))

    try:
        client = OllamaClient()
    except Exception as e:
        print(json.dumps({"error": f"failed to initialize OllamaClient: {str(e)}"}))
        sys.exit(3)

    if not ministers:
        print(json.dumps({}))
        return

    # STEP 2 CHECK: confirm chapter text
    print("CHAPTER TEXT LENGTH:", len(chapter))
    print("CHAPTER PREVIEW:", chapter[:200])

    results = extract_doctrine(chapter, client, ministers=ministers)
    print(json.dumps(results))


if __name__ == "__main__":
    main()
