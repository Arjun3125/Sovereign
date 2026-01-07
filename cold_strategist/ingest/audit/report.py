def format_report(conflicts):
    """Format detected conflicts into a human-readable report.
    
    Args:
        conflicts: List of conflict dicts from detect_conflicts().
        
    Returns:
        Formatted report string.
    """
    if not conflicts:
        return "✅ No doctrine contradictions detected."

    lines = ["⚠️ Doctrine Contradictions Detected:\n"]

    for c in conflicts:
        lines.append(
            f"  Chapter {c['chapter_a']} vs Chapter {c['chapter_b']}\n"
            f"    A: {c['statement_a']}\n"
            f"    B: {c['statement_b']}\n"
        )

    return "\n".join(lines)
