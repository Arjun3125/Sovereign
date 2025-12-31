def compute_confidence(
    authority: str,
    unique_books: int,
    support_count: int
) -> float:
    """
    Returns confidence in range [0.0, 1.0]
    Deterministic, comparable, explainable.
    """

    score = 0.0

    # Authority weight
    if authority == "universal":
        score += 0.5
    elif authority == "book":
        score += 0.3

    # Breadth (books)
    score += min(0.3, 0.05 * unique_books)

    # Density (supporting principles)
    score += min(0.2, 0.02 * support_count)

    return round(min(score, 1.0), 2)
