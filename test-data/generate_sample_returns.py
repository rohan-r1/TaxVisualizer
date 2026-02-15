#!/usr/bin/env python3
"""
Generate sample filled Form 1040 PDFs by overlaying text onto IRS blank templates.

This generator:
1. Uses the actual IRS blank Form 1040 templates
2. Overlays text at the exact coordinates from our extraction mappings
3. Produces PDFs that the extraction pipeline can read correctly

Supports:
- Multi-year persona sequences (e.g., 2018-2024)
- Correct tax bracket calculations per year
- Year-over-year continuity (realistic career progression)
- JSON sidecar files for validation

Usage:
    python generate_sample_returns.py                    # Generate all personas
    python generate_sample_returns.py --persona alex_chen  # Generate specific persona
    python generate_sample_returns.py --year 2022        # Generate single year
"""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import json
import sys

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


# =============================================================================
# Output Directories
# =============================================================================

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "generated"
TEMPLATES_DIR = BASE_DIR / "blank-templates"

# Add mappings directory to path
MAPPINGS_DIR = BASE_DIR.parent / "app" / "src-tauri" / "python" / "mappings"
sys.path.insert(0, str(MAPPINGS_DIR.parent))


# =============================================================================
# Tax Data: Brackets, Standard Deductions, Credits (2018-2024)
# =============================================================================

# Federal tax brackets by year and filing status
# Format: [(upper_limit, rate), ...] - upper_limit is the max income for that bracket
TAX_BRACKETS = {
    2018: {
        "Single": [(9525, 0.10), (38700, 0.12), (82500, 0.22), (157500, 0.24), (200000, 0.32), (500000, 0.35), (float('inf'), 0.37)],
        "Married Filing Jointly": [(19050, 0.10), (77400, 0.12), (165000, 0.22), (315000, 0.24), (400000, 0.32), (600000, 0.35), (float('inf'), 0.37)],
        "Head of Household": [(13600, 0.10), (51800, 0.12), (82500, 0.22), (157500, 0.24), (200000, 0.32), (500000, 0.35), (float('inf'), 0.37)],
    },
    2019: {
        "Single": [(9700, 0.10), (39475, 0.12), (84200, 0.22), (160725, 0.24), (204100, 0.32), (510300, 0.35), (float('inf'), 0.37)],
        "Married Filing Jointly": [(19400, 0.10), (78950, 0.12), (168400, 0.22), (321450, 0.24), (408200, 0.32), (612350, 0.35), (float('inf'), 0.37)],
        "Head of Household": [(13850, 0.10), (52850, 0.12), (84200, 0.22), (160700, 0.24), (204100, 0.32), (510300, 0.35), (float('inf'), 0.37)],
    },
    2020: {
        "Single": [(9875, 0.10), (40125, 0.12), (85525, 0.22), (163300, 0.24), (207350, 0.32), (518400, 0.35), (float('inf'), 0.37)],
        "Married Filing Jointly": [(19750, 0.10), (80250, 0.12), (171050, 0.22), (326600, 0.24), (414700, 0.32), (622050, 0.35), (float('inf'), 0.37)],
        "Head of Household": [(14100, 0.10), (53700, 0.12), (85500, 0.22), (163300, 0.24), (207350, 0.32), (518400, 0.35), (float('inf'), 0.37)],
    },
    2021: {
        "Single": [(9950, 0.10), (40525, 0.12), (86375, 0.22), (164925, 0.24), (209425, 0.32), (523600, 0.35), (float('inf'), 0.37)],
        "Married Filing Jointly": [(19900, 0.10), (81050, 0.12), (172750, 0.22), (329850, 0.24), (418850, 0.32), (628300, 0.35), (float('inf'), 0.37)],
        "Head of Household": [(14200, 0.10), (54200, 0.12), (86350, 0.22), (164900, 0.24), (209400, 0.32), (523600, 0.35), (float('inf'), 0.37)],
    },
    2022: {
        "Single": [(10275, 0.10), (41775, 0.12), (89075, 0.22), (170050, 0.24), (215950, 0.32), (539900, 0.35), (float('inf'), 0.37)],
        "Married Filing Jointly": [(20550, 0.10), (83550, 0.12), (178150, 0.22), (340100, 0.24), (431900, 0.32), (647850, 0.35), (float('inf'), 0.37)],
        "Head of Household": [(14650, 0.10), (55900, 0.12), (89050, 0.22), (170050, 0.24), (215950, 0.32), (539900, 0.35), (float('inf'), 0.37)],
    },
    2023: {
        "Single": [(11000, 0.10), (44725, 0.12), (95375, 0.22), (182100, 0.24), (231250, 0.32), (578125, 0.35), (float('inf'), 0.37)],
        "Married Filing Jointly": [(22000, 0.10), (89450, 0.12), (190750, 0.22), (364200, 0.24), (462500, 0.32), (693750, 0.35), (float('inf'), 0.37)],
        "Head of Household": [(15700, 0.10), (59850, 0.12), (95350, 0.22), (182100, 0.24), (231250, 0.32), (578100, 0.35), (float('inf'), 0.37)],
    },
    2024: {
        "Single": [(11600, 0.10), (47150, 0.12), (100525, 0.22), (191950, 0.24), (243725, 0.32), (609350, 0.35), (float('inf'), 0.37)],
        "Married Filing Jointly": [(23200, 0.10), (94300, 0.12), (201050, 0.22), (383900, 0.24), (487450, 0.32), (731200, 0.35), (float('inf'), 0.37)],
        "Head of Household": [(16550, 0.10), (63100, 0.12), (100500, 0.22), (191950, 0.24), (243700, 0.32), (609350, 0.35), (float('inf'), 0.37)],
    },
}

