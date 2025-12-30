def conduct_debate(ministers, book_id, question):
    """Conduct a debate by gathering advice from all ministers.
    
    Args:
        ministers: List of Minister instances.
        book_id: Book identifier.
        question: Question to debate.
        
    Returns:
        List of records, each with minister name and opinion.
    """
    records = []

    for m in ministers:
        opinion = m.advise(book_id, question)
        records.append({
            "minister": m.name,
            "opinion": opinion
        })

    return records
