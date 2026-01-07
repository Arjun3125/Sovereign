# doctrine_federation.py
# MULTI-BOOK DOCTRINE FEDERATION (read-only, no merging)

import sqlite3
import json
import math
from pathlib import Path

class DoctrineFederation:
    """
    Routes doctrine queries across independent per-book DBs.
    
    NEVER merges embeddings.
    NEVER normalizes doctrine.
    Results labeled by source book.
    """
    
    def __init__(self, book_dbs: dict):
        """
        book_dbs: dict mapping book_name -> db_path
        
        Example:
            {
                "The Art of War": "workspace/The_Art_Of_War/embeddings/doctrine_vectors.db",
                "48 Laws of Power": "workspace/48_Laws_Of_Power/embeddings/doctrine_vectors.db",
            }
        """
        self.book_dbs = {k: v for k, v in book_dbs.items() if Path(v).exists()}
        if not self.book_dbs:
            raise ValueError("No valid doctrine DBs found")

    @staticmethod
    def _cosine(a, b):
        """Compute cosine similarity between two vectors."""
        if not a or not b:
            return 0.0
        dot = sum(x*y for x, y in zip(a, b))
        na = math.sqrt(sum(x*x for x in a))
        nb = math.sqrt(sum(x*x for x in b))
        return dot / (na * nb) if na and nb else 0.0

    def query(self, query_vec, top_k=5, min_similarity=0.3):
        """
        Query all books, return ranked results (NOT merged).
        
        Args:
            query_vec: embedding vector (list of floats)
            top_k: max results across all books
            min_similarity: filter out low-confidence matches
        
        Returns:
            List of dicts with keys:
              - book: source book name
              - doctrine_id: unique ID
              - text: doctrine text
              - similarity: cosine score
              - metadata: full metadata dict
        """
        results = []

        for book, db_path in self.book_dbs.items():
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()

                rows = cur.execute(
                    "SELECT id, text, embedding, metadata FROM embeddings"
                ).fetchall()
                conn.close()

                # Score each doctrine in this book
                for r in rows:
                    try:
                        emb = json.loads(r[2])
                        meta = json.loads(r[3])
                    except Exception:
                        continue
                    
                    sim = self._cosine(query_vec, emb)
                    if sim >= min_similarity:
                        results.append({
                            "book": book,
                            "doctrine_id": r[0],
                            "text": r[1],
                            "similarity": sim,
                            "metadata": meta,
                        })
            except Exception as e:
                print(f"⚠️  Error querying {book}: {e}")
                continue

        # Re-rank across all books (by similarity only, no normalization)
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def by_book(self, query_vec, top_k_per_book=3):
        """
        Return results grouped by book (not pooled).
        
        Useful for seeing how different sources rank the same query.
        
        Returns:
            Dict: {book_name: [result1, result2, ...]}
        """
        by_book = {}
        
        for book, db_path in self.book_dbs.items():
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                rows = cur.execute(
                    "SELECT id, text, embedding, metadata FROM embeddings"
                ).fetchall()
                conn.close()

                book_results = []
                for r in rows:
                    try:
                        emb = json.loads(r[2])
                        meta = json.loads(r[3])
                    except Exception:
                        continue
                    sim = self._cosine(query_vec, emb)
                    book_results.append({
                        "doctrine_id": r[0],
                        "text": r[1],
                        "similarity": sim,
                        "metadata": meta,
                    })
                
                book_results.sort(key=lambda x: x["similarity"], reverse=True)
                by_book[book] = book_results[:top_k_per_book]
            except Exception as e:
                print(f"⚠️  Error querying {book}: {e}")
                continue

        return by_book

    def stats(self):
        """Print federation stats (# of DBs, # of doctrines per book)."""
        print("\n🏛️  DOCTRINE FEDERATION STATS\n")
        total = 0
        for book, db_path in self.book_dbs.items():
            try:
                conn = sqlite3.connect(db_path)
                count = conn.execute(
                    "SELECT COUNT(*) FROM embeddings"
                ).fetchone()[0]
                conn.close()
                print(f"  {book}: {count} doctrines")
                total += count
            except Exception as e:
                print(f"  {book}: ERROR ({e})")
        print(f"\n  TOTAL: {total} doctrines across {len(self.book_dbs)} books\n")