# Standard deductions by year and filing status
STANDARD_DEDUCTIONS = {
    2018: {"Single": 12000, "Married Filing Jointly": 24000, "Head of Household": 18000},
    2019: {"Single": 12200, "Married Filing Jointly": 24400, "Head of Household": 18350},
    2020: {"Single": 12400, "Married Filing Jointly": 24800, "Head of Household": 18650},
    2021: {"Single": 12550, "Married Filing Jointly": 25100, "Head of Household": 18800},
    2022: {"Single": 12950, "Married Filing Jointly": 25900, "Head of Household": 19400},
    2023: {"Single": 13850, "Married Filing Jointly": 27700, "Head of Household": 20800},
    2024: {"Single": 14600, "Married Filing Jointly": 29200, "Head of Household": 21900},
}

# Child tax credit by year
CHILD_TAX_CREDIT = {
    2018: 2000,
    2019: 2000,
    2020: 2000,
    2021: 3000,  # Expanded for 2021
    2022: 2000,
    2023: 2000,
    2024: 2000,
}


# =============================================================================
# Tax Calculator
# =============================================================================

@dataclass
class TaxInput:
    """Input data for tax calculation."""
    wages: int = 0
    interest: int = 0
    dividends: int = 0
    qualified_dividends: int = 0
    capital_gains: int = 0
    other_income: int = 0
    adjustments: int = 0
    itemized_deductions: int = 0
    withholding: int = 0
    estimated_payments: int = 0
    children: int = 0
    filing_status: str = "Single"


@dataclass
class TaxResult:
    """Result of tax calculation with all intermediate values."""
    wages: int = 0
    interest: int = 0
    dividends: int = 0
    qualified_dividends: int = 0
    capital_gains: int = 0
    other_income: int = 0
    total_income: int = 0
    adjustments: int = 0
    agi: int = 0
    deduction_type: str = "standard"
    deduction_amount: int = 0
    taxable_income: int = 0
    tax_on_ordinary_income: int = 0
    total_tax_before_credits: int = 0
    child_tax_credit: int = 0
    other_credits: int = 0
    total_tax: int = 0
    withholding: int = 0
    estimated_payments: int = 0
    total_payments: int = 0
    refund: int = 0
    amount_owed: int = 0
    filing_status: str = "Single"
    year: int = 2024


