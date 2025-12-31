import json


class ValidationError(Exception):
    pass


def require_keys(obj, keys, ctx):
    missing = [k for k in keys if k not in obj]
    if missing:
        raise ValidationError(f"{ctx}: missing keys {missing}")


def validate_raw(raw):
    require_keys(raw, ["book_id", "pages"], "raw")
    if not raw.get("pages"):
        raise ValidationError("raw: no pages")


def validate_structural(s):
    require_keys(s, ["book_id", "sections"], "structural")
    if not s.get("sections"):
        raise ValidationError("structural: no sections")


def validate_semantic(s):
    require_keys(s, ["book_id", "slices"], "semantic")
    slices = s.get("slices") or []
    # warn if slices are very short
    for sl in slices:
        if not sl.get("text") or len(sl.get("text", "")) < 50:
            raise ValidationError("semantic: slices too small")


def validate_principles(p):
    require_keys(p, ["book_id", "principles"], "principles")
    for pr in p.get("principles", []):
        require_keys(pr, ["principle", "derived_from"], "principle")


def validate_affinity(a):
    require_keys(a, ["book_id", "affinity"], "affinity")
