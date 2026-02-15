#!/usr/bin/env python3
"""
Form 1040 PDF Extraction Script

Extracts tax return data from Form 1040 PDFs using coordinate-based extraction.
Uses pdfplumber to read text from specific bounding boxes defined per form year.

Usage:
    python extract.py <pdf_path>
    python extract.py --help

Output:
    JSON object with extracted fields printed to stdout
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional

try:
    import pdfplumber
except ImportError:
    print(json.dumps({
        "error": "pdfplumber not installed. Run: pip install pdfplumber",
        "fields": []
    }))
    sys.exit(1)

from mappings import detect_form_year, detect_schedules, get_field_mapping, get_supported_years


def parse_currency(text: str) -> Optional[str]:
    """
    Parse a currency value from extracted text.

    Args:
        text: Raw text that may contain a dollar amount

    Returns:
        Cleaned numeric string or None if no valid number found
    """
    if not text:
        return None

    # Remove common formatting
    cleaned = text.strip()
    cleaned = re.sub(r'[$,\s]', '', cleaned)  # Remove $, commas, spaces
    cleaned = re.sub(r'\(([0-9.]+)\)', r'-\1', cleaned)  # (123) -> -123

    # Extract just the numeric portion (handles trailing dots, letters, etc.)
    match = re.match(r'^(-?\d+\.?\d*)', cleaned)
    if not match:
        return None

    # Check if it's a valid number
    try:
        value = float(match.group(1))
        # Round to nearest dollar
        return str(int(round(value)))
    except ValueError:
        return None


def extract_filing_status(page) -> str:
    """
    Detect the filing status from Form 1040.

    This is a simplified detection based on text content.
    A more accurate method would check the checkbox positions.
    """
    text = (page.extract_text() or "").lower()

    status_patterns = [
        ("married filing jointly", "Married Filing Jointly"),
        ("married filing separately", "Married Filing Separately"),
        ("head of household", "Head of Household"),
        ("qualifying widow", "Qualifying Surviving Spouse"),
        ("single", "Single"),
    ]

    for pattern, status in status_patterns:
        if pattern in text:
            return status

    return "Single"  # Default


def extract_field(page, bbox: tuple) -> str:
    """
    Extract text from a specific bounding box on a page.

    Uses character-level filtering based on vertical midpoint to avoid
    capturing adjacent values when rows are tightly spaced.

    Args:
        page: pdfplumber page object
        bbox: Tuple of (x0, y0, x1, y1) coordinates

    Returns:
        Extracted text string (may be empty)
    """
    try:
        x0, y0, x1, y1 = bbox

        # Filter characters where the vertical midpoint is within the bbox
        # This avoids capturing characters from adjacent rows that just
        # touch the bbox boundary
        def char_in_bbox(char):
            char_mid_y = (char['top'] + char['bottom']) / 2
            return (x0 <= char['x0'] < x1 and
                    y0 <= char_mid_y < y1)

        chars = [c for c in page.chars if char_in_bbox(c)]

        if not chars:
            return ""

        # Sort by position (left to right)
        chars.sort(key=lambda c: c['x0'])

        # Join characters into text
        text = ''.join(c['text'] for c in chars)
        return text.strip()
    except Exception:
        return ""


def extract_form_1040(pdf_path: str) -> Dict[str, Any]:
    """
    Extract all fields from a Form 1040 PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with year, filing_status, extraction_method, and fields
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return {
                    "error": "PDF has no pages",
                    "year": 0,
                    "filing_status": "Unknown",
                    "extraction_method": "pdfplumber",
                    "fields": []
                }

            # Detect form year from first page
            first_page = pdf.pages[0]
            year = detect_form_year(first_page)

            if year is None:
                # Try to get year from filename as fallback
                year_match = re.search(r'20\d{2}', pdf_path)
                year = int(year_match.group()) if year_match else 0

            # Get field mapping for this year
            field_mapping = get_field_mapping(year) if year else {}

            if not field_mapping:
                return {
                    "error": f"No field mapping available for year {year}",
                    "year": year,
                    "filing_status": "Unknown",
                    "extraction_method": "pdfplumber",
                    "supported_years": get_supported_years(),
                    "fields": []
                }

            # Extract filing status
            filing_status = extract_filing_status(first_page)

            # Extract each field
            fields: List[Dict[str, Any]] = []

            for field_key, config in field_mapping.items():
                page_num = config.get("page", 0)

                # Make sure we have enough pages
                if page_num >= len(pdf.pages):
                    continue

                page = pdf.pages[page_num]
                bbox = config.get("bbox")

                if not bbox:
                    continue

                # Extract raw text from bounding box
                raw_text = extract_field(page, bbox)

                # Parse as currency value
                value = parse_currency(raw_text)

                # Calculate confidence based on whether we got a valid value
                if value and int(value) >= 0:
                    confidence = 0.95  # High confidence for successful extraction
                elif value:
                    confidence = 0.90  # Slightly lower for negative values
                else:
                    confidence = 0.50  # No value extracted - needs review

                fields.append({
                    "key": field_key,
                    "label": config.get("label", field_key),
                    "value": value,
                    "raw_text": raw_text,  # Include raw text for debugging
                    "category": config.get("category", "other"),
                    "line_number": config.get("line", ""),
                    "confidence": confidence,
                    "page": page_num,
                })

            # Detect which schedules are present in the PDF
            schedules = detect_schedules(pdf)

            # Build the detected_forms list
            detected_forms = ["Form 1040"]
            for schedule_type, page_idx in schedules.items():
                if page_idx is not None:
                    # Convert schedule_1 -> Schedule 1, schedule_a -> Schedule A, etc.
                    name = schedule_type.replace("_", " ").title()
                    detected_forms.append(name)

            return {
                "year": year,
                "filing_status": filing_status,
                "extraction_method": "pdfplumber",
                "fields": fields,
                "page_count": len(pdf.pages),
                "detected_forms": detected_forms,
            }

    except FileNotFoundError:
        return {
            "error": f"File not found: {pdf_path}",
            "year": 0,
            "filing_status": "Unknown",
            "extraction_method": "pdfplumber",
            "fields": []
        }
    except Exception as e:
        return {
            "error": str(e),
            "year": 0,
            "filing_status": "Unknown",
            "extraction_method": "pdfplumber",
            "fields": []
        }


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Extract Form 1040 data from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract.py /path/to/tax_return_2018.pdf
    python extract.py --pretty /path/to/1040.pdf
    python extract.py --years
    python extract.py --accuracy-report test-data/sample-returns/

Output is JSON printed to stdout.
        """
    )

    parser.add_argument(
        "pdf_path",
        nargs="?",
        help="Path to the PDF file to extract"
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )

    parser.add_argument(
        "--years",
        action="store_true",
        help="List supported form years and exit"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Include raw text in output for debugging"
    )

    parser.add_argument(
        "--accuracy-report",
        metavar="DIR",
        help="Generate accuracy report for test PDFs in DIR"
    )

    args = parser.parse_args()

    # Handle --years flag
    if args.years:
        years = get_supported_years()
        print(json.dumps({"supported_years": years}))
        return

    # Handle --accuracy-report flag
    if args.accuracy_report:
        from tests.test_accuracy import generate_accuracy_report
        report = generate_accuracy_report(args.accuracy_report)
        print(report.format_report())
        return

    # Require pdf_path if not just listing years
    if not args.pdf_path:
        parser.print_help()
        sys.exit(1)

    # Extract data
    result = extract_form_1040(args.pdf_path)

    # Remove raw_text from fields unless debugging
    if not args.debug:
        for field in result.get("fields", []):
            field.pop("raw_text", None)

    # Output JSON
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