class TaxCalculator:
    """Calculate federal income tax with correct bracket math."""

    def __init__(self, year: int):
        self.year = year
        if year not in TAX_BRACKETS:
            raise ValueError(f"Year {year} not supported. Available: {list(TAX_BRACKETS.keys())}")

    def calculate(self, input_data: TaxInput) -> TaxResult:
        """Calculate complete tax liability from input data."""
        result = TaxResult(year=self.year, filing_status=input_data.filing_status)

        # 1. Total income
        result.wages = input_data.wages
        result.interest = input_data.interest
        result.dividends = input_data.dividends
        result.qualified_dividends = input_data.qualified_dividends
        result.capital_gains = input_data.capital_gains
        result.other_income = input_data.other_income
        result.total_income = (
            input_data.wages + input_data.interest + input_data.dividends +
            input_data.capital_gains + input_data.other_income
        )

        # 2. AGI
        result.adjustments = input_data.adjustments
        result.agi = result.total_income - input_data.adjustments

        # 3. Deductions
        standard = STANDARD_DEDUCTIONS[self.year][input_data.filing_status]
        if input_data.itemized_deductions > standard:
            result.deduction_type = "itemized"
            result.deduction_amount = input_data.itemized_deductions
        else:
            result.deduction_type = "standard"
            result.deduction_amount = standard

        # 4. Taxable income
        result.taxable_income = max(0, result.agi - result.deduction_amount)

        # 5. Tax calculation
        result.tax_on_ordinary_income = self._calculate_bracket_tax(
            result.taxable_income,
            input_data.filing_status
        )
        result.total_tax_before_credits = result.tax_on_ordinary_income

        # 6. Credits
        if input_data.children > 0:
            result.child_tax_credit = min(
                input_data.children * CHILD_TAX_CREDIT[self.year],
                result.total_tax_before_credits
            )

        # 7. Final tax
        result.total_tax = max(0, result.total_tax_before_credits - result.child_tax_credit - result.other_credits)

        # 8. Payments and result
        result.withholding = input_data.withholding
        result.estimated_payments = input_data.estimated_payments
        result.total_payments = input_data.withholding + input_data.estimated_payments

        if result.total_payments >= result.total_tax:
            result.refund = result.total_payments - result.total_tax
            result.amount_owed = 0
        else:
            result.refund = 0
            result.amount_owed = result.total_tax - result.total_payments

        return result

    def _calculate_bracket_tax(self, taxable_income: int, filing_status: str) -> int:
        """Calculate tax using progressive brackets."""
        brackets = TAX_BRACKETS[self.year][filing_status]
        tax = 0
        prev_limit = 0

        for limit, rate in brackets:
            if taxable_income <= prev_limit:
                break
            bracket_income = min(taxable_income, limit) - prev_limit
            tax += int(bracket_income * rate)
            prev_limit = limit

        return tax


# =============================================================================
# Field Mappings for Each Year
# =============================================================================

def get_field_mapping(year: int) -> dict:
    """Load field mappings for a specific year from the mappings module."""
    try:
        if year == 2018:
            from mappings.form_1040_2018 import FIELDS
        elif year == 2019:
            from mappings.form_1040_2019 import FIELDS
        elif year == 2020:
            from mappings.form_1040_2020 import FIELDS
        elif year == 2021:
            from mappings.form_1040_2021 import FIELDS
        elif year == 2022:
            from mappings.form_1040_2022 import FIELDS
        elif year == 2023:
            from mappings.form_1040_2023 import FIELDS
        elif year == 2024:
            from mappings.form_1040_2024 import FIELDS
        else:
            # Fall back to closest year
            from mappings.form_1040_2022 import FIELDS
        return FIELDS
    except ImportError as e:
        print(f"Warning: Could not load mappings for {year}: {e}")
        return {}


# =============================================================================
# Persona Generator
# =============================================================================

@dataclass
class YearlyData:
    """Data for one year of a persona."""
    wages: int
    interest: int = 0
    dividends: int = 0
    qualified_dividends: int = 0
    capital_gains: int = 0
    other_income: int = 0
    adjustments: int = 0
    itemized_deductions: int = 0
    withholding: int = 0
    estimated_payments: int = 0
    filing_status: str = "Single"
    children: int = 0
    first_name: str = ""
    last_name: str = ""
    spouse_first_name: str = ""
    spouse_last_name: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""


# =============================================================================
# Alex Chen Persona: Software Engineer Career Progression (2018-2024)
# =============================================================================

