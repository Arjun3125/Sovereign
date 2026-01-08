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
        raise RuntimeError(f"Missing keys: {missing}")

    # Enforce string-only items in doctrine lists
    for k in ("principles", "claims", "rules", "warnings"):
        vals = output.get(k, [])
        if not isinstance(vals, list):
            raise RuntimeError(f"Invalid type for {k}: expected list, got {type(vals)}")
        if not all(isinstance(x, str) for x in vals):
            raise RuntimeError(f"Non-string item detected in {k}")
