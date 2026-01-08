from .normalize import normalize

NEGATIONS = {"not", "never", "avoid", "forbid", "prohibit", "no"}


def has_negation(text: str) -> bool:
    """Check if text contains a negation keyword.
    
    Args:
        text: Text to check.
        
    Returns:
        True if negation is present.
    """
    return any(n in text.split() for n in NEGATIONS)


def is_direct_contradiction(a: str, b: str) -> bool:
    """Detect direct contradiction between two statements.
    
    Conservative by design:
    - Requires >= 3 words overlap
    - Requires one affirmative and one negated
    - Avoids false positives at cost of false negatives
    
    Args:
        a: First statement.
        b: Second statement.
        
    Returns:
        True if statements are direct contradictions.
    """
    na, nb = normalize(a), normalize(b)

    # Identical statements aren't contradictions
    if na == nb:
        return False

    words_a = set(na.split())
    words_b = set(nb.split())

    overlap = words_a & words_b
    if len(overlap) < 3:
        return False

    # XOR: one must have negation, the other must not
    return has_negation(na) ^ has_negation(nb)
