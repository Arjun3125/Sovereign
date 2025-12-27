"""
War Mode RAG Selector

Scores books/sources based on War Mode preferences.
Higher score = more relevant to War Mode objectives.

Scoring algorithm:
- Domain alignment: +2.0 per preferred domain, -1.5 per deprioritized domain
- Tone alignment: +1.5 per preferred tone, -0.8 per deprioritized tone
- War Mode priority multiplier: book.priority.war (0.0-1.0)

Result: Deterministic ranking that prefers leverage-heavy sources over moral commentary.
"""

from typing import Dict, List
from core.knowledge.war_rag_bias import WAR_RAG_BIAS


class WarRAGSelector:
    """
    Scores books/sources for War Mode retrieval.
    
    Usage:
        selector = WarRAGSelector()
        score = selector.score(book_metadata_dict)
        
    Metadata format:
        {
            "book_id": "art_of_seduction",
            "title": "The Art of Seduction",
            "domains": ["power", "psychology", "narrative"],
            "tones": ["dark", "strategic"],
            "priority": {"war": 1.0, "standard": 0.7, "quick": 0.2}
        }
    """

    def score(self, book_meta: Dict) -> float:
        """
        Score a book for War Mode retrieval preference.
        
        Args:
            book_meta: Book metadata dict with domains, tones, priority.war
            
        Returns:
            Float score (higher = more relevant to War Mode)
            Typically 0.0-10.0 range, but unbounded.
        """
        score = 0.0

        # Domain scoring
        domains = book_meta.get("domains", [])
        for domain in domains:
            domain_lower = domain.lower()
            
            if domain_lower in WAR_RAG_BIAS["preferred_domains"]:
                score += 2.0
            
            if domain_lower in WAR_RAG_BIAS["deprioritized_domains"]:
                score -= 1.5

        # Tone scoring
        tones = book_meta.get("tones", [])
        for tone in tones:
            tone_lower = tone.lower()
            
            if tone_lower in WAR_RAG_BIAS["preferred_tones"]:
                score += 1.5
            
            if tone_lower in WAR_RAG_BIAS["deprioritized_tones"]:
                score -= 0.8

        # War Mode priority multiplier
        # If book has war priority: score *= priority.war (0.0-1.0)
        # If book has no war priority: use fallback of 0.5
        priority_war = book_meta.get("priority", {}).get("war", 0.5)
        score *= priority_war

        return score

    def audit(self, book_meta: Dict, score: float) -> Dict:
        """
        Return explanation of why a book scored what it did.
        For debugging and transparency.
        
        Returns:
            {
                "book_id": str,
                "score": float,
                "domain_contribution": float,
                "tone_contribution": float,
                "priority_multiplier": float,
                "matching_domains": list,
                "matching_tones": list,
            }
        """
        domains = book_meta.get("domains", [])
        tones = book_meta.get("tones", [])
        priority_war = book_meta.get("priority", {}).get("war", 0.5)

        # Recalculate contributions
        domain_score = 0.0
        matching_domains = []
        for d in domains:
            d_lower = d.lower()
            if d_lower in WAR_RAG_BIAS["preferred_domains"]:
                domain_score += 2.0
                matching_domains.append((d, "+2.0 (preferred)"))
            elif d_lower in WAR_RAG_BIAS["deprioritized_domains"]:
                domain_score -= 1.5
                matching_domains.append((d, "-1.5 (deprioritized)"))

        tone_score = 0.0
        matching_tones = []
        for t in tones:
            t_lower = t.lower()
            if t_lower in WAR_RAG_BIAS["preferred_tones"]:
                tone_score += 1.5
                matching_tones.append((t, "+1.5 (preferred)"))
            elif t_lower in WAR_RAG_BIAS["deprioritized_tones"]:
                tone_score -= 0.8
                matching_tones.append((t, "-0.8 (deprioritized)"))

        return {
            "book_id": book_meta.get("book_id"),
            "title": book_meta.get("title"),
            "final_score": score,
            "domain_contribution": domain_score,
            "tone_contribution": tone_score,
            "priority_multiplier": priority_war,
            "matching_domains": matching_domains,
            "matching_tones": matching_tones,
        }

    def rank(self, books: List[Dict], limit: int = 5) -> List[Dict]:
        """
        Rank books by War Mode preference, return top N.
        
        Args:
            books: List of book metadata dicts
            limit: Maximum sources to return (respects hard_rules.max_sources)
            
        Returns:
            List of (book_meta, score) tuples, sorted descending
        """
        max_sources = WAR_RAG_BIAS["hard_rules"]["max_sources"]
        limit = min(limit, max_sources)

        # Score and sort
        scored = [
            (book, self.score(book))
            for book in books
        ]
        ranked = sorted(scored, key=lambda x: x[1], reverse=True)

        return [book for book, score in ranked[:limit]]
