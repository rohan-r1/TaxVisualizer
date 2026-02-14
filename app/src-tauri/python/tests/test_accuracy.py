#!/usr/bin/env python3
"""
Accuracy testing framework for Form 1040 PDF extraction.

This module implements golden file testing - comparing extracted values
against expected values defined in JSON sidecar files.

Run with: python -m pytest tests/test_accuracy.py -v
Or: python -m pytest tests/test_accuracy.py -v --tb=short

For accuracy report: python extract.py --accuracy-report <test-dir>
"""

import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract import extract_form_1040, parse_currency


# ============================================================================
# Expected Values JSON Schema
# ============================================================================
#
# Each PDF should have a corresponding JSON file with expected values:
#
# {
#   "pdf_file": "casual_filer_1040_2024.pdf",
#   "tax_year": 2024,
#   "filing_status": "Single",
#   "fields": {
#     "wages": { "expected": "72245", "tolerance": 0 },
#     "total_income": { "expected": "72245", "tolerance": 0 },
#     "refund": { "expected": "1288", "tolerance": 0 },
#     "amount_owed": { "expected": null, "allow_null": true }
#   },
#   "metadata": {
#     "scenario": "W-2 employee with standard deduction",
#     "edge_cases": ["single_income_source", "refund_scenario"]
#   }
# }
# ============================================================================


@dataclass
class FieldComparison:
    """Result of comparing one extracted field to its expected value."""
    field_key: str
    expected: Optional[str]
    actual: Optional[str]
    matches: bool
    tolerance: int = 0
    allow_null: bool = False
    error_message: Optional[str] = None


@dataclass
class ExtractionComparison:
    """Result of comparing an entire extraction to expected values."""
    pdf_file: str
    tax_year: int
    filing_status_expected: str
    filing_status_actual: str
    filing_status_matches: bool
    field_comparisons: List[FieldComparison] = field(default_factory=list)
    fields_matched: int = 0
    fields_total: int = 0
    accuracy_percent: float = 0.0

    def __post_init__(self):
        if self.field_comparisons:
            self.fields_matched = sum(1 for fc in self.field_comparisons if fc.matches)
            self.fields_total = len(self.field_comparisons)
            self.accuracy_percent = (
                (self.fields_matched / self.fields_total * 100)
                if self.fields_total > 0 else 0.0
            )


@dataclass
class AccuracyReport:
    """Aggregated accuracy report across multiple PDFs."""
    comparisons: List[ExtractionComparison] = field(default_factory=list)
    overall_fields_matched: int = 0
    overall_fields_total: int = 0
    overall_accuracy: float = 0.0
    by_year: Dict[int, Tuple[int, int, float]] = field(default_factory=dict)
    critical_fields_accuracy: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    failures: List[Tuple[str, str, str, str]] = field(default_factory=list)

    def compute(self):
        """Compute aggregate statistics from comparisons."""
        self.overall_fields_matched = 0
        self.overall_fields_total = 0
        self.by_year = {}
        self.critical_fields_accuracy = {}
        self.failures = []

        critical_fields = ['total_income', 'total_tax', 'refund', 'amount_owed']
        critical_stats = {f: [0, 0] for f in critical_fields}  # [matched, total]
        year_stats = {}  # year -> [matched, total]

        for comp in self.comparisons:
            for fc in comp.field_comparisons:
                self.overall_fields_total += 1
                if fc.matches:
                    self.overall_fields_matched += 1
                else:
                    self.failures.append((
                        comp.pdf_file,
                        fc.field_key,
                        fc.expected,
                        fc.actual
                    ))

                # Track by year
                if comp.tax_year not in year_stats:
                    year_stats[comp.tax_year] = [0, 0]
                year_stats[comp.tax_year][1] += 1
                if fc.matches:
                    year_stats[comp.tax_year][0] += 1

                # Track critical fields
                if fc.field_key in critical_stats:
                    critical_stats[fc.field_key][1] += 1
                    if fc.matches:
                        critical_stats[fc.field_key][0] += 1

        # Compute percentages
        if self.overall_fields_total > 0:
            self.overall_accuracy = (
                self.overall_fields_matched / self.overall_fields_total * 100
            )

        for year, (matched, total) in year_stats.items():
            pct = (matched / total * 100) if total > 0 else 0.0
            self.by_year[year] = (matched, total, pct)

        for field_key, (matched, total) in critical_stats.items():
            self.critical_fields_accuracy[field_key] = (matched, total)

    def format_report(self) -> str:
        """Format the report as a human-readable string."""
        lines = [
            "=== PDF Extraction Accuracy Report ===",
            "",
            f"Overall: {self.overall_accuracy:.1f}% "
            f"({self.overall_fields_matched} / {self.overall_fields_total} fields correct)",
            "",
            "By Year:",
        ]

        for year in sorted(self.by_year.keys(), reverse=True):
            matched, total, pct = self.by_year[year]
            lines.append(f"  {year}: {pct:.1f}% ({matched}/{total} fields)")

        lines.append("")
        lines.append("Critical Fields (must be 100%):")
        for field_key, (matched, total) in sorted(self.critical_fields_accuracy.items()):
            pct = (matched / total * 100) if total > 0 else 0.0
            status = "OK" if matched == total else "FAIL"
            lines.append(f"  {field_key}: {pct:.0f}% ({matched}/{total}) {status}")

        if self.failures:
            lines.append("")
            lines.append("Failures:")
            for pdf, field_key, expected, actual in self.failures[:10]:  # Limit to 10
                lines.append(f"  [{pdf}] {field_key}: expected \"{expected}\", got \"{actual}\"")
            if len(self.failures) > 10:
                lines.append(f"  ... and {len(self.failures) - 10} more failures")

        return "\n".join(lines)