ALEX_CHEN_PERSONA: Dict[int, YearlyData] = {
    2018: YearlyData(
        wages=65000, interest=50, withholding=9750, filing_status="Single",
        first_name="Alex", last_name="Chen",
        address="456 Startup Lane, Apt 12", city="San Francisco", state="CA", zip_code="94107",
    ),
    2019: YearlyData(
        wages=72000, interest=120, dividends=80, withholding=10800, filing_status="Single",
        first_name="Alex", last_name="Chen",
        address="456 Startup Lane, Apt 12", city="San Francisco", state="CA", zip_code="94107",
    ),
    2020: YearlyData(
        wages=75000, interest=200, dividends=150, withholding=11200, filing_status="Single",
        first_name="Alex", last_name="Chen",
        address="789 Remote Work Dr", city="Austin", state="TX", zip_code="78701",
    ),
    2021: YearlyData(
        wages=95000, interest=350, dividends=200, capital_gains=1500, withholding=12000, filing_status="Single",
        first_name="Alex", last_name="Chen",
        address="789 Remote Work Dr", city="Austin", state="TX", zip_code="78701",
    ),
    2022: YearlyData(
        wages=105000, interest=500, dividends=400, qualified_dividends=300, capital_gains=2500,
        withholding=16000, filing_status="Married Filing Jointly",
        first_name="Alex", last_name="Chen", spouse_first_name="Jordan", spouse_last_name="Chen",
        address="123 Married Life Blvd", city="Austin", state="TX", zip_code="78704",
    ),
    2023: YearlyData(
        wages=120000, interest=800, dividends=600, qualified_dividends=450, capital_gains=3200,
        withholding=19000, filing_status="Married Filing Jointly",
        first_name="Alex", last_name="Chen", spouse_first_name="Jordan", spouse_last_name="Chen",
        address="123 Married Life Blvd", city="Austin", state="TX", zip_code="78704",
    ),
    2024: YearlyData(
        wages=130000, interest=1000, dividends=800, qualified_dividends=600, capital_gains=4000,
        withholding=21000, filing_status="Married Filing Jointly", children=1,
        first_name="Alex", last_name="Chen", spouse_first_name="Jordan", spouse_last_name="Chen",
        address="456 Family Home Ct", city="Austin", state="TX", zip_code="78745",
    ),
}


# =============================================================================
# Maria Garcia Persona: Healthcare Professional (2018-2024)
# =============================================================================

MARIA_GARCIA_PERSONA: Dict[int, YearlyData] = {
    2018: YearlyData(
        # Age 35, nurse practitioner, married with 2 kids
        wages=82000, interest=180, dividends=250, withholding=11500,
        filing_status="Married Filing Jointly", children=2,
        first_name="Maria", last_name="Garcia", spouse_first_name="Carlos", spouse_last_name="Garcia",
        address="234 Oak Street", city="Chicago", state="IL", zip_code="60614",
    ),
    2019: YearlyData(
        # Promotion to senior NP
        wages=92000, interest=220, dividends=350, capital_gains=800, withholding=13000,
        filing_status="Married Filing Jointly", children=2,
        first_name="Maria", last_name="Garcia", spouse_first_name="Carlos", spouse_last_name="Garcia",
        address="234 Oak Street", city="Chicago", state="IL", zip_code="60614",
    ),
    2020: YearlyData(
        # COVID year - overtime pay, hazard bonuses
        wages=115000, interest=300, dividends=400, withholding=18000,
        filing_status="Married Filing Jointly", children=2,
        first_name="Maria", last_name="Garcia", spouse_first_name="Carlos", spouse_last_name="Garcia",
        address="234 Oak Street", city="Chicago", state="IL", zip_code="60614",
    ),
    2021: YearlyData(
        # Divorce finalized, now Head of Household with kids
        wages=105000, interest=250, dividends=300, withholding=16500,
        filing_status="Head of Household", children=2,
        first_name="Maria", last_name="Garcia",
        address="567 New Beginning Ave", city="Chicago", state="IL", zip_code="60657",
    ),
    2022: YearlyData(
        # Stable, rebuilding savings
        wages=110000, interest=400, dividends=500, capital_gains=1200, withholding=17000,
        filing_status="Head of Household", children=2,
        first_name="Maria", last_name="Garcia",
        address="567 New Beginning Ave", city="Chicago", state="IL", zip_code="60657",
    ),
    2023: YearlyData(
        # Director of nursing role
        wages=125000, interest=600, dividends=700, capital_gains=2000, withholding=20000,
        filing_status="Head of Household", children=2,
        first_name="Maria", last_name="Garcia",
        address="567 New Beginning Ave", city="Chicago", state="IL", zip_code="60657",
    ),
    2024: YearlyData(
        # Kids now 1 dependent (one turned 18)
        wages=135000, interest=800, dividends=900, capital_gains=2500, withholding=22000,
        filing_status="Head of Household", children=1,
        first_name="Maria", last_name="Garcia",
        address="567 New Beginning Ave", city="Chicago", state="IL", zip_code="60657",
    ),
}


