def merge_lists(dicts, key):
    merged = []
    for d in dicts:
        merged.extend(d.get(key, []))
    return list(dict.fromkeys(merged))  # dedupe, preserve order


def assemble(chapter, partials):
    return {
        "book_id": chapter.book_id,
        "chapter_index": chapter.index,
        "chapter_title": chapter.title,
        "principles": merge_lists(partials, "principles"),
        "claims": merge_lists(partials, "claims"),
        "rules": merge_lists(partials, "rules"),
        "warnings": merge_lists(partials, "warnings"),
        "cross_references": sorted(
            set().union(*[p.get("cross_references", []) for p in partials])
        ),
        "source_hash": chapter.hash
    }