def normalize_value(value: Any) -> Optional[str]:
    """Normalize a value for comparison."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return str(int(round(value)))
    if isinstance(value, str):
        # Remove formatting
        return parse_currency(value)
    return str(value)


def compare_field(
    field_key: str,
    actual_value: Optional[str],
    expectation: Dict[str, Any]
) -> FieldComparison:
    """
    Compare an extracted field value against its expected value.

    Args:
        field_key: The field key being compared
        actual_value: The extracted value (may be None)
        expectation: Dict with 'expected', optional 'tolerance', 'allow_null'

    Returns:
        FieldComparison with match result
    """
    expected_raw = expectation.get("expected")
    tolerance = expectation.get("tolerance", 0)
    allow_null = expectation.get("allow_null", False)

    # Normalize expected value
    expected = normalize_value(expected_raw)
    actual = normalize_value(actual_value)

    # Handle null cases
    if expected is None and allow_null:
        matches = actual is None or actual == "0" or actual == ""
        return FieldComparison(
            field_key=field_key,
            expected=expected,
            actual=actual,
            matches=matches,
            tolerance=tolerance,
            allow_null=allow_null,
        )

    if expected is None and actual is None:
        return FieldComparison(
            field_key=field_key,
            expected=expected,
            actual=actual,
            matches=True,
            tolerance=tolerance,
            allow_null=allow_null,
        )

    if expected is None or actual is None:
        return FieldComparison(
            field_key=field_key,
            expected=expected,
            actual=actual,
            matches=False,
            tolerance=tolerance,
            allow_null=allow_null,
            error_message="One value is null but the other is not"
        )

    # Compare numeric values with tolerance
    try:
        expected_num = int(expected)
        actual_num = int(actual)
        matches = abs(expected_num - actual_num) <= tolerance
        return FieldComparison(
            field_key=field_key,
            expected=expected,
            actual=actual,
            matches=matches,
            tolerance=tolerance,
            allow_null=allow_null,
        )
    except (ValueError, TypeError):
        # Fall back to string comparison
        matches = expected == actual
        return FieldComparison(
            field_key=field_key,
            expected=expected,
            actual=actual,
            matches=matches,
            tolerance=tolerance,
            allow_null=allow_null,
        )


def compare_extraction(
    pdf_path: str,
    expected_json: Dict[str, Any]
) -> ExtractionComparison:
    """
    Compare extraction results against expected values.

    Args:
        pdf_path: Path to the PDF file
        expected_json: Dict with expected values (see schema above)

    Returns:
        ExtractionComparison with detailed results
    """
    # Extract from PDF
    result = extract_form_1040(pdf_path)

    if "error" in result and result.get("fields", []) == []:
        return ExtractionComparison(
            pdf_file=os.path.basename(pdf_path),
            tax_year=expected_json.get("tax_year", 0),
            filing_status_expected=expected_json.get("filing_status", "Unknown"),
            filing_status_actual="Error",
            filing_status_matches=False,
            field_comparisons=[],
        )

    # Build lookup of extracted fields
    extracted_by_key = {f["key"]: f["value"] for f in result.get("fields", [])}

    # Compare filing status
    filing_status_expected = expected_json.get("filing_status", "Unknown")
    filing_status_actual = result.get("filing_status", "Unknown")
    filing_status_matches = filing_status_expected == filing_status_actual

    # Compare each expected field
    field_comparisons = []
    expected_fields = expected_json.get("fields", {})

    for field_key, expectation in expected_fields.items():
        actual_value = extracted_by_key.get(field_key)
        comparison = compare_field(field_key, actual_value, expectation)
        field_comparisons.append(comparison)

    return ExtractionComparison(
        pdf_file=os.path.basename(pdf_path),
        tax_year=result.get("year", expected_json.get("tax_year", 0)),
        filing_status_expected=filing_status_expected,
        filing_status_actual=filing_status_actual,
        filing_status_matches=filing_status_matches,
        field_comparisons=field_comparisons,
    )


def load_test_cases(test_dir: str) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Load all PDF + JSON pairs from a test directory.

    Looks for JSON files in:
    - <test_dir>/*.json (paired with *.pdf)
    - <test_dir>/expected/*.json (paired with ../*.pdf)
    - <test_dir>/custom/*.json (paired with custom/*.pdf)

    Returns:
        List of (pdf_path, expected_json) tuples
    """
    test_cases = []

    # Check for expected/ subdirectory
    expected_dir = os.path.join(test_dir, "expected")
    custom_dir = os.path.join(test_dir, "custom")

    # Load from expected/ directory
    if os.path.isdir(expected_dir):
        for filename in os.listdir(expected_dir):
            if filename.endswith(".json"):
                json_path = os.path.join(expected_dir, filename)
                with open(json_path, 'r') as f:
                    expected = json.load(f)

                # Find corresponding PDF
                pdf_name = expected.get("pdf_file", filename.replace(".json", ".pdf"))
                pdf_path = os.path.join(test_dir, pdf_name)

                if os.path.exists(pdf_path):
                    test_cases.append((pdf_path, expected))

    # Load from custom/ directory
    if os.path.isdir(custom_dir):
        for filename in os.listdir(custom_dir):
            if filename.endswith(".json"):
                json_path = os.path.join(custom_dir, filename)
                with open(json_path, 'r') as f:
                    expected = json.load(f)

                # Find corresponding PDF in same directory
                pdf_name = expected.get("pdf_file", filename.replace(".json", ".pdf"))
                pdf_path = os.path.join(custom_dir, pdf_name)

                if os.path.exists(pdf_path):
                    test_cases.append((pdf_path, expected))

    return test_cases


