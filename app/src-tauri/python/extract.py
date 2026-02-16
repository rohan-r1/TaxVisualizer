#!/usr/bin/env python3
"""
Form 1040 PDF Extraction Script

Extracts tax return data from Form 1040 PDFs using PaddleOCR and label-based
field mapping. Works with both digital and scanned PDFs.

Usage:
    python extract.py <pdf_path>
    python extract.py --help

Output:
    Progress messages to stderr (for UI progress indicator)
    JSON object with extracted fields to stdout
"""

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Fix Windows encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def progress(message: str):
    """Output progress message to stderr for UI consumption."""
    print(message, file=sys.stderr, flush=True)


@dataclass
class OCRResult:
    """Represents a single OCR text detection result."""
    text: str
    confidence: float
    page: int
    bbox: list  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

    @property
    def center_x(self) -> float:
        return sum(p[0] for p in self.bbox) / 4

    @property
    def center_y(self) -> float:
        return sum(p[1] for p in self.bbox) / 4

    @property
    def right_x(self) -> float:
        return max(p[0] for p in self.bbox)

    @property
    def left_x(self) -> float:
        return min(p[0] for p in self.bbox)


# =============================================================================
# Field Definitions
# =============================================================================
# Each field has label patterns to search for and optional line number patterns.
# Labels are ordered by specificity (most specific first).

FORM_1040_FIELDS = {
    # Income section
    'wages': {
        'labels': ['wages, salaries, tips', 'total from form(s) w-2'],
        'line_patterns': ['1a'],
        'category': 'income',
        'label': 'Wages, salaries, tips'
    },
    'taxable_interest': {
        'labels': ['taxable interest'],
        'line_patterns': ['2b'],
        'category': 'income',
        'label': 'Taxable interest'
    },
    'ordinary_dividends': {
        'labels': ['ordinary dividends'],
        'line_patterns': ['3b'],
        'category': 'income',
        'label': 'Ordinary dividends'
    },
    'capital_gains': {
        'labels': ['capital gain or (loss)'],
        'line_patterns': ['7'],
        'category': 'income',
        'label': 'Capital gain or (loss)'
    },
    'other_income': {
        'labels': ['other income from schedule 1'],
        'line_patterns': ['8'],
        'category': 'income',
        'label': 'Other income'
    },
    'total_income': {
        'labels': ['add lines 1z through 8', 'this is your total income'],
        'line_patterns': ['9'],
        'category': 'income',
        'label': 'Total income',
        'prefer_line': True
    },

    # Adjustments
    'adjustments': {
        'labels': ['total other adjustments', 'adjustments to income from schedule 1'],
        'line_patterns': ['10'],
        'category': 'adjustments',
        'label': 'Adjustments to income'
    },
    'agi': {
        'labels': ['this is your adjusted gross income', 'adjusted gross income'],
        'line_patterns': ['11'],
        'category': 'adjustments',
        'label': 'Adjusted gross income (AGI)',
        'prefer_line': True
    },

    # Deductions
    'standard_deduction': {
        'labels': ['standard deduction or itemized deductions'],
        'line_patterns': ['12'],
        'category': 'deductions',
        'label': 'Standard deduction'
    },
    'qbi_deduction': {
        'labels': ['qualified business income deduction'],
        'line_patterns': ['13'],
        'category': 'deductions',
        'label': 'QBI deduction'
    },
    'total_deductions': {
        'labels': ['add lines 12 and 13'],
        'line_patterns': ['14'],
        'category': 'deductions',
        'label': 'Total deductions'
    },
    'taxable_income': {
        'labels': ['taxable income. subtract line 14', 'this is your taxable income'],
        'line_patterns': ['15'],
        'category': 'deductions',
        'label': 'Taxable income'
    },

    # Tax computation
    'tax_amount': {
        'labels': ['tax (see instructions)'],
        'line_patterns': ['16'],
        'category': 'tax',
        'label': 'Tax'
    },
    'child_tax_credit': {
        'labels': ['child tax credit or credit for other dependents'],
        'line_patterns': ['19'],
        'category': 'tax',
        'label': 'Child tax credit'
    },
    'total_tax': {
        'labels': ['add lines 22 and 23. this is your total tax', 'this is your total tax'],
        'line_patterns': ['24'],
        'category': 'tax',
        'label': 'Total tax',
        'prefer_line': True
    },

    # Payments
    'federal_withholding': {
        'labels': ['federal income tax withheld from'],
        'line_patterns': ['25d'],
        'category': 'payments',
        'label': 'Federal income tax withheld'
    },
    'estimated_payments': {
        'labels': ['estimated tax payments'],
        'line_patterns': ['26'],
        'category': 'payments',
        'label': 'Estimated tax payments'
    },
    'eic': {
        'labels': ['earned income credit'],
        'line_patterns': ['27'],
        'category': 'payments',
        'label': 'Earned income credit (EIC)'
    },
    'total_payments': {
        'labels': ['add lines 25d through 32. these are your total payments', 'these are your total payments'],
        'line_patterns': ['33'],
        'category': 'payments',
        'label': 'Total payments'
    },

    # Refund/Owed
    'refund': {
        'labels': ['if line 33 is more than line 24', 'amount you overpaid'],
        'line_patterns': ['34'],
        'category': 'refund_owed',
        'label': 'Refund'
    },
    'amount_owed': {
        'labels': ['amount you owe. subtract line 33 from line 24'],
        'line_patterns': ['37'],
        'category': 'refund_owed',
        'label': 'Amount owed'
    },
}

