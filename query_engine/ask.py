from .loader import load_book
from .retriever import retrieve
from .prompt import build_prompt
from .synthesize import synthesize


def ask(book_id: str, question: str) -> str:
    chapters = load_book(book_id)
    relevant = retrieve(question, chapters)

    if not relevant:
        return "Doctrine contains no relevant material."

    prompt = build_prompt(question, relevant)
    return synthesize(prompt)
