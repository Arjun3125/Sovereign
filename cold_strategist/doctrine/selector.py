def select_core_doctrine(universal_principles, k=5):
    """
    universal_principles: list of records with
    - id
    - support_count
    - unique_books
    """

    ranked = sorted(
        universal_principles,
        key=lambda p: (
            p.get("unique_books", 0),
            p.get("support_count", 0)
        ),
        reverse=True
    )

    return ranked[:k]
