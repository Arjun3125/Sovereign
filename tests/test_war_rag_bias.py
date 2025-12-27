"""
Test suite for War Mode RAG Book Selection Bias

Tests:
1. Book metadata loading
2. War RAG scoring algorithm
3. Book ranking by War Mode preference
4. Bias application to retrieval results
5. Two-pass chunking with principle extraction
"""

import unittest
import os
import tempfile
from core.knowledge.war_rag_bias import WAR_RAG_BIAS
from core.knowledge.war_rag_selector import WarRAGSelector
from core.knowledge.book_metadata_loader import BookMetadataLoader
from core.knowledge.ingest.two_pass_chunker import TwoPassSemanticChunker


class TestWarRAGBias(unittest.TestCase):
    """Test War RAG Bias data structure."""

    def test_bias_structure_complete(self):
        """Bias should have all required tiers."""
        required_keys = [
            "preferred_domains",
            "preferred_tones",
            "deprioritized_domains",
            "deprioritized_tones",
            "hard_rules",
        ]
        for key in required_keys:
            self.assertIn(key, WAR_RAG_BIAS)

    def test_preferred_domains_are_leverage_heavy(self):
        """Preferred domains should be strategic/power-focused."""
        leverage_terms = ["power", "conflict", "intelligence"]
        for term in leverage_terms:
            self.assertIn(
                term, WAR_RAG_BIAS["preferred_domains"],
                f"{term} should be in preferred domains"
            )

    def test_deprioritized_are_soft_voices(self):
        """Deprioritized domains should be ethics/harmony/soft."""
        soft_terms = ["ethics", "harmony", "healing"]
        for term in soft_terms:
            self.assertIn(
                term, WAR_RAG_BIAS["deprioritized_domains"],
                f"{term} should be deprioritized"
            )

    def test_hard_rules_exist(self):
        """Hard rules should define min/max sources."""
        rules = WAR_RAG_BIAS["hard_rules"]
        self.assertIn("min_sources", rules)
        self.assertIn("max_sources", rules)
        self.assertTrue(rules["allow_dark_texts"])
        self.assertTrue(rules["no_moral_filtering"])


class TestWarRAGSelector(unittest.TestCase):
    """Test War RAG Selector scoring engine."""

    def setUp(self):
        """Initialize selector for each test."""
        self.selector = WarRAGSelector()

    def test_dark_text_preferred(self):
        """Books with 'dark' tone should score higher."""
        dark_book = {
            "book_id": "48_laws",
            "title": "48 Laws of Power",
            "domains": ["power"],
            "tones": ["dark", "strategic"],
            "priority": {"war": 1.0},
        }

        light_book = {
            "book_id": "getting_to_yes",
            "title": "Getting to Yes",
            "domains": ["diplomacy"],
            "tones": ["collaborative"],
            "priority": {"war": 0.2},
        }

        dark_score = self.selector.score(dark_book)
        light_score = self.selector.score(light_book)

        self.assertGreater(dark_score, light_score)

    def test_power_domain_preferred(self):
        """Books with 'power' domain should score higher."""
        power_book = {
            "book_id": "power_test",
            "domains": ["power"],
            "tones": [],
            "priority": {"war": 0.5},
        }

        ethics_book = {
            "book_id": "ethics_test",
            "domains": ["ethics"],
            "tones": [],
            "priority": {"war": 0.5},
        }

        power_score = self.selector.score(power_book)
        ethics_score = self.selector.score(ethics_book)

        self.assertGreater(power_score, ethics_score)

    def test_war_priority_multiplier(self):
        """Books with higher war priority should score higher."""
        base_book = {
            "book_id": "base",
            "domains": ["power"],
            "tones": ["dark"],
        }

        high_priority = base_book.copy()
        high_priority["priority"] = {"war": 1.0}

        low_priority = base_book.copy()
        low_priority["priority"] = {"war": 0.2}

        high_score = self.selector.score(high_priority)
        low_score = self.selector.score(low_priority)

        self.assertGreater(high_score, low_score)

    def test_deprioritized_domain_reduces_score(self):
        """Books with deprioritized domains should score lower."""
        good_book = {
            "book_id": "good",
            "domains": ["power"],
            "tones": [],
            "priority": {"war": 1.0},
        }

        bad_book = {
            "book_id": "bad",
            "domains": ["ethics"],
            "tones": [],
            "priority": {"war": 1.0},
        }

        good_score = self.selector.score(good_book)
        bad_score = self.selector.score(bad_book)

        self.assertGreater(good_score, bad_score)

    def test_audit_breaks_down_scoring(self):
        """Audit should show why a book scored what it did."""
        book = {
            "book_id": "test",
            "title": "Test Book",
            "domains": ["power", "psychology"],
            "tones": ["dark", "strategic"],
            "priority": {"war": 0.8},
        }

        score = self.selector.score(book)
        audit = self.selector.audit(book, score)

        self.assertIn("matching_domains", audit)
        self.assertIn("matching_tones", audit)
        self.assertIn("priority_multiplier", audit)
        self.assertGreater(len(audit["matching_domains"]), 0)

    def test_rank_respects_max_sources(self):
        """Ranking should respect hard_rules.max_sources."""
        books = [
            {
                "book_id": f"book{i}",
                "domains": ["power"],
                "tones": ["dark"],
                "priority": {"war": 0.9},
            }
            for i in range(10)
        ]

        ranked = self.selector.rank(books, limit=5)

        max_sources = WAR_RAG_BIAS["hard_rules"]["max_sources"]
        self.assertLessEqual(len(ranked), max_sources)