# Schedule 1 fields (Adjustments)
SCHEDULE_1_FIELDS = {
    'educator_expenses': {
        'labels': ['educator expenses'],
        'line_patterns': ['11'],
        'category': 'schedule_1',
        'label': 'Educator expenses'
    },
    'hsa_deduction': {
        'labels': ['health savings account deduction'],
        'line_patterns': ['13'],
        'category': 'schedule_1',
        'label': 'HSA deduction'
    },
    'self_employment_tax_deductible': {
        'labels': ['deductible part of self-employment tax'],
        'line_patterns': ['15'],
        'category': 'schedule_1',
        'label': 'SE tax deduction'
    },
    'self_employed_health_insurance': {
        'labels': ['self-employed health insurance deduction'],
        'line_patterns': ['17'],
        'category': 'schedule_1',
        'label': 'SE health insurance'
    },
    'ira_deduction': {
        'labels': ['ira deduction'],
        'line_patterns': ['20'],
        'category': 'schedule_1',
        'label': 'IRA deduction'
    },
    'student_loan_interest': {
        'labels': ['student loan interest deduction'],
        'line_patterns': ['21'],
        'category': 'schedule_1',
        'label': 'Student loan interest'
    },
    'total_adjustments': {
        'labels': ['add lines 11 through 25'],
        'line_patterns': ['26'],
        'category': 'schedule_1',
        'label': 'Total adjustments'
    },
}

# Schedule C fields (Self-employment)
SCHEDULE_C_FIELDS = {
    'gross_receipts': {
        'labels': ['gross receipts or sales'],
        'line_patterns': ['1'],
        'category': 'schedule_c',
        'label': 'Gross receipts'
    },
    'cost_of_goods_sold': {
        'labels': ['cost of goods sold'],
        'line_patterns': ['4'],
        'category': 'schedule_c',
        'label': 'Cost of goods sold'
    },
    'gross_profit': {
        'labels': ['gross profit'],
        'line_patterns': ['5'],
        'category': 'schedule_c',
        'label': 'Gross profit'
    },
    'total_expenses': {
        'labels': ['total expenses before expenses for business use'],
        'line_patterns': ['28'],
        'category': 'schedule_c',
        'label': 'Total expenses'
    },
    'net_profit': {
        'labels': ['net profit or (loss)'],
        'line_patterns': ['31'],
        'category': 'schedule_c',
        'label': 'Net profit/loss'
    },
}

