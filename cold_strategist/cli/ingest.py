"""Thin CLI wrapper for ingestion.

This file follows the rule: `main()` only calls the canonical API.
"""

def main(argv=None):
    from cold_strategist.ingest.pipeline import ingest
    # Forward CLI args minimally — callers should parse before calling.
    return ingest()


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