class TestBookMetadataLoader(unittest.TestCase):
    """Test Book Metadata Loader."""

    def setUp(self):
        """Create temporary metadata directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = BookMetadataLoader(metadata_dir=self.temp_dir)

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_load_nonexistent_book_returns_default(self):
        """Loading nonexistent book should return default metadata."""
        metadata = self.loader.load_one("nonexistent_book")

        self.assertIn("book_id", metadata)
        self.assertIn("domains", metadata)
        self.assertIn("priority", metadata)

    def test_load_all_empty_directory(self):
        """Loading from empty directory should return empty dict."""
        all_books = self.loader.load_all()

        self.assertEqual(len(all_books), 0)

    def test_cache_persistence(self):
        """Loaded metadata should be cached."""
        meta1 = self.loader.load_one("test_book")
        meta2 = self.loader.load_one("test_book")

        self.assertIs(meta1, meta2)  # Should be same object (cached)

    def test_refresh_clears_cache(self):
        """Refresh should clear cache."""
        meta1 = self.loader.load_one("test_book")
        self.loader.refresh()
        meta2 = self.loader.load_one("test_book")

        self.assertIsNot(meta1, meta2)


class TestTwoPassChunker(unittest.TestCase):
    """Test Two-Pass Semantic Chunker."""

    def setUp(self):
        """Initialize chunker without LLM."""
        self.chunker = TwoPassSemanticChunker(llm_call=None)

    def test_structural_split_creates_chunks(self):
        """Structural split should create multiple chunks from text."""
        text = """
This is an introduction paragraph.

The principle is that charm disarms resistance.

In the story of the rake, we see this play out.

Warning: do not be too obvious about it.
"""

        chunks = self.chunker._structural_split(
            text=text,
            book_id="test_book",
            chapter_title="Test Chapter",
            chapter_num=1,
            page_start=10,
        )

        self.assertGreater(len(chunks), 1)

    def test_label_detection_identifies_principle(self):
        """Label detection should identify 'principle' label."""
        text = "The principle is that slow movements increase attraction."
        label = self.chunker._detect_label(text)
        self.assertEqual(label, "principle")

    def test_label_detection_identifies_story(self):
        """Label detection should identify 'story' label."""
        text = "In the story of the courtesan, she uses this technique."
        label = self.chunker._detect_label(text)
        self.assertEqual(label, "story")

    def test_label_detection_identifies_warning(self):
        """Label detection should identify 'warning' label."""
        text = "Warning: never reveal your strategy directly."
        label = self.chunker._detect_label(text)
        self.assertEqual(label, "warning")

    def test_chunk_has_source_metadata(self):
        """Each chunk should have full source traceability."""
        text = "The principle is charm disarms resistance."

        chunks = self.chunker._structural_split(
            text=text,
            book_id="art_of_seduction",
            chapter_title="The Art of Charm",
            chapter_num=3,
            page_start=112,
        )

        self.assertGreater(len(chunks), 0)
        chunk = chunks[0]

        self.assertIn("source", chunk)
        self.assertEqual(chunk["source"]["book_id"], "art_of_seduction")
        self.assertEqual(chunk["source"]["chapter_title"], "The Art of Charm")

    def test_chunk_format_has_required_fields(self):
        """Chunk should have all required fields."""
        text = "Sample text."

        chunks = self.chunker._structural_split(
            text=text,
            book_id="test",
            chapter_title="Test",
            chapter_num=1,
            page_start=1,
        )

        required_fields = [
            "chunk_id",
            "semantic_label",
            "source",
            "text",
            "start_char",
            "end_char",
        ]

        for field in required_fields:
            self.assertIn(field, chunks[0])

    def test_chunk_id_deterministic(self):
        """Chunk IDs should be deterministic (same input = same ID)."""
        chunk_id1 = self.chunker._make_chunk_id(
            book_id="test", chapter_num=1, page_start=10, chunk_index=0
        )
        chunk_id2 = self.chunker._make_chunk_id(
            book_id="test", chapter_num=1, page_start=10, chunk_index=0
        )

        self.assertEqual(chunk_id1, chunk_id2)


class TestWarModePhilosophy(unittest.TestCase):
    """Test that War Mode philosophy is correctly implemented."""

    def setUp(self):
        """Initialize selector."""
        self.selector = WarRAGSelector()

    def test_dark_texts_always_allowed(self):
        """Dark texts should be allowed and preferred in War Mode."""
        dark_book = {
            "book_id": "48_laws",
            "domains": ["power"],
            "tones": ["dark", "amoral"],
            "priority": {"war": 1.0},
        }

        score = self.selector.score(dark_book)

        # Score should be positive (dark is preferred)
        self.assertGreater(score, 0)

    def test_soft_voices_deprioritized(self):
        """Ethics/harmony texts should score lower."""
        ethics_book = {
            "book_id": "ethics",
            "domains": ["ethics"],
            "tones": ["moral"],
            "priority": {"war": 0.5},
        }

        score = self.selector.score(ethics_book)

        # Score should be lower due to deprioritization
        # (might be negative due to -1.5 domain penalty)
        self.assertLess(score, 2.0)

    def test_manipulation_preferred(self):
        """Books on manipulation should be preferred."""
        manip_book = {
            "book_id": "seduction",
            "domains": ["manipulation", "psychology"],
            "tones": ["dark"],
            "priority": {"war": 1.0},
        }

        score = self.selector.score(manip_book)

        # Should have strong score (manipulation + psychology + dark + high priority)
        self.assertGreater(score, 5.0)


if __name__ == "__main__":
    unittest.main()