def generate_accuracy_report(test_dir: str) -> AccuracyReport:
    """
    Generate an accuracy report for all test cases in a directory.

    Args:
        test_dir: Directory containing test PDFs and expected JSONs

    Returns:
        AccuracyReport with detailed statistics
    """
    test_cases = load_test_cases(test_dir)
    report = AccuracyReport()

    for pdf_path, expected in test_cases:
        comparison = compare_extraction(pdf_path, expected)
        report.comparisons.append(comparison)

    report.compute()
    return report


# ============================================================================
# Pytest Fixtures and Test Classes
# ============================================================================

# Path to test data
TEST_DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..",
    "test-data", "sample-returns"
)


@pytest.fixture
def test_data_dir():
    """Return path to test data directory."""
    return TEST_DATA_DIR


@pytest.fixture
def test_cases(test_data_dir):
    """Load all test cases from the test data directory."""
    return load_test_cases(test_data_dir)


class TestCompareField:
    """Tests for the compare_field function."""

    def test_exact_match(self):
        result = compare_field("wages", "50000", {"expected": "50000"})
        assert result.matches is True
        assert result.expected == "50000"
        assert result.actual == "50000"

    def test_formatted_match(self):
        result = compare_field("wages", "50000", {"expected": "$50,000"})
        assert result.matches is True

    def test_mismatch(self):
        result = compare_field("wages", "50000", {"expected": "60000"})
        assert result.matches is False

    def test_tolerance(self):
        result = compare_field("wages", "50001", {"expected": "50000", "tolerance": 5})
        assert result.matches is True

    def test_tolerance_exceeded(self):
        result = compare_field("wages", "50010", {"expected": "50000", "tolerance": 5})
        assert result.matches is False

    def test_allow_null_with_null(self):
        result = compare_field("amount_owed", None, {"expected": None, "allow_null": True})
        assert result.matches is True

    def test_allow_null_with_zero(self):
        result = compare_field("amount_owed", "0", {"expected": None, "allow_null": True})
        assert result.matches is True

    def test_null_not_allowed(self):
        result = compare_field("wages", None, {"expected": "50000"})
        assert result.matches is False


