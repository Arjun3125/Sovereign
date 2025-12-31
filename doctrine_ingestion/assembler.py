def _coerce_to_str(item, key):
    if isinstance(item, str):
        return item.strip()

    if isinstance(item, dict):
        # allowed coercions
        for k in ("claim", "principle", "rule", "warning", "text"):
            if k in item and isinstance(item[k], str):
                return item[k].strip()

    raise TypeError(
        f"Invalid item type in '{key}': {type(item)} | value={item}"
    )


def merge_lists(partials, key):
    merged = []

    for p in partials:
        for item in p.get(key, []):
            merged.append(_coerce_to_str(item, key))

    # dedupe, preserve order
    seen = set()
    out = []
    for x in merged:
        if x not in seen:
            seen.add(x)
            out.append(x)

    return out


def _coerce_ref(item):
    if isinstance(item, int):
        return item

    if isinstance(item, str) and item.isdigit():
        return int(item)

    if isinstance(item, dict):
        for k in ("chapter", "ref", "index"):
            if k in item and isinstance(item[k], int):
                return item[k]

    raise TypeError(
        f"Invalid cross_reference type: {type(item)} | value={item}"
    )


def assemble(chapter, partials):
    return {
        "book_id": chapter.book_id,
        "chapter_index": chapter.index,
        "chapter_title": chapter.title,
        "principles": merge_lists(partials, "principles"),
        "claims": merge_lists(partials, "claims"),
        "rules": merge_lists(partials, "rules"),
        "warnings": merge_lists(partials, "warnings"),
        # normalize cross-references to integers, dedupe deterministically
        "cross_references": (lambda refs=[
            _coerce_ref(r) for p in partials for r in p.get("cross_references", [])
        ]: sorted(set(refs)))(),
        "source_hash": chapter.hash
    }