# =============================================================================
# PDF Generation with Template Overlay
# =============================================================================

PAGE_HEIGHT = 792  # Standard letter page height in points

# Templates with coversheets - we skip the coversheet when generating
# so the output matches the structure expected by extraction mappings
TEMPLATE_COVERSHEET_PAGES = {
    2018: 1,  # Skip first 1 page (coversheet)
    2019: 1,  # Skip first 1 page (coversheet)
    # 2020-2024 have no coversheet to skip
}

# Override field positions for templates where mappings don't match
# Format: {year: {field_name: {"page": int, "bbox": (x0, y0, x1, y1)}}}
# These are calibrated against the actual IRS blank templates
TEMPLATE_FIELD_OVERRIDES = {
    2018: {
        # 2018 Form 1040 - "postcard" format, different layout
        # After coversheet removal, form is on page 0 of output
        # Value boxes: left edge ~461, cents divider at 554, so dollars right-align at 552
        "wages":              {"page": 0, "bbox": (461, 41, 552, 51)},
        "taxable_interest":   {"page": 0, "bbox": (461, 53, 552, 63)},
        "ordinary_dividends": {"page": 0, "bbox": (461, 65, 552, 75)},
        "total_income":       {"page": 0, "bbox": (461, 101, 552, 111)},
        "agi":                {"page": 0, "bbox": (461, 119, 552, 129)},
        "deductions":         {"page": 0, "bbox": (461, 131, 552, 141)},
        "taxable_income":     {"page": 0, "bbox": (461, 155, 552, 165)},
        "tax_amount":         {"page": 0, "bbox": (170, 167, 230, 177)},  # Left column for 11a
        "total_tax":          {"page": 0, "bbox": (461, 227, 552, 237)},
        "federal_withholding": {"page": 0, "bbox": (461, 239, 552, 249)},
        "total_payments":     {"page": 0, "bbox": (461, 275, 552, 285)},
        "overpaid":           {"page": 0, "bbox": (461, 287, 552, 297)},
        "refund":             {"page": 0, "bbox": (461, 299, 552, 309)},
        "amount_owed":        {"page": 0, "bbox": (461, 347, 552, 357)},
    },
    2019: {
        # 2019 Form 1040 - 2 pages after coversheet (income on page 0, tax on page 1)
        # Calibrated against IRS blank template f1040--2019.pdf
        # Page 0 (income) - lines 1-11 (shifted up 12pts from previous - was 1 row too low)
        "wages":              {"page": 0, "bbox": (504, 339, 552, 349)},  # Line 1
        "taxable_interest":   {"page": 0, "bbox": (504, 351, 552, 361)},  # Line 2b
        "ordinary_dividends": {"page": 0, "bbox": (504, 363, 552, 373)},  # Line 3b
        "capital_gains":      {"page": 0, "bbox": (504, 399, 552, 409)},  # Line 6
        "total_income":       {"page": 0, "bbox": (504, 411, 552, 421)},  # Line 7b
        "agi":                {"page": 0, "bbox": (504, 435, 552, 445)},  # Line 7b
        "deductions":         {"page": 0, "bbox": (504, 459, 552, 469)},  # Line 8b
        "taxable_income":     {"page": 0, "bbox": (504, 507, 552, 517)},  # Line 11b
        # Page 1 (tax) - lines 12+ (these were correct)
        "tax_amount":         {"page": 1, "bbox": (504, 63, 552, 73)},    # Line 12b
        "total_tax":          {"page": 1, "bbox": (504, 111, 552, 121)},  # Line 15
        "federal_withholding": {"page": 1, "bbox": (504, 123, 552, 133)}, # Line 16
        "total_payments":     {"page": 1, "bbox": (504, 207, 552, 217)},  # Line 18e
        "overpaid":           {"page": 1, "bbox": (504, 219, 552, 229)},  # Line 19
        "refund":             {"page": 1, "bbox": (504, 231, 552, 241)},  # Line 20
        "amount_owed":        {"page": 1, "bbox": (504, 291, 552, 301)},  # Line 23
    },
    2021: {
        # 2021 Form 1040 - calibrated against IRS blank template f1040--2021.pdf
        # Page 0: Income (lines 1-15), Page 1: Tax/payments/refund (lines 16-37)
        # Value column: x=504-576, cents divider ~554, so right-align at 552
        # Page 0 - Income
        "wages":              {"page": 0, "bbox": (504, 357, 552, 367)},
        "taxable_interest":   {"page": 0, "bbox": (504, 369, 552, 379)},
        "ordinary_dividends": {"page": 0, "bbox": (504, 381, 552, 391)},
        "capital_gains":      {"page": 0, "bbox": (504, 429, 552, 439)},
        "other_income":       {"page": 0, "bbox": (504, 441, 552, 451)},
        "total_income":       {"page": 0, "bbox": (504, 453, 552, 463)},
        "adjustments":        {"page": 0, "bbox": (504, 465, 552, 475)},
        "agi":                {"page": 0, "bbox": (504, 477, 552, 487)},
        "deductions":         {"page": 0, "bbox": (504, 489, 552, 499)},
        "taxable_income":     {"page": 0, "bbox": (504, 549, 552, 559)},
        # Page 1 - Tax and payments
        "tax_amount":         {"page": 1, "bbox": (504, 39, 552, 49)},
        "child_tax_credit":   {"page": 1, "bbox": (504, 75, 552, 85)},
        "total_tax":          {"page": 1, "bbox": (504, 135, 552, 145)},
        "federal_withholding": {"page": 1, "bbox": (504, 195, 552, 205)},
        "total_payments":     {"page": 1, "bbox": (504, 345, 552, 355)},
        "overpaid":           {"page": 1, "bbox": (504, 357, 552, 367)},
        "refund":             {"page": 1, "bbox": (504, 369, 552, 379)},
        "amount_owed":        {"page": 1, "bbox": (504, 417, 552, 427)},
    },
}