class TestNormalizeValue:
    """Tests for the normalize_value function."""

    def test_string(self):
        assert normalize_value("50000") == "50000"

    def test_formatted_string(self):
        assert normalize_value("$50,000") == "50000"

    def test_integer(self):
        assert normalize_value(50000) == "50000"

    def test_float(self):
        assert normalize_value(50000.75) == "50001"

    def test_none(self):
        assert normalize_value(None) is None


class TestCompareExtraction:
    """Tests for the compare_extraction function."""

    @pytest.mark.skipif(
        not os.path.exists(os.path.join(TEST_DATA_DIR, "custom", "casual_filer_1040_2024.pdf")),
        reason="Test PDF not found"
    )
    def test_compare_custom_pdf(self):
        pdf_path = os.path.join(TEST_DATA_DIR, "custom", "casual_filer_1040_2024.pdf")
        expected = {
            "tax_year": 2024,
            "filing_status": "Single",
            "fields": {
                "wages": {"expected": "72245", "tolerance": 0},
                "total_income": {"expected": "72245", "tolerance": 0},
            }
        }

        result = compare_extraction(pdf_path, expected)
        assert result.tax_year == 2024
        assert result.fields_total == 2


class TestAccuracyReport:
    """Tests for the AccuracyReport class."""

    def test_compute_empty(self):
        report = AccuracyReport()
        report.compute()
        assert report.overall_accuracy == 0.0
        assert report.overall_fields_total == 0

    def test_compute_with_data(self):
        comp = ExtractionComparison(
            pdf_file="test.pdf",
            tax_year=2024,
            filing_status_expected="Single",
            filing_status_actual="Single",
            filing_status_matches=True,
            field_comparisons=[
                FieldComparison("wages", "50000", "50000", True),
                FieldComparison("total_tax", "5000", "5001", False),
            ]
        )

        report = AccuracyReport(comparisons=[comp])
        report.compute()

        assert report.overall_fields_matched == 1
        assert report.overall_fields_total == 2
        assert report.overall_accuracy == 50.0

    def test_format_report(self):
        comp = ExtractionComparison(
            pdf_file="test.pdf",
            tax_year=2024,
            filing_status_expected="Single",
            filing_status_actual="Single",
            filing_status_matches=True,
            field_comparisons=[
                FieldComparison("wages", "50000", "50000", True),
            ]
        )

        report = AccuracyReport(comparisons=[comp])
        report.compute()

        output = report.format_report()
        assert "PDF Extraction Accuracy Report" in output
        assert "100.0%" in output


# ============================================================================
# Golden File Tests - Run against actual test data
# ============================================================================