# Schedule 2 fields (Additional Taxes)
# Note: Schedule 2 has two parts:
# Part I: Tax (lines 1-3) - AMT, excess premium tax credit
# Part II: Other Taxes (lines 4-21) - SE tax, Medicare, etc.
SCHEDULE_2_FIELDS = {
    'alternative_minimum_tax': {
        'labels': ['alternative minimum tax', 'amt'],
        'line_patterns': ['1'],
        'category': 'schedule_2',
        'label': 'Alternative minimum tax'
    },
    'self_employment_tax': {
        'labels': ['self-employment tax', 'attach schedule se'],
        'line_patterns': ['4'],
        'category': 'schedule_2',
        'label': 'Self-employment tax',
        'prefer_line': True
    },
    'additional_medicare_tax': {
        'labels': ['additional medicare tax', 'attach form 8959'],
        'line_patterns': ['8'],  # Fixed: was 11, should be 8
        'category': 'schedule_2',
        'label': 'Additional Medicare tax'
    },
    'net_investment_income_tax': {
        'labels': ['net investment income tax', 'attach form 8960'],
        'line_patterns': ['8'],  # NIIT is also reported on line 8 area
        'category': 'schedule_2',
        'label': 'Net investment income tax'
    },
    'total_additional_taxes': {
        'labels': ['add lines 4 and 7 through', 'total other taxes'],
        'line_patterns': ['21'],  # Fixed: total is line 21 in current forms
        'category': 'schedule_2',
        'label': 'Total additional taxes',
        'prefer_line': True
    },
}


# =============================================================================
# OCR Functions
# =============================================================================

def run_ocr(pdf_path: str, max_pages: int = 20) -> List[Dict]:
    """
    Run PaddleOCR on a PDF and return results.

    Args:
        pdf_path: Path to the PDF file
        max_pages: Maximum number of pages to process

    Returns:
        List of OCR result dicts with text, confidence, page, bbox
    """
    import os

    # Check if file exists first
    if not os.path.exists(pdf_path):
        progress(f"ERROR: File does not exist: {pdf_path}")
        progress(f"ERROR: Current working directory: {os.getcwd()}")
        return []

    try:
        from paddleocr import PaddleOCR
        import fitz  # PyMuPDF
    except ImportError as e:
        progress(f"ERROR: Missing dependency: {e}")
        return []

    progress(f"PROGRESS:opening:{pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = min(len(doc), max_pages)

    progress(f"PROGRESS:pages:{total_pages}")

    # Convert PDF pages to images
    temp_dir = tempfile.mkdtemp()
    images = []

    for i in range(total_pages):
        progress(f"PROGRESS:rendering:{i+1}/{total_pages}")
        page = doc[i]
        # 2x zoom for better OCR accuracy
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_path = os.path.join(temp_dir, f"page_{i}.png")
        pix.save(img_path)
        images.append(img_path)
    doc.close()

    # Initialize PaddleOCR (suppress logging)
    progress("PROGRESS:loading_ocr:")
    ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)

    all_results = []
    try:
        for i, img_path in enumerate(images):
            progress(f"PROGRESS:ocr:{i+1}/{total_pages}")
            result = ocr.ocr(img_path, cls=True)

            if result and result[0]:
                for line in result[0]:
                    bbox, (text, confidence) = line
                    all_results.append({
                        'text': text,
                        'confidence': confidence,
                        'page': i + 1,  # 1-indexed pages
                        'bbox': [[int(c) for c in point] for point in bbox]
                    })
    finally:
        shutil.rmtree(temp_dir)

    progress(f"PROGRESS:complete:{len(all_results)} text blocks")
    return all_results


# =============================================================================
# Text Parsing
# =============================================================================