def create_overlay_pdf(year: int, tax_result: TaxResult, num_pages: int = 2) -> BytesIO:
    """Create a PDF with text overlaid at correct positions for extraction."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Get field mappings for this year
    fields = get_field_mapping(year)
    if not fields:
        print(f"  Warning: No field mappings for {year}, using default positions")
        return buffer

    # Apply template-specific overrides if available
    overrides = TEMPLATE_FIELD_OVERRIDES.get(year, {})
    if overrides:
        # Merge overrides into fields (overrides take precedence)
        for field_name, override_info in overrides.items():
            if field_name in fields:
                fields[field_name] = {**fields[field_name], **override_info}
            else:
                fields[field_name] = override_info

    # Build value lookup from tax result
    values = {
        "wages": tax_result.wages if tax_result.wages else None,
        "taxable_interest": tax_result.interest if tax_result.interest else None,
        "ordinary_dividends": tax_result.dividends if tax_result.dividends else None,
        "capital_gains": tax_result.capital_gains if tax_result.capital_gains else None,
        "other_income": tax_result.other_income if tax_result.other_income else None,
        "total_income": tax_result.total_income,
        "adjustments": tax_result.adjustments if tax_result.adjustments else None,
        "agi": tax_result.agi,
        "deductions": tax_result.deduction_amount,
        "taxable_income": tax_result.taxable_income,
        "tax_amount": tax_result.tax_on_ordinary_income,
        "child_tax_credit": tax_result.child_tax_credit if tax_result.child_tax_credit else None,
        "total_tax": tax_result.total_tax,
        "federal_withholding": tax_result.withholding,
        "estimated_payments": tax_result.estimated_payments if tax_result.estimated_payments else None,
        "total_payments": tax_result.total_payments,
        "refund": tax_result.refund if tax_result.refund else None,
        "amount_owed": tax_result.amount_owed if tax_result.amount_owed else None,
        "overpaid": tax_result.refund if tax_result.refund else None,
    }

    # Group fields by page (no offset needed - we skip coversheets in the merge step)
    pages = {}
    for field_name, field_info in fields.items():
        page = field_info.get("page", 0)
        if page not in pages:
            pages[page] = []
        pages[page].append((field_name, field_info))

    # Draw each page
    for page_num in range(num_pages):
        if page_num > 0:
            c.showPage()

        c.setFont("Helvetica", 9)

        if page_num in pages:
            for field_name, field_info in pages[page_num]:
                value = values.get(field_name)
                if value is None:
                    continue

                bbox = field_info.get("bbox")
                if not bbox:
                    continue

                x0, y0, x1, y1 = bbox

                # Convert from PDF coordinates (origin top-left) to reportlab (origin bottom-left)
                # y_reportlab = PAGE_HEIGHT - y_pdf
                # We want to draw at the vertical center of the bbox
                y_center_pdf = (y0 + y1) / 2
                y_reportlab = PAGE_HEIGHT - y_center_pdf

                # Draw right-aligned at x1 (right edge of bbox)
                text = f"{value:,}" if isinstance(value, int) else str(value)
                c.drawRightString(x1, y_reportlab, text)

    c.save()
    buffer.seek(0)
    return buffer


def generate_filled_pdf(year: int, tax_result: TaxResult, output_path: Path):
    """Generate a filled 1040 by overlaying values onto the blank template."""
    # Find the template
    template_path = TEMPLATES_DIR / f"f1040--{year}.pdf"
    if not template_path.exists():
        template_path = TEMPLATES_DIR / "f1040.pdf"  # Fallback
        if not template_path.exists():
            print(f"  Error: No template found for {year}")
            return False

    try:
        # Load template
        template_pdf = PdfReader(str(template_path))

        # Skip coversheet pages if present (so output matches extraction mappings)
        skip_pages = TEMPLATE_COVERSHEET_PAGES.get(year, 0)
        template_pages = list(template_pdf.pages)[skip_pages:]
        num_pages = len(template_pages)

        # Create overlay with values (matches the non-coversheet pages)
        overlay_buffer = create_overlay_pdf(year, tax_result, num_pages)
        overlay_pdf = PdfReader(overlay_buffer)

        # Merge overlay onto template (excluding coversheet)
        writer = PdfWriter()
        for i, page in enumerate(template_pages):
            if i < len(overlay_pdf.pages):
                page.merge_page(overlay_pdf.pages[i])
            writer.add_page(page)

        # Write output
        with open(output_path, "wb") as f:
            writer.write(f)

        return True

    except Exception as e:
        print(f"  Error generating PDF for {year}: {e}")
        return False


def generate_json_sidecar(year: int, tax_result: TaxResult, yearly_data: YearlyData, output_path: Path):
    """Generate JSON sidecar with expected values for extraction validation."""
    json_data = {
        "pdf_file": output_path.name,
        "tax_year": year,
        "filing_status": tax_result.filing_status,
        "fields": {
            "wages": {"expected": str(tax_result.wages) if tax_result.wages else None, "tolerance": 0, "allow_null": tax_result.wages == 0},
            "taxable_interest": {"expected": str(tax_result.interest) if tax_result.interest else None, "tolerance": 0, "allow_null": True},
            "ordinary_dividends": {"expected": str(tax_result.dividends) if tax_result.dividends else None, "tolerance": 0, "allow_null": True},
            "capital_gains": {"expected": str(tax_result.capital_gains) if tax_result.capital_gains else None, "tolerance": 0, "allow_null": True},
            "total_income": {"expected": str(tax_result.total_income), "tolerance": 0},
            "adjustments": {"expected": str(tax_result.adjustments) if tax_result.adjustments else None, "tolerance": 0, "allow_null": True},
            "agi": {"expected": str(tax_result.agi), "tolerance": 0},
            "deductions": {"expected": str(tax_result.deduction_amount), "tolerance": 0},
            "taxable_income": {"expected": str(tax_result.taxable_income), "tolerance": 0},
            "tax_amount": {"expected": str(tax_result.tax_on_ordinary_income), "tolerance": 0},
            "child_tax_credit": {"expected": str(tax_result.child_tax_credit) if tax_result.child_tax_credit else None, "tolerance": 0, "allow_null": True},
            "total_tax": {"expected": str(tax_result.total_tax), "tolerance": 0},
            "federal_withholding": {"expected": str(tax_result.withholding), "tolerance": 0},
            "estimated_payments": {"expected": str(tax_result.estimated_payments) if tax_result.estimated_payments else None, "tolerance": 0, "allow_null": True},
            "total_payments": {"expected": str(tax_result.total_payments), "tolerance": 0},
            "refund": {"expected": str(tax_result.refund) if tax_result.refund else None, "tolerance": 0, "allow_null": True},
            "amount_owed": {"expected": str(tax_result.amount_owed) if tax_result.amount_owed else None, "tolerance": 0, "allow_null": True},
        },
        "metadata": {
            "persona": f"{yearly_data.first_name} {yearly_data.last_name}",
            "scenario": f"Year {year} - {tax_result.filing_status}",
            "auto_generated": True,
        },
    }

    with open(output_path.with_suffix('.json'), 'w') as f:
        json.dump(json_data, f, indent=2)


def generate_persona(persona_name: str, persona_data: Dict[int, YearlyData], years: List[int] = None):
    """Generate all years for a persona."""
    output_dir = OUTPUT_DIR / persona_name
    output_dir.mkdir(parents=True, exist_ok=True)

    if years is None:
        years = sorted(persona_data.keys())

    print(f"\nGenerating persona: {persona_name}")
    print(f"Years: {years}")
    print("-" * 50)

    for year in years:
        if year not in persona_data:
            print(f"  Skipping {year}: no data")
            continue

        yearly = persona_data[year]

        # Calculate tax
        calc = TaxCalculator(year)
        tax_input = TaxInput(
            wages=yearly.wages,
            interest=yearly.interest,
            dividends=yearly.dividends,
            qualified_dividends=yearly.qualified_dividends,
            capital_gains=yearly.capital_gains,
            other_income=yearly.other_income,
            adjustments=yearly.adjustments,
            itemized_deductions=yearly.itemized_deductions,
            withholding=yearly.withholding,
            estimated_payments=yearly.estimated_payments,
            children=yearly.children,
            filing_status=yearly.filing_status,
        )
        result = calc.calculate(tax_input)

        # Generate PDF with template overlay
        pdf_path = output_dir / f"1040_{year}.pdf"
        success = generate_filled_pdf(year, result, pdf_path)

        # Generate JSON sidecar
        if success:
            generate_json_sidecar(year, result, yearly, pdf_path)

        # Report
        status = "OK" if success else "FAILED"
        refund_or_owed = f"Refund: ${result.refund:,}" if result.refund else f"Owed: ${result.amount_owed:,}"
        print(f"  {year}: {yearly.filing_status}, Income: ${result.total_income:,}, Tax: ${result.total_tax:,}, {refund_or_owed} [{status}]")

    print(f"\nOutput: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Generate sample Form 1040 PDFs using IRS templates")
    parser.add_argument("--persona", help="Generate specific persona (e.g., alex_chen)")
    parser.add_argument("--year", type=int, help="Generate single year")
    parser.add_argument("--list", action="store_true", help="List available personas")
    args = parser.parse_args()

    personas = {
        "alex_chen": ALEX_CHEN_PERSONA,
        "maria_garcia": MARIA_GARCIA_PERSONA,
    }

    if args.list:
        print("Available personas:")
        for name, data in personas.items():
            years = sorted(data.keys())
            print(f"  {name}: {years[0]}-{years[-1]} ({len(years)} years)")
        return

    print("=" * 60)
    print("Form 1040 Test Data Generator (Template Overlay)")
    print("=" * 60)

    if args.persona:
        if args.persona not in personas:
            print(f"Unknown persona: {args.persona}")
            print(f"Available: {list(personas.keys())}")
            return
        years = [args.year] if args.year else None
        generate_persona(args.persona, personas[args.persona], years)
    else:
        # Generate all personas
        for name, data in personas.items():
            years = [args.year] if args.year else None
            generate_persona(name, data, years)

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
