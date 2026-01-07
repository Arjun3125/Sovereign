from .pairwise import is_direct_contradiction

CHECK_FIELDS = ("principles", "rules", "warnings")


def extract_statements(chapter):
    """Extract all statements from a chapter's doctrine fields.
    
    Args:
        chapter: Chapter dict with potential principles/rules/warnings.
        
    Returns:
        List of (field_name, statement) tuples.
    """
    out = []
    for field in CHECK_FIELDS:
        for stmt in chapter.get(field, []):
            out.append((field, stmt))
    return out


def detect_conflicts(chapters):
    """Detect contradictions across all chapters using pairwise comparison.
    
    Args:
        chapters: List of chapter dicts loaded from doctrine store.
        
    Returns:
        List of conflict dicts with chapter indices and statements.
    """
    conflicts = []

    for i, ch_a in enumerate(chapters):
        stmts_a = extract_statements(ch_a)

        for j in range(i + 1, len(chapters)):
            ch_b = chapters[j]
            stmts_b = extract_statements(ch_b)

            for type_a, a in stmts_a:
                for type_b, b in stmts_b:
                    if is_direct_contradiction(a, b):
                        conflicts.append({
                            "conflict_type": "direct_contradiction",
                            "chapter_a": ch_a.get("chapter_index", i),
                            "statement_a": a,
                            "chapter_b": ch_b.get("chapter_index", j),
                            "statement_b": b
                        })

    return conflicts
