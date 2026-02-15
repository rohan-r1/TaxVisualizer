#!/usr/bin/env python3
"""
Unit tests for schedule field extraction.

Run with: python -m pytest tests/test_schedule_extraction.py -v
"""

import os
import sys
import pytest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mappings import get_schedule_mapping, get_schedule_supported_years, SCHEDULE_MAPPINGS
from extract import extract_form_1040, extract_schedule_fields

# Test data paths
TEST_DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "test-data"
GENERATED_DIR = TEST_DATA_DIR / "generated"
TEMPLATES_DIR = TEST_DATA_DIR / "blank-templates"


class TestScheduleMappingRegistry:
    """Tests for schedule mapping registry."""

    def test_all_schedule_types_registered(self):
        """All schedule types should be registered."""
        assert "schedule_1" in SCHEDULE_MAPPINGS
        assert "schedule_a" in SCHEDULE_MAPPINGS
        assert "schedule_c" in SCHEDULE_MAPPINGS

    def test_all_years_available(self):
        """Each schedule should have mappings for 2018-2024."""
        expected_years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]

        for schedule_type in ["schedule_1", "schedule_a", "schedule_c"]:
            supported = get_schedule_supported_years(schedule_type)
            for year in expected_years:
                assert year in supported, f"{schedule_type} missing year {year}"


class TestGetScheduleMapping:
    """Tests for get_schedule_mapping function."""

    def test_exact_year_match(self):
        """Should return exact year mapping when available."""
        mapping = get_schedule_mapping("schedule_1", 2024)
        assert len(mapping) > 0
        assert "sched1_taxable_refunds" in mapping

    def test_fallback_to_closest_year(self):
        """Should fall back to closest year when exact year not available."""
        # 2025 doesn't exist, should fall back to 2024
        mapping = get_schedule_mapping("schedule_1", 2025)
        assert len(mapping) > 0
        assert "sched1_taxable_refunds" in mapping

    def test_unknown_schedule_returns_empty(self):
        """Unknown schedule type should return empty dict."""
        mapping = get_schedule_mapping("schedule_z", 2024)
        assert mapping == {}


class TestScheduleFieldMappings:
    """Tests for field mapping content."""

    def test_schedule_1_key_fields(self):
        """Schedule 1 should have key income and adjustment fields."""
        mapping = get_schedule_mapping("schedule_1", 2024)

        # Part I - Additional Income
        assert "sched1_business_income" in mapping
        assert "sched1_rental_income" in mapping
        assert "sched1_unemployment" in mapping

        # Part II - Adjustments
        assert "sched1_hsa_deduction" in mapping
        assert "sched1_student_loan_interest" in mapping
        assert "sched1_total_adjustments" in mapping

    def test_schedule_a_key_fields(self):
        """Schedule A should have key itemized deduction fields."""
        mapping = get_schedule_mapping("schedule_a", 2024)

        # Medical
        assert "scheda_medical_expenses" in mapping

        # Taxes (SALT)
        assert "scheda_salt_deduction" in mapping

        # Interest
        assert "scheda_mortgage_interest_1098" in mapping
        assert "scheda_total_interest" in mapping

        # Charity
        assert "scheda_charity_cash" in mapping
        assert "scheda_total_charity" in mapping

        # Total
        assert "scheda_total_itemized" in mapping

    def test_schedule_c_key_fields(self):
        """Schedule C should have key business income and expense fields."""
        mapping = get_schedule_mapping("schedule_c", 2024)

        # Income
        assert "schedc_gross_receipts" in mapping
        assert "schedc_gross_profit" in mapping
        assert "schedc_gross_income" in mapping

        # Expenses
        assert "schedc_total_expenses" in mapping
        assert "schedc_net_profit" in mapping

    def test_all_fields_have_required_attributes(self):
        """All field mappings should have required attributes."""
        for schedule_type in ["schedule_1", "schedule_a", "schedule_c"]:
            mapping = get_schedule_mapping(schedule_type, 2024)

            for field_key, field_info in mapping.items():
                assert "page" in field_info, f"{field_key} missing 'page'"
                assert "bbox" in field_info, f"{field_key} missing 'bbox'"
                assert "label" in field_info, f"{field_key} missing 'label'"
                assert "category" in field_info, f"{field_key} missing 'category'"

                # Validate bbox format
                bbox = field_info["bbox"]
                assert len(bbox) == 4, f"{field_key} bbox should have 4 coordinates"
                assert all(isinstance(c, (int, float)) for c in bbox)