def parse_number(text: str) -> Optional[int]:
    """Parse a number from OCR text, handling common formats."""
    cleaned = text.strip().replace(',', '').replace('$', '').replace(' ', '')
    # Remove trailing decimal and zeros (e.g., "398,490.00" -> "398490")
    cleaned = re.sub(r'\.0*$', '', cleaned)
    # Remove any remaining decimal portion
    cleaned = re.sub(r'\.\d+$', '', cleaned)

    # Handle negative numbers in parentheses
    if cleaned.startswith('(') and cleaned.endswith(')'):
        cleaned = '-' + cleaned[1:-1]

    if re.match(r'^-?\d+$', cleaned):
        return int(cleaned)
    return None


def is_number_text(text: str) -> bool:
    """Check if text looks like a number."""
    cleaned = text.strip().replace(',', '').replace('$', '').replace(' ', '')
    cleaned = re.sub(r'\.0*$', '', cleaned)
    return bool(re.match(r'^-?\d+\.?\d*$', cleaned))


# =============================================================================
# Label Matching Functions
# =============================================================================

def find_rightmost_number_on_line(
    label_result: OCRResult,
    all_results: List[OCRResult],
    min_value: int = 100,
    page_width: int = 1200
) -> Optional[Tuple[int, float, str]]:
    """
    Find the rightmost number on the same line as a label.

    Uses column detection (right 40% of page) to avoid picking up line numbers.
    Returns (value, confidence, raw_text) or None.
    """
    label_y = label_result.center_y

    # Estimate page width from all results on this page
    page_results = [r for r in all_results if r.page == label_result.page]
    if page_results:
        page_width = max(r.right_x for r in page_results)

    # Value column starts at roughly 55% of page width
    value_column_start = page_width * 0.55

    candidates = []

    for result in all_results:
        if result.page != label_result.page:
            continue
        if not is_number_text(result.text):
            continue

        # Must be in the value column (right side of page)
        if result.left_x < value_column_start:
            continue

        # Must be on the same line (within 15 pixels vertically - tighter tolerance)
        y_distance = abs(result.center_y - label_y)
        if y_distance > 15:
            continue

        value = parse_number(result.text)
        if value is not None:
            # Skip small numbers that are likely line numbers (1-99)
            if abs(value) < min_value:
                continue
            candidates.append((value, result.confidence, result.right_x, result.text))

    if not candidates:
        return None

    # Return the rightmost one (furthest right on the page = actual value)
    candidates.sort(key=lambda x: x[2], reverse=True)
    return (candidates[0][0], candidates[0][1], candidates[0][3])


def find_number_after_line_number(
    line_pattern: str,
    all_results: List[OCRResult],
    page: int
) -> Optional[Tuple[int, float, str]]:
    """
    Find a number that appears after a line number pattern.
    E.g., "11" followed by "120,200" on the same line.
    """
    for result in all_results:
        if result.page != page:
            continue

        text = result.text.strip().lower()
        if text == line_pattern or text == line_pattern + '.':
            # Look for the rightmost number on this line
            found = find_rightmost_number_on_line(result, all_results)
            if found:
                return found

    return None


# =============================================================================
# Form Detection
# =============================================================================

def find_form_1040_pages(ocr_results: List[Dict]) -> List[int]:
    """Find pages that contain Form 1040 (the actual form, not cover letters)."""
    form_pages = []

    for result in ocr_results:
        text_lower = result['text'].lower()
        # Look for Form 1040 header indicators
        if 'u.s. individual income tax return' in text_lower:
            if result['page'] not in form_pages:
                form_pages.append(result['page'])
        # Also look for "form 1040" near top of page (y < 300)
        elif 'form 1040' in text_lower or '1040' in result['text']:
            bbox = result.get('bbox', [])
            if bbox:
                avg_y = sum(p[1] for p in bbox) / 4
                if avg_y < 300:  # Near top of page
                    if result['page'] not in form_pages:
                        form_pages.append(result['page'])

    return sorted(form_pages)