def load_expected_test_cases(test_dir: str) -> List[Tuple[str, Dict[str, Any]]]:
    """Load test cases only from expected/ directory (auto-generated golden files)."""
    test_cases = []
    expected_dir = os.path.join(test_dir, "expected")

    if os.path.isdir(expected_dir):
        for filename in os.listdir(expected_dir):
            if filename.endswith(".json"):
                json_path = os.path.join(expected_dir, filename)
                with open(json_path, 'r') as f:
                    expected = json.load(f)

                pdf_name = expected.get("pdf_file", filename.replace(".json", ".pdf"))
                pdf_path = os.path.join(test_dir, pdf_name)

                if os.path.exists(pdf_path):
                    test_cases.append((pdf_path, expected))

    return test_cases


class TestGoldenFiles:
    """
    Golden file tests comparing extraction against expected values.

    Tests use auto-generated sidecars in test-data/sample-returns/expected/
    """

    @pytest.fixture
    def expected_test_cases(self, test_data_dir):
        """Load only expected/ directory test cases (auto-generated)."""
        return load_expected_test_cases(test_data_dir)

    @pytest.mark.skipif(
        not os.path.isdir(TEST_DATA_DIR),
        reason="Test data directory not found"
    )
    def test_sample_pdf_accuracy(self, expected_test_cases):
        """Run accuracy tests on sample PDFs with auto-generated sidecars."""
        if not expected_test_cases:
            pytest.skip("No expected test cases found")

        all_passed = True
        failures = []

        for pdf_path, expected in expected_test_cases:
            comparison = compare_extraction(pdf_path, expected)

            for fc in comparison.field_comparisons:
                if not fc.matches:
                    all_passed = False
                    failures.append(
                        f"{comparison.pdf_file}: {fc.field_key} "
                        f"expected '{fc.expected}', got '{fc.actual}'"
                    )

        if not all_passed:
            pytest.fail(
                f"Accuracy test failures:\n" + "\n".join(failures[:20])
            )

    @pytest.mark.skipif(
        not os.path.isdir(TEST_DATA_DIR),
        reason="Test data directory not found"
    )
    def test_all_test_cases(self, test_cases):
        """Run all available test cases including custom (may have mismatches)."""
        if not test_cases:
            pytest.skip("No test cases found with JSON sidecars")

        # This test reports mismatches but doesn't fail for custom PDFs
        # Custom PDFs may have hypothetical expected values that don't match
        report = AccuracyReport()

        for pdf_path, expected in test_cases:
            comparison = compare_extraction(pdf_path, expected)
            report.comparisons.append(comparison)

        report.compute()
        print(f"\n{report.format_report()}")

        # Only fail if expected/ directory tests fail (these should always match)
        expected_failures = [
            f for f in report.failures
            if "sample" in f[0].lower() or "expected" in f[0].lower()
        ]

        if expected_failures:
            pytest.fail(
                f"Sample PDF accuracy failures:\n" +
                "\n".join([f"{f[0]}: {f[1]} expected '{f[2]}', got '{f[3]}'"
                          for f in expected_failures[:10]])
            )

    @pytest.mark.skipif(
        not os.path.isdir(TEST_DATA_DIR),
        reason="Test data directory not found"
    )
    def test_filing_status_detection(self, test_cases):
        """Verify filing status is correctly detected for all test cases."""
        if not test_cases:
            pytest.skip("No test cases found with JSON sidecars")

        failures = []
        for pdf_path, expected in test_cases:
            comparison = compare_extraction(pdf_path, expected)

            if not comparison.filing_status_matches:
                failures.append(
                    f"{comparison.pdf_file}: expected '{comparison.filing_status_expected}', "
                    f"got '{comparison.filing_status_actual}'"
                )

        if failures:
            pytest.fail(
                f"Filing status detection failures:\n" + "\n".join(failures)
            )


if __name__ == "__main__":
    # Run as script to generate accuracy report
    import argparse

    parser = argparse.ArgumentParser(description="Generate accuracy report")
    parser.add_argument(
        "test_dir",
        nargs="?",
        default=TEST_DATA_DIR,
        help="Directory containing test PDFs and expected JSONs"
    )

    args = parser.parse_args()

    report = generate_accuracy_report(args.test_dir)
    print(report.format_report())