class TestScheduleExtractionWithGeneratedPDFs:
    """Integration tests using generated test PDFs."""

    @pytest.fixture
    def alex_chen_2024_pdf(self):
        """Path to Alex Chen 2024 PDF (has Schedule 1)."""
        path = GENERATED_DIR / "alex_chen" / "1040_2024.pdf"
        if not path.exists():
            pytest.skip("Test data not generated. Run generate_sample_returns.py first.")
        return str(path)

    @pytest.fixture
    def maria_garcia_2024_pdf(self):
        """Path to Maria Garcia 2024 PDF (has Schedule A)."""
        path = GENERATED_DIR / "maria_garcia" / "1040_2024.pdf"
        if not path.exists():
            pytest.skip("Test data not generated. Run generate_sample_returns.py first.")
        return str(path)

    def test_extracts_schedule_1_fields(self, alex_chen_2024_pdf):
        """Should extract Schedule 1 fields from multi-page PDF."""
        result = extract_form_1040(alex_chen_2024_pdf)

        assert "Schedule 1" in result.get("detected_forms", [])

        # Find Schedule 1 fields
        fields = result.get("fields", [])
        schedule_1_fields = [f for f in fields if f["category"] == "schedule_1"]

        # Should have Schedule 1 fields
        assert len(schedule_1_fields) > 0, "No Schedule 1 fields extracted"

        # Check for expected fields with values (Alex has HSA and educator expenses)
        field_keys = {f["key"] for f in schedule_1_fields}
        assert "sched1_hsa_deduction" in field_keys or "sched1_total_adjustments" in field_keys

    def test_extracts_schedule_a_fields(self, maria_garcia_2024_pdf):
        """Should extract Schedule A fields from multi-page PDF."""
        result = extract_form_1040(maria_garcia_2024_pdf)

        assert "Schedule A" in result.get("detected_forms", [])

        # Find Schedule A fields
        fields = result.get("fields", [])
        schedule_a_fields = [f for f in fields if f["category"] == "schedule_a"]

        # Should have Schedule A fields
        assert len(schedule_a_fields) > 0, "No Schedule A fields extracted"

        # Check for expected fields
        field_keys = {f["key"] for f in schedule_a_fields}
        assert "scheda_total_itemized" in field_keys

    def test_multi_schedule_pdf_page_count(self, alex_chen_2024_pdf):
        """PDF with schedules should have more than 2 pages."""
        result = extract_form_1040(alex_chen_2024_pdf)

        # Form 1040 (2 pages) + Schedule 1 (2 pages) = 4 pages
        assert result.get("page_count", 0) >= 3

    def test_form_1040_fields_still_extracted(self, maria_garcia_2024_pdf):
        """Form 1040 fields should still be extracted alongside schedule fields."""
        result = extract_form_1040(maria_garcia_2024_pdf)

        fields = result.get("fields", [])

        # Should have income fields from Form 1040
        income_fields = [f for f in fields if f["category"] == "income"]
        assert len(income_fields) > 0, "No income fields extracted"

        # Should have wages field
        wages_field = next((f for f in fields if f["key"] == "wages"), None)
        assert wages_field is not None


class TestScheduleExtractionWithBlankTemplates:
    """Tests using blank IRS templates to verify detection works."""

    @pytest.fixture
    def schedule_1_template(self):
        """Path to Schedule 1 template."""
        path = TEMPLATES_DIR / "f1040s1--2024.pdf"
        if not path.exists():
            pytest.skip("Schedule 1 template not found")
        return str(path)

    @pytest.fixture
    def schedule_a_template(self):
        """Path to Schedule A template."""
        path = TEMPLATES_DIR / "f1040sa--2024.pdf"
        if not path.exists():
            pytest.skip("Schedule A template not found")
        return str(path)

    @pytest.fixture
    def schedule_c_template(self):
        """Path to Schedule C template."""
        path = TEMPLATES_DIR / "f1040sc--2024.pdf"
        if not path.exists():
            pytest.skip("Schedule C template not found")
        return str(path)

    def test_schedule_1_template_detected(self, schedule_1_template):
        """Schedule 1 template should be detected and fields extracted."""
        result = extract_form_1040(schedule_1_template)

        assert "Schedule 1" in result.get("detected_forms", [])

        # Should have schedule_1 category fields
        fields = result.get("fields", [])
        s1_fields = [f for f in fields if f["category"] == "schedule_1"]
        assert len(s1_fields) > 0

    def test_schedule_a_template_detected(self, schedule_a_template):
        """Schedule A template should be detected and fields extracted."""
        result = extract_form_1040(schedule_a_template)

        assert "Schedule A" in result.get("detected_forms", [])

        # Should have schedule_a category fields
        fields = result.get("fields", [])
        sa_fields = [f for f in fields if f["category"] == "schedule_a"]
        assert len(sa_fields) > 0

    def test_schedule_c_template_detected(self, schedule_c_template):
        """Schedule C template should be detected and fields extracted."""
        result = extract_form_1040(schedule_c_template)

        assert "Schedule C" in result.get("detected_forms", [])

        # Should have schedule_c category fields
        fields = result.get("fields", [])
        sc_fields = [f for f in fields if f["category"] == "schedule_c"]
        assert len(sc_fields) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
