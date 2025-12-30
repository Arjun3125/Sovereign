from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class Chapter:
    book_id: str
    index: int
    title: str
    text: str
    start_page: int
    end_page: int
    hash: str

    @staticmethod
    def compute_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
