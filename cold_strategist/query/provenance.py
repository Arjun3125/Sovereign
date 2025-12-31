def build_provenance(principles):
    """
    principles: list of principle records
    """

    books = set()
    authors = set()
    principle_ids = []

    for p in principles:
        books.add(p["book_id"])
        authors.add(p.get("author", "unknown"))
        principle_ids.append(p["id"])

    return {
        "books": sorted(books),
        "authors": sorted(authors),
        "principle_ids": principle_ids
    }
