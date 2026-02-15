#!/usr/bin/env python3
"""
Unit tests for schedule detection functionality.

Run with: python -m pytest tests/test_schedule_detection.py -v
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mappings import detect_schedules, SCHEDULE_PATTERNS


class MockPage:
    """Mock pdfplumber page for testing."""

    def __init__(self, text: str):
        self._text = text

    def extract_text(self) -> str:
        return self._text


class MockPDF:
    """Mock pdfplumber PDF for testing."""

    def __init__(self, pages: list):
        self.pages = [MockPage(text) for text in pages]


class TestSchedulePatterns:
    """Tests for schedule pattern definitions."""

    def test_patterns_defined_for_all_schedules(self):
        assert "schedule_1" in SCHEDULE_PATTERNS
        assert "schedule_a" in SCHEDULE_PATTERNS
        assert "schedule_c" in SCHEDULE_PATTERNS

    def test_each_schedule_has_multiple_patterns(self):
        for schedule_type, patterns in SCHEDULE_PATTERNS.items():
            assert len(patterns) >= 2, f"{schedule_type} should have at least 2 patterns"


class TestDetectSchedulesFormOnly:
    """Tests for PDFs with only Form 1040."""

    def test_form_1040_only(self):
        """PDFs with only Form 1040 should return None for all schedules."""
        pdf = MockPDF([
            "Form 1040 2023\nDepartment of the Treasury\nInternal Revenue Service",
            "Page 2 of Form 1040\nTax and Credits"
        ])

        result = detect_schedules(pdf)

        assert result["schedule_1"] is None
        assert result["schedule_a"] is None
        assert result["schedule_c"] is None

    def test_empty_pdf(self):
        """Empty PDFs should return None for all schedules."""
        pdf = MockPDF([])

        result = detect_schedules(pdf)

        assert result["schedule_1"] is None
        assert result["schedule_a"] is None
        assert result["schedule_c"] is None


class TestDetectSchedulesWithScheduleA:
    """Tests for Schedule A detection."""

    def test_schedule_a_detected(self):
        """Schedule A should be detected by primary pattern."""
        pdf = MockPDF([
            "Form 1040 2023\nDepartment of the Treasury",
            "Page 2 of Form 1040",
            "SCHEDULE A (Form 1040)\nItemized Deductions\nMedical and Dental Expenses"
        ])

        result = detect_schedules(pdf)

        assert result["schedule_a"] == 2
        assert result["schedule_1"] is None
        assert result["schedule_c"] is None

    def test_schedule_a_secondary_pattern(self):
        """Schedule A should be detected by secondary pattern."""
        pdf = MockPDF([
            "Form 1040 2023",
            "SCHEDULE A Itemized Deductions\nGo to www.irs.gov/ScheduleA"
        ])

        result = detect_schedules(pdf)

        assert result["schedule_a"] == 1


class TestDetectSchedulesWithSchedule1:
    """Tests for Schedule 1 detection."""

    def test_schedule_1_detected(self):
        """Schedule 1 should be detected by primary pattern."""
        pdf = MockPDF([
            "Form 1040 2023",
            "SCHEDULE 1 (Form 1040)\nAdditional Income and Adjustments to Income"
        ])

        result = detect_schedules(pdf)

        assert result["schedule_1"] == 1
        assert result["schedule_a"] is None
        assert result["schedule_c"] is None

    def test_schedule_1_secondary_pattern(self):
        """Schedule 1 should be detected by secondary pattern."""
        pdf = MockPDF([
            "Form 1040 2023",
            "Page 2",
            "SCHEDULE 1 Additional Income\nPart I Additional Income"
        ])

        result = detect_schedules(pdf)

        assert result["schedule_1"] == 2


class TestDetectSchedulesWithScheduleC:
    """Tests for Schedule C detection."""

    def test_schedule_c_detected(self):
        """Schedule C should be detected by primary pattern."""
        pdf = MockPDF([
            "Form 1040 2023",
            "SCHEDULE C (Form 1040)\nProfit or Loss From Business"
        ])

        result = detect_schedules(pdf)

        assert result["schedule_c"] == 1
        assert result["schedule_1"] is None
        assert result["schedule_a"] is None

    def test_schedule_c_secondary_pattern(self):
        """Schedule C should be detected by secondary pattern."""
        pdf = MockPDF([
            "Form 1040 2023",
            "SCHEDULE C Profit or Loss\n(Sole Proprietorship)"
        ])

        result = detect_schedules(pdf)

        assert result["schedule_c"] == 1


class TestDetectSchedulesMultiple:
    """Tests for PDFs with multiple schedules."""

    def test_multiple_schedules(self):
        """Multiple schedules in one PDF should all be detected."""
        pdf = MockPDF([
            "Form 1040 2023\nDepartment of the Treasury",
            "Page 2 of Form 1040",
            "SCHEDULE 1 (Form 1040)\nAdditional Income",
            "SCHEDULE A (Form 1040)\nItemized Deductions",
            "SCHEDULE C (Form 1040)\nProfit or Loss From Business"
        ])

        result = detect_schedules(pdf)

        assert result["schedule_1"] == 2
        assert result["schedule_a"] == 3
        assert result["schedule_c"] == 4

    def test_schedules_in_different_order(self):
        """Schedules should be detected regardless of order."""
        pdf = MockPDF([
            "Form 1040 2023",
            "SCHEDULE C (Form 1040)\nProfit or Loss",  # C first
            "SCHEDULE A (Form 1040)\nItemized Deductions",  # A second
            "SCHEDULE 1 (Form 1040)\nAdditional Income"  # 1 last
        ])

        result = detect_schedules(pdf)

        assert result["schedule_c"] == 1
        assert result["schedule_a"] == 2
        assert result["schedule_1"] == 3


class TestDetectSchedulesCaseInsensitive:
    """Tests for case-insensitive matching."""

    def test_lowercase_schedule(self):
        """Detection should be case-insensitive."""
        pdf = MockPDF([
            "form 1040 2023",
            "schedule a (form 1040)\nitemized deductions"
        ])

        result = detect_schedules(pdf)

        assert result["schedule_a"] == 1

    def test_mixed_case(self):
        """Mixed case should still be detected."""
        pdf = MockPDF([
            "Form 1040 2023",
            "SCHEDULE 1 (FORM 1040)\nADDITIONAL INCOME AND ADJUSTMENTS TO INCOME"
        ])

        result = detect_schedules(pdf)

        assert result["schedule_1"] == 1


class TestDetectSchedulesFirstOccurrence:
    """Tests that only the first occurrence is recorded."""

    def test_duplicate_schedule_uses_first_page(self):
        """When a schedule appears multiple times, use the first occurrence."""
        pdf = MockPDF([
            "Form 1040 2023",
            "SCHEDULE A (Form 1040)\nPage 1 of Schedule A",
            "Schedule A continued\nPage 2",  # This should not update the page
            "SCHEDULE A (Form 1040) - another reference"  # This should not update
        ])

        result = detect_schedules(pdf)

        # Should be page 1, not page 2 or 3
        assert result["schedule_a"] == 1


class TestDetectSchedulesReturnType:
    """Tests for return type correctness."""

    def test_returns_dict(self):
        """Result should always be a dictionary."""
        pdf = MockPDF(["Form 1040 2023"])

        result = detect_schedules(pdf)

        assert isinstance(result, dict)

    def test_returns_all_schedule_keys(self):
        """Result should contain all schedule types even if not found."""
        pdf = MockPDF(["Form 1040 2023"])

        result = detect_schedules(pdf)

        assert "schedule_1" in result
        assert "schedule_a" in result
        assert "schedule_c" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