def find_schedule_pages(ocr_results: List[Dict]) -> Dict[str, Optional[int]]:
    """Find pages that contain various schedules.

    Looks for schedule headers at the top of pages. Avoids false positives from
    references like "Amount from Schedule 2, line 3" on Form 1040.
    """
    schedules = {
        'schedule_1': None,
        'schedule_2': None,
        'schedule_a': None,
        'schedule_b': None,
        'schedule_c': None,
        'schedule_d': None,
    }

    # Look for schedule headers in individual OCR blocks
    # Schedule headers are typically standalone text like "SCHEDULE 2" or "Schedule 2 (Form 1040)"
    for result in ocr_results:
        bbox = result.get('bbox', [])
        if not bbox:
            continue
        avg_y = sum(p[1] for p in bbox) / 4
        if avg_y > 200:  # Only very top of page (header area)
            continue

        text = result['text']
        text_lower = text.lower()
        page = result['page']

        # Skip references like "from Schedule 2" or "Amount from Schedule"
        if 'from schedule' in text_lower or 'amount from' in text_lower:
            continue

        # Schedule 1: Look for "SCHEDULE 1" or "Schedule 1 (Form 1040)"
        if schedules['schedule_1'] is None:
            if ('schedule 1' in text_lower or 'SCHEDULE 1' in text) and '(form 1040)' in text_lower:
                schedules['schedule_1'] = page
            elif text.strip().upper() == 'SCHEDULE 1':
                schedules['schedule_1'] = page

        # Schedule 2: Look for "SCHEDULE 2" or "Schedule 2 (Form 1040)"
        if schedules['schedule_2'] is None:
            if ('schedule 2' in text_lower or 'SCHEDULE 2' in text) and '(form 1040)' in text_lower:
                schedules['schedule_2'] = page
            elif text.strip().upper() == 'SCHEDULE 2':
                schedules['schedule_2'] = page

        # Schedule A: Look for "SCHEDULE A" or "Schedule A (Form 1040)"
        if schedules['schedule_a'] is None:
            if ('schedule a' in text_lower or 'SCHEDULE A' in text) and '(form 1040)' in text_lower:
                schedules['schedule_a'] = page
            elif text.strip().upper() == 'SCHEDULE A':
                schedules['schedule_a'] = page

        # Schedule B: Look for "SCHEDULE B" or "Schedule B (Form 1040)"
        if schedules['schedule_b'] is None:
            if ('schedule b' in text_lower or 'SCHEDULE B' in text) and '(form 1040)' in text_lower:
                schedules['schedule_b'] = page
            elif text.strip().upper() == 'SCHEDULE B':
                schedules['schedule_b'] = page

        # Schedule C: Look for "SCHEDULE C" or "Schedule C (Form 1040)"
        if schedules['schedule_c'] is None:
            if ('schedule c' in text_lower or 'SCHEDULE C' in text) and '(form 1040)' in text_lower:
                schedules['schedule_c'] = page
            elif text.strip().upper() == 'SCHEDULE C':
                schedules['schedule_c'] = page

        # Schedule D: Look for "SCHEDULE D" or "Schedule D (Form 1040)"
        if schedules['schedule_d'] is None:
            if ('schedule d' in text_lower or 'SCHEDULE D' in text) and '(form 1040)' in text_lower:
                schedules['schedule_d'] = page
            elif text.strip().upper() == 'SCHEDULE D':
                schedules['schedule_d'] = page

    return schedules


def detect_form_year(ocr_results: List[Dict], form_pages: List[int]) -> Optional[int]:
    """Detect the tax year from OCR results."""
    year_pattern = re.compile(r'\b(20\d{2})\b')

    # First check Form 1040 pages
    for result in ocr_results:
        if form_pages and result['page'] not in form_pages:
            continue

        text = result['text']
        matches = year_pattern.findall(text)
        for match in matches:
            year = int(match)
            if 2018 <= year <= 2030:  # Reasonable range
                return year

    return None


