from typing import Dict, List, Any


BOOK_REGISTRY = {
    "art_of_seduction": {
        "title": "The Art of Seduction",
        "author": "Robert Greene",
        "domains": ["psychology", "seduction"],
        "allowed_ministers": ["psychology"],
        "chapters": [
            "The Art of Charm",
            "The Coquette"
        ]
    },
    "48_laws_of_power": {
        "title": "The 48 Laws of Power",
        "author": "Robert Greene",
        "domains": ["power", "influence"],
        "allowed_ministers": ["power"],
        "chapters": [
            "Law 1"
        ]
    },
    "art_of_war": {
        "title": "The Art of War",
        "author": "Sun Tzu",
        "domains": ["conflict", "war", "strategy"],
        "allowed_ministers": ["conflict", "strategy"],
        "chapters": [
            "Laying Plans",
            "Waging War"
        ]
    },
    "antifragile": {
        "title": "Antifragile",
        "author": "Nassim Taleb",
        "domains": ["optionality", "risk"],
        "allowed_ministers": ["optionality", "strategy"],
        "chapters": [
            "Fragility and Antifragility"
        ]
    }
}


def get_book_config(book_id: str) -> Dict[str, Any]:
    """Get configuration for a book."""
    if book_id not in BOOK_REGISTRY:
        raise ValueError(f"Book {book_id} not in registry")
    return BOOK_REGISTRY[book_id]


def list_books() -> List[str]:
    """List all available books."""
    return list(BOOK_REGISTRY.keys())


def register_book(book_id: str, config: Dict[str, Any]) -> None:
    """Register a new book configuration."""
    BOOK_REGISTRY[book_id] = config
