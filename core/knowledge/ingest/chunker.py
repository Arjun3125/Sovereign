def chunk_by_chapter(book):
    chunks = []
    text = book["raw_text"]

    for chapter in book["meta"]["chapters"]:
        marker = chapter["title"]
        if marker not in text:
            continue

        section = text.split(marker, 1)[1].split("\n\n", 1)[0]

        chunks.append({
            "book_id": book["book_id"],
            "chapter": chapter["id"],
            "chapter_title": chapter["title"],
            "text": section.strip()
        })

    return chunks
