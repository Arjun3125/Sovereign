"""
Tests for Ingestion v2: Two-pass doctrine compiler.

Coverage:
- Phase-1 schema validation
- Phase-2 schema validation
- Progress tracking
- End-to-end mock ingestion
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

from cold_strategist.ingest.core.validators import validate_phase1, validate_phase2, ValidationError
from cold_strategist.ingest.core.progress import Progress
from cold_strategist.ingest.core.phase1_structure import phase1_structure
from cold_strategist.ingest.core.phase2_doctrine import phase2_doctrine
from cold_strategist.ingest.core.ingest_v2 import ingest_v2


class TestPhase1Validation:
    """Tests for Phase-1 output schema."""

    def test_valid_phase1_minimal(self):
        """Minimal valid Phase-1 response."""
        data = {
            "book_title": "The Art of War",
            "author": None,
            "chapters": [
                {
                    "chapter_index": 1,
                    "chapter_title": "Laying Plans",
                    "chapter_text": "Sun Tzu said..."
                }
            ]
        }
        validate_phase1(data)  # Should not raise

    def test_valid_phase1_multiple_chapters(self):
        """Phase-1 with multiple chapters."""
        data = {
            "book_title": "The Art of War",
            "author": None,
            "chapters": [
                {
                    "chapter_index": 1,
                    "chapter_title": "Laying Plans",
                    "chapter_text": "Chapter 1 content"
                },
                {
                    "chapter_index": 2,
                    "chapter_title": "Waging War",
                    "chapter_text": "Chapter 2 content"
                }
            ]
        }
        validate_phase1(data)

    def test_invalid_phase1_not_dict(self):
        """Phase-1 response not a dict."""
        with pytest.raises(ValidationError, match="must be dict"):
            validate_phase1([])

    def test_invalid_phase1_missing_chapters(self):
        """Phase-1 missing 'chapters' key."""
        data = {"book_title": "Test", "author": None}
        with pytest.raises(ValidationError, match="Missing 'chapters'"):
            validate_phase1(data)

    def test_invalid_phase1_empty_chapters(self):
        """Phase-1 with empty chapters list."""
        data = {"chapters": []}
        with pytest.raises(ValidationError, match="non-empty list"):
            validate_phase1(data)

    def test_invalid_phase1_chapter_wrong_index(self):
        """Chapter index does not match position."""
        data = {
            "chapters": [
                {
                    "chapter_index": 99,  # Wrong!
                    "chapter_title": "Laying Plans",
                    "chapter_text": "Content"
                }
            ]
        }
        with pytest.raises(ValidationError, match="wrong index"):
            validate_phase1(data)

    def test_invalid_phase1_chapter_text_not_string(self):
        """Chapter text is not a string."""
        data = {
            "chapters": [
                {
                    "chapter_index": 1,
                    "chapter_title": "Laying Plans",
                    "chapter_text": 12345  # Not a string
                }
            ]
        }
        with pytest.raises(ValidationError, match="not string"):
            validate_phase1(data)


class TestPhase2Validation:
    """Tests for Phase-2 output schema."""

    def test_valid_phase2_minimal(self):
        """Minimal valid Phase-2 response."""
        data = {
            "chapter_index": 1,
            "chapter_title": "Laying Plans",
            "domains": ["Strategy", "Deception"],
            "principles": ["All warfare is based on deception"],
            "rules": ["Understand the enemy"],
            "claims": ["Victory can be achieved"],
            "warnings": ["Haste leads to defeat"],
            "cross_references": []
        }
        validate_phase2(data)  # Should not raise

    def test_valid_phase2_full(self):
        """Phase-2 with all fields populated."""
        data = {
            "chapter_index": 1,
            "chapter_title": "Laying Plans",
            "domains": ["Strategy", "Deception", "Psychology"],
            "principles": [
                "All warfare is based on deception",
                "Know yourself and know your enemy"
            ],
            "rules": [
                "Appear weak when strong",
                "Appear strong when weak"
            ],
            "claims": [
                "Victory achieved through superior strategy"
            ],
            "warnings": [
                "Prolonged warfare exhausts resources"
            ],
            "cross_references": [2, 3, 5]
        }
        validate_phase2(data)

    def test_invalid_phase2_not_dict(self):
        """Phase-2 response not a dict."""
        with pytest.raises(ValidationError, match="must be dict"):
            validate_phase2([])

    def test_invalid_phase2_missing_required_key(self):
        """Phase-2 missing required key."""
        data = {"chapter_index": 1}  # Missing many keys
        with pytest.raises(ValidationError, match="Missing required key"):
            validate_phase2(data)

    def test_invalid_phase2_invalid_domain(self):
        """Phase-2 contains invalid domain."""
        data = {
            "chapter_index": 1,
            "chapter_title": "Test",
            "domains": ["InvalidDomain"],
            "principles": [],
            "rules": [],
            "claims": [],
            "warnings": [],
            "cross_references": []
        }
        with pytest.raises(ValidationError, match="Invalid domain"):
            validate_phase2(data)

    def test_invalid_phase2_non_string_in_principles(self):
        """Principles contains non-string."""
        data = {
            "chapter_index": 1,
            "chapter_title": "Test",
            "domains": ["Strategy"],
            "principles": [123],  # Not a string
            "rules": [],
            "claims": [],
            "warnings": [],
            "cross_references": []
        }
        with pytest.raises(ValidationError, match="non-string"):
            validate_phase2(data)

    def test_invalid_phase2_empty_string_in_rules(self):
        """Rules contains empty string."""
        data = {
            "chapter_index": 1,
            "chapter_title": "Test",
            "domains": ["Strategy"],
            "principles": [],
            "rules": [""],  # Empty string
            "claims": [],
            "warnings": [],
            "cross_references": []
        }
        with pytest.raises(ValidationError, match="Empty string"):
            validate_phase2(data)

    def test_invalid_phase2_insufficient_content(self):
        """No principles or rules (sparse extraction)."""
        data = {
            "chapter_index": 1,
            "chapter_title": "Test",
            "domains": ["Strategy"],
            "principles": [],
            "rules": [],
            "claims": ["Some claim"],
            "warnings": [],
            "cross_references": []
        }
        with pytest.raises(ValidationError, match="No principles or rules"):
            validate_phase2(data)

    def test_invalid_phase2_no_assertions(self):
        """No claims or warnings (missing assertions)."""
        data = {
            "chapter_index": 1,
            "chapter_title": "Test",
            "domains": ["Strategy"],
            "principles": ["A principle"],
            "rules": [],
            "claims": [],
            "warnings": [],
            "cross_references": []
        }
        with pytest.raises(ValidationError, match="No claims or warnings"):
            validate_phase2(data)

    def test_invalid_phase2_no_domains(self):
        """No domains extracted (should fail)."""
        data = {
            "chapter_index": 1,
            "chapter_title": "Test",
            "domains": [],
            "principles": ["A principle"],
            "rules": ["A rule"],
            "claims": ["A claim"],
            "warnings": [],
            "cross_references": []
        }
        with pytest.raises(ValidationError, match="No domains extracted"):
            validate_phase2(data)

    def test_invalid_phase2_non_int_in_cross_references(self):
        """Cross-references contains non-integer."""
        data = {
            "chapter_index": 1,
            "chapter_title": "Test",
            "domains": ["Strategy"],
            "principles": [],
            "rules": [],
            "claims": [],
            "warnings": [],
            "cross_references": ["2"]  # String instead of int
        }
        with pytest.raises(ValidationError, match="non-int"):
            validate_phase2(data)


class TestProgress:
    """Tests for progress tracking."""

    def test_progress_init(self):
        """Progress initialization."""
        prog = Progress(13)
        assert prog.total_chapters == 13
        assert prog.total_units == 14  # 1 for Phase-1 + 13 for chapters

    def test_progress_phase1_complete(self, capsys):
        """Mark Phase-1 as complete."""
        prog = Progress(5)
        prog.phase1_complete()
        assert prog.completed_units == 1
        captured = capsys.readouterr()
        assert "Phase-1" in captured.out
        assert "16%" in captured.out  # 1 / 6 = 16%

    def test_progress_chapter_ingested(self, capsys):
        """Ingest chapters and track progress."""
        prog = Progress(5)
        prog.phase1_complete()

        for i in range(1, 6):
            prog.chapter_ingested(i, f"Chapter {i}")

        captured = capsys.readouterr()
        assert "5/5 chapters" in captured.out
        assert "100%" in captured.out

    def test_progress_complete(self, capsys):
        """Mark ingestion as complete."""
        prog = Progress(2)
        prog.complete()
        assert prog.completed_units == 3  # 1 + 2
        captured = capsys.readouterr()
        assert "100%" in captured.out


class TestPhase1Integration:
    """Integration tests for Phase-1."""

    @patch('ingestion_v2.phase1_structure.call_llm')
    def test_phase1_structure_valid_response(self, mock_llm):
        """Phase-1 with valid LLM response."""
        mock_llm.return_value = {
            "book_title": "The Art of War",
            "author": None,
            "chapters": [
                {
                    "chapter_index": 1,
                    "chapter_title": "Laying Plans",
                    "chapter_text": "Sun Tzu said..."
                }
            ]
        }

        result = phase1_structure("dummy book text")
        assert len(result["chapters"]) == 1
        assert result["chapters"][0]["chapter_index"] == 1

    @patch('ingestion_v2.phase1_structure.call_llm')
    def test_phase1_structure_invalid_schema(self, mock_llm):
        """Phase-1 with invalid schema from LLM."""
        mock_llm.return_value = {
            "chapters": []  # Empty!
        }

        with pytest.raises(ValidationError):
            phase1_structure("dummy book text")


class TestPhase2Integration:
    """Integration tests for Phase-2."""

    @patch('ingestion_v2.phase2_doctrine.call_llm')
    def test_phase2_doctrine_valid_response(self, mock_llm):
        """Phase-2 with valid LLM response."""
        mock_llm.return_value = {
            "chapter_index": 1,
            "chapter_title": "Laying Plans",
            "domains": ["Strategy", "Deception"],
            "principles": ["All warfare is based on deception"],
            "rules": ["Understand the enemy"],
            "claims": ["Victory through strategy"],
            "warnings": ["Haste leads to defeat"],
            "cross_references": []
        }

        chapter = {
            "chapter_index": 1,
            "chapter_title": "Laying Plans",
            "chapter_text": "Sun Tzu said..."
        }

        result = phase2_doctrine(chapter)
        assert result["chapter_index"] == 1
        assert "Strategy" in result["domains"]

    @patch('ingestion_v2.phase2_doctrine.call_llm')
    def test_phase2_doctrine_invalid_schema(self, mock_llm):
        """Phase-2 with invalid schema from LLM."""
        mock_llm.return_value = {
            "chapter_index": 1,
            "domains": ["InvalidDomain"]  # Invalid!
        }

        chapter = {
            "chapter_index": 1,
            "chapter_title": "Test",
            "chapter_text": "Content"
        }

        with pytest.raises(ValidationError):
            phase2_doctrine(chapter)


class TestEndToEndIngestion:
    """End-to-end ingestion tests."""

    @patch('ingestion_v2.ingest_v2.phase1_structure')
    @patch('ingestion_v2.ingest_v2.phase2_doctrine')
    def test_ingest_v2_full_flow(self, mock_phase2, mock_phase1):
        """Full end-to-end ingestion."""
        # Mock Phase-1
        mock_phase1.return_value = {
            "book_title": "The Art of War",
            "author": None,
            "chapters": [
                {
                    "chapter_index": 1,
                    "chapter_title": "Laying Plans",
                    "chapter_text": "Chapter 1 content"
                },
                {
                    "chapter_index": 2,
                    "chapter_title": "Waging War",
                    "chapter_text": "Chapter 2 content"
                }
            ]
        }

        # Mock Phase-2
        mock_phase2.return_value = {
            "chapter_index": 1,
            "chapter_title": "Laying Plans",
            "domains": ["Strategy"],
            "principles": [],
            "rules": [],
            "claims": [],
            "warnings": [],
            "cross_references": []
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = ingest_v2(
                "dummy book text",
                "test_book",
                output_dir=tmpdir
            )

            assert result["book_id"] == "test_book"
            assert result["chapters_ingested"] == 2
            assert os.path.exists(result["structure_path"])

            # Verify structure saved
            with open(result["structure_path"]) as f:
                structure = json.load(f)
                assert len(structure["chapters"]) == 2

    @patch('ingestion_v2.ingest_v2.phase1_structure')
    @patch('ingestion_v2.ingest_v2.phase2_doctrine')
    def test_ingest_v2_resume_safe(self, mock_phase2, mock_phase1):
        """Ingestion is resume-safe (skips existing chapters)."""
        mock_phase1.return_value = {
            "book_title": "Test",
            "author": None,
            "chapters": [
                {
                    "chapter_index": 1,
                    "chapter_title": "Ch1",
                    "chapter_text": "Content 1"
                }
            ]
        }

        mock_phase2.return_value = {
            "chapter_index": 1,
            "chapter_title": "Ch1",
            "domains": ["Strategy"],
            "principles": [],
            "rules": [],
            "claims": [],
            "warnings": [],
            "cross_references": []
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # First ingestion
            ingest_v2("book text", "test_resume", output_dir=tmpdir)

            # Reset mock call count
            mock_phase2.reset_mock()

            # Second ingestion (resume)
            ingest_v2("book text", "test_resume", output_dir=tmpdir)

            # Phase-2 should not be called again (chapter already exists)
            assert mock_phase2.call_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
