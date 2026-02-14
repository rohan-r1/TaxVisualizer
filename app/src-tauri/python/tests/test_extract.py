#!/usr/bin/env python3
"""
Unit tests for Form 1040 PDF extraction.

Run with: python -m pytest tests/ -v
Or: python -m pytest tests/test_extract.py -v
"""

import json
import os
import sys
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract import parse_currency, extract_form_1040
from mappings import detect_form_year, get_field_mapping, get_supported_years

# Path to test data
TEST_DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..",
    "test-data", "sample-returns"
)


class TestParseCurrency:
    """Tests for the parse_currency function."""

    def test_simple_number(self):
        assert parse_currency("12345") == "12345"

    def test_number_with_commas(self):
        assert parse_currency("1,234,567") == "1234567"

    def test_number_with_dollar_sign(self):
        assert parse_currency("$50,000") == "50000"

    def test_number_with_decimal(self):
        assert parse_currency("1,234.56") == "1235"  # Rounds to nearest dollar

    def test_negative_in_parentheses(self):
        assert parse_currency("(500)") == "-500"

    def test_number_with_trailing_dots(self):
        assert parse_currency("44,682..") == "44682"

    def test_number_with_spaces(self):
        assert parse_currency("  30,262  ") == "30262"

    def test_empty_string(self):
        assert parse_currency("") is None

    def test_none_input(self):
        assert parse_currency(None) is None

    def test_non_numeric(self):
        assert parse_currency("abc") is None

    def test_mixed_with_leading_number(self):
        assert parse_currency("125,189.abc") == "125189"


class TestGetSupportedYears:
    """Tests for get_supported_years function."""

    def test_returns_list(self):
        years = get_supported_years()
        assert isinstance(years, list)

    def test_contains_expected_years(self):
        years = get_supported_years()
        assert 2018 in years
        assert 2019 in years
        assert 2020 in years
        assert 2021 in years
        assert 2022 in years
        assert 2023 in years
        assert 2024 in years
        assert 2025 in years

    def test_sorted(self):
        years = get_supported_years()
        assert years == sorted(years)


class TestGetFieldMapping:
    """Tests for get_field_mapping function."""

    def test_returns_dict(self):
        mapping = get_field_mapping(2018)
        assert isinstance(mapping, dict)

    def test_has_required_fields(self):
        mapping = get_field_mapping(2018)
        assert "total_income" in mapping
        assert "total_tax" in mapping

    def test_field_has_bbox(self):
        mapping = get_field_mapping(2018)
        field = mapping["total_income"]
        assert "bbox" in field
        assert len(field["bbox"]) == 4

    def test_fallback_to_closest_year(self):
        # 2023 doesn't have a mapping, should fall back
        mapping = get_field_mapping(2023)
        assert isinstance(mapping, dict)
        assert len(mapping) > 0


@pytest.mark.skipif(
    not os.path.exists(os.path.join(TEST_DATA_DIR, "1040_2018_sample.pdf")),
    reason="Test PDF not found"
)
class TestExtractForm1040:
    """Integration tests for extract_form_1040 function."""

    def test_extract_2018(self):
        pdf_path = os.path.join(TEST_DATA_DIR, "1040_2018_sample.pdf")
        result = extract_form_1040(pdf_path)

        assert result["year"] == 2018
        assert result["filing_status"] == "Married Filing Jointly"
        assert result["extraction_method"] == "pdfplumber"
        assert "fields" in result
        assert len(result["fields"]) > 0

        # Check specific field values
        fields_by_key = {f["key"]: f for f in result["fields"]}
        assert fields_by_key["total_income"]["value"] == "30262"
        assert fields_by_key["total_tax"]["value"] == "46014"

    def test_extract_2019(self):
        pdf_path = os.path.join(TEST_DATA_DIR, "1040_2019_sample.pdf")
        result = extract_form_1040(pdf_path)

        assert result["year"] == 2019
        assert "fields" in result

        fields_by_key = {f["key"]: f for f in result["fields"]}
        assert fields_by_key["wages"]["value"] == "526918"
        assert fields_by_key["total_tax"]["value"] == "125189"

    def test_extract_2020(self):
        pdf_path = os.path.join(TEST_DATA_DIR, "1040_2020_sample.pdf")
        result = extract_form_1040(pdf_path)

        assert result["year"] == 2020
        assert "fields" in result

        fields_by_key = {f["key"]: f for f in result["fields"]}
        assert fields_by_key["wages"]["value"] == "502213"
        assert fields_by_key["taxable_income"]["value"] == "479531"

    def test_extract_2021(self):
        pdf_path = os.path.join(TEST_DATA_DIR, "1040_2021_sample.pdf")
        result = extract_form_1040(pdf_path)

        assert result["year"] == 2021
        assert "fields" in result

        fields_by_key = {f["key"]: f for f in result["fields"]}
        assert fields_by_key["wages"]["value"] == "60500"
        assert fields_by_key["total_tax"]["value"] == "11187"

    def test_file_not_found(self):
        result = extract_form_1040("/nonexistent/path/file.pdf")
        assert "error" in result
        assert result["year"] == 0

    def test_output_is_json_serializable(self):
        pdf_path = os.path.join(TEST_DATA_DIR, "1040_2018_sample.pdf")
        result = extract_form_1040(pdf_path)
        # Should not raise
        json.dumps(result)


class TestFieldCategories:
    """Tests for field categorization."""

    def test_2018_categories(self):
        mapping = get_field_mapping(2018)
        categories = set(f["category"] for f in mapping.values())

        assert "income" in categories
        assert "tax_computation" in categories
        assert "refund_owed" in categories

    def test_all_fields_have_required_keys(self):
        for year in get_supported_years():
            mapping = get_field_mapping(year)
            for key, field in mapping.items():
                assert "page" in field, f"Missing 'page' in {year}/{key}"
                assert "bbox" in field, f"Missing 'bbox' in {year}/{key}"
                assert "label" in field, f"Missing 'label' in {year}/{key}"
                assert "category" in field, f"Missing 'category' in {year}/{key}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
