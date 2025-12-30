REQUIRED_KEYS = {
    "principles",
    "claims",
    "rules",
    "warnings",
    "cross_references",
}


def validate(output):
    missing = REQUIRED_KEYS - output.keys()
    if missing:
        raise RuntimeError(f"Invalid LLM output, missing: {missing}")