def detect_filing_status(ocr_results: List[Dict], form_pages: List[int]) -> str:
    """Detect the filing status from OCR results."""
    # Combine text from Form 1040 pages
    text = ""
    for result in ocr_results:
        if form_pages and result['page'] in form_pages:
            text += " " + result['text'].lower()

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


# =============================================================================
# Field Extraction
# =============================================================================

def extract_fields(
    ocr_results: List[Dict],
    field_defs: Dict[str, Dict],
    target_pages: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """
    Extract fields from OCR results using label matching.

    Args:
        ocr_results: List of OCR result dicts
        field_defs: Dictionary of field definitions
        target_pages: Optional list of pages to search (1-indexed)

    Returns:
        List of extracted field dicts
    """
    # Convert to OCRResult objects
    results = []
    for r in ocr_results:
        if r.get('bbox'):
            results.append(OCRResult(
                text=r['text'],
                confidence=r['confidence'],
                page=r['page'],
                bbox=r['bbox']
            ))

    # Determine which pages to search
    if target_pages:
        pages_to_search = set(target_pages)
    else:
        pages_to_search = set(r.page for r in results)

    fields = []

    for field_key, field_def in field_defs.items():
        found = None
        source = None

        # For fields with prefer_line=True, try line patterns first (more reliable)
        if field_def.get('prefer_line') and 'line_patterns' in field_def:
            for page in pages_to_search:
                for line_pattern in field_def['line_patterns']:
                    found = find_number_after_line_number(line_pattern, results, page)
                    if found:
                        source = f"line: {line_pattern}"
                        break
                if found:
                    break

        # Strategy 1: Look for label text, find rightmost number on same line
        if not found:
            for result in results:
                if result.page not in pages_to_search:
                    continue

                text_lower = result.text.lower()

                for label in field_def.get('labels', []):
                    if label in text_lower:
                        # Found the label, look for the rightmost number on this line
                        found = find_rightmost_number_on_line(result, results)
                        if found:
                            source = f"label: '{label}'"
                            break
                if found:
                    break

        # Strategy 2: If not found by label, try line number patterns
        if not found and 'line_patterns' in field_def:
            for page in pages_to_search:
                for line_pattern in field_def['line_patterns']:
                    found = find_number_after_line_number(line_pattern, results, page)
                    if found:
                        source = f"line: {line_pattern}"
                        break
                if found:
                    break

        # Create field entry
        if found:
            value, confidence, raw_text = found
            fields.append({
                'key': field_key,
                'label': field_def.get('label', field_key),
                'value': str(value),
                'raw_text': raw_text,
                'category': field_def.get('category', 'other'),
                'line_number': field_def.get('line_patterns', [''])[0] if field_def.get('line_patterns') else '',
                'confidence': confidence,
                'source': source,
            })
        else:
            # Field not found - still add it with null value for completeness
            fields.append({
                'key': field_key,
                'label': field_def.get('label', field_key),
                'value': None,
                'raw_text': None,
                'category': field_def.get('category', 'other'),
                'line_number': field_def.get('line_patterns', [''])[0] if field_def.get('line_patterns') else '',
                'confidence': 0.0,
                'source': None,
            })

    return fields


# =============================================================================
# Main Extraction
# =============================================================================

def extract_form_1040(pdf_path: str) -> Dict[str, Any]:
    """
    Extract all fields from a Form 1040 PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with year, filing_status, extraction_method, fields, etc.
    """
    try:
        # Run OCR
        ocr_results = run_ocr(pdf_path)

        if not ocr_results:
            return {
                "error": "OCR produced no results",
                "year": 0,
                "filing_status": "Unknown",
                "extraction_method": "paddleocr",
                "fields": []
            }

        # Find Form 1040 pages
        form_pages = find_form_1040_pages(ocr_results)
        progress(f"PROGRESS:detected_form_pages:{form_pages}")

        if not form_pages:
            # Fall back to first 2 pages if no Form 1040 detected
            form_pages = [1, 2]

        # Detect year and filing status
        year = detect_form_year(ocr_results, form_pages)
        if year is None:
            # Try to get year from filename
            year_match = re.search(r'20\d{2}', pdf_path)
            year = int(year_match.group()) if year_match else 0

        filing_status = detect_filing_status(ocr_results, form_pages)

        # Check year is supported (2020+)
        if year and year < 2020:
            return {
                "error": f"Tax returns from {year} are not supported. This app currently supports tax years 2020 and later.",
                "year": year,
                "filing_status": filing_status,
                "extraction_method": "paddleocr",
                "fields": [],
                "unsupported_year": True
            }

        # Extract Form 1040 fields
        progress("PROGRESS:extracting:Form 1040")
        fields = extract_fields(ocr_results, FORM_1040_FIELDS, form_pages)

        # Detect and extract schedule fields
        detected_forms = ["Form 1040"]
        schedules = find_schedule_pages(ocr_results)

        if schedules.get('schedule_1'):
            detected_forms.append("Schedule 1")
            progress("PROGRESS:extracting:Schedule 1")
            schedule_fields = extract_fields(
                ocr_results,
                SCHEDULE_1_FIELDS,
                [schedules['schedule_1']]
            )
            fields.extend(schedule_fields)

        if schedules.get('schedule_2'):
            detected_forms.append("Schedule 2")
            progress(f"PROGRESS:extracting:Schedule 2 (page {schedules['schedule_2']})")
            schedule_fields = extract_fields(
                ocr_results,
                SCHEDULE_2_FIELDS,
                [schedules['schedule_2']]
            )
            # Log what was found
            found_count = sum(1 for f in schedule_fields if f.get('value') is not None)
            progress(f"PROGRESS:schedule_2_fields:{found_count}/{len(schedule_fields)} fields found")
            fields.extend(schedule_fields)

        if schedules.get('schedule_c'):
            detected_forms.append("Schedule C")
            progress("PROGRESS:extracting:Schedule C")
            schedule_fields = extract_fields(
                ocr_results,
                SCHEDULE_C_FIELDS,
                [schedules['schedule_c']]
            )
            fields.extend(schedule_fields)

        # Calculate page count from OCR results
        page_count = max(r['page'] for r in ocr_results) if ocr_results else 0

        return {
            "year": year,
            "filing_status": filing_status,
            "extraction_method": "paddleocr",
            "fields": fields,
            "page_count": page_count,
            "detected_forms": detected_forms,
            "form_1040_page": form_pages[0] if form_pages else 1,
        }

    except FileNotFoundError:
        return {
            "error": f"File not found: {pdf_path}",
            "year": 0,
            "filing_status": "Unknown",
            "extraction_method": "paddleocr",
            "fields": []
        }
    except Exception as e:
        progress(f"ERROR: {e}")
        return {
            "error": str(e),
            "year": 0,
            "filing_status": "Unknown",
            "extraction_method": "paddleocr",
            "fields": []
        }


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Extract Form 1040 data from PDF files using PaddleOCR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract.py /path/to/tax_return_2024.pdf
    python extract.py --pretty /path/to/1040.pdf

Output is JSON printed to stdout.
Progress messages are printed to stderr.
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
        "--debug",
        action="store_true",
        help="Include raw text and source in output for debugging"
    )

    args = parser.parse_args()

    # Require pdf_path
    if not args.pdf_path:
        parser.print_help()
        sys.exit(1)

    # Extract data
    result = extract_form_1040(args.pdf_path)

    # Remove debug fields unless debugging
    if not args.debug:
        for field in result.get("fields", []):
            field.pop("raw_text", None)
            field.pop("source", None)

    # Output JSON
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
