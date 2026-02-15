"""
Form 1040 field mappings by year.

Each year's Form 1040 has slightly different field positions.
This module provides coordinate mappings for each supported year.
"""

from typing import Dict, Any, Optional
import re

# Import year-specific Form 1040 mappings
from . import form_1040_2018
from . import form_1040_2019
from . import form_1040_2020
from . import form_1040_2021
from . import form_1040_2022
from . import form_1040_2023
from . import form_1040_2024
from . import form_1040_2025

# Import Schedule 1 mappings (2018-2024)
from . import schedule_1_2018
from . import schedule_1_2019
from . import schedule_1_2020
from . import schedule_1_2021
from . import schedule_1_2022
from . import schedule_1_2023
from . import schedule_1_2024

# Import Schedule A mappings (2018-2024)
from . import schedule_a_2018
from . import schedule_a_2019
from . import schedule_a_2020
from . import schedule_a_2021
from . import schedule_a_2022
from . import schedule_a_2023
from . import schedule_a_2024

# Import Schedule C mappings (2018-2024)
from . import schedule_c_2018
from . import schedule_c_2019
from . import schedule_c_2020
from . import schedule_c_2021
from . import schedule_c_2022
from . import schedule_c_2023
from . import schedule_c_2024

# Registry of all supported form years
FORM_MAPPINGS: Dict[int, Dict[str, Any]] = {
    2018: form_1040_2018.FIELDS,
    2019: form_1040_2019.FIELDS,
    2020: form_1040_2020.FIELDS,
    2021: form_1040_2021.FIELDS,
    2022: form_1040_2022.FIELDS,
    2023: form_1040_2023.FIELDS,
    2024: form_1040_2024.FIELDS,
    2025: form_1040_2025.FIELDS,
}

# Registry of schedule mappings by type and year
SCHEDULE_MAPPINGS: Dict[str, Dict[int, Dict[str, Any]]] = {
    'schedule_1': {
        2018: schedule_1_2018.FIELDS,
        2019: schedule_1_2019.FIELDS,
        2020: schedule_1_2020.FIELDS,
        2021: schedule_1_2021.FIELDS,
        2022: schedule_1_2022.FIELDS,
        2023: schedule_1_2023.FIELDS,
        2024: schedule_1_2024.FIELDS,
    },
    'schedule_a': {
        2018: schedule_a_2018.FIELDS,
        2019: schedule_a_2019.FIELDS,
        2020: schedule_a_2020.FIELDS,
        2021: schedule_a_2021.FIELDS,
        2022: schedule_a_2022.FIELDS,
        2023: schedule_a_2023.FIELDS,
        2024: schedule_a_2024.FIELDS,
    },
    'schedule_c': {
        2018: schedule_c_2018.FIELDS,
        2019: schedule_c_2019.FIELDS,
        2020: schedule_c_2020.FIELDS,
        2021: schedule_c_2021.FIELDS,
        2022: schedule_c_2022.FIELDS,
        2023: schedule_c_2023.FIELDS,
        2024: schedule_c_2024.FIELDS,
    },
}


def detect_form_year(page) -> Optional[int]:
    """
    Detect the tax year from a Form 1040 page.

    Args:
        page: A pdfplumber page object

    Returns:
        The detected year (e.g., 2018) or None if not found
    """
    text = page.extract_text() or ""

    # Look for "Form 1040" followed by a 4-digit year
    match = re.search(r'Form\s*1040[-A-Z]*\s*(20\d{2})', text, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # Try finding just a standalone year near "1040"
    match = re.search(r'1040.*?(20\d{2})', text)
    if match:
        return int(match.group(1))

    return None


def get_field_mapping(year: int) -> Dict[str, Any]:
    """
    Get the field mapping for a specific form year.

    Args:
        year: The tax year (e.g., 2018)

    Returns:
        Dictionary of field definitions with bounding boxes
    """
    if year in FORM_MAPPINGS:
        return FORM_MAPPINGS[year]

    # Fallback: use the closest available year
    if FORM_MAPPINGS:
        closest = min(FORM_MAPPINGS.keys(), key=lambda y: abs(y - year))
        return FORM_MAPPINGS[closest]

    # No mappings available
    return {}


def get_supported_years() -> list:
    """Return list of years with calibrated mappings."""
    return sorted(FORM_MAPPINGS.keys())


def get_schedule_mapping(schedule_type: str, year: int) -> Dict[str, Any]:
    """
    Get the field mapping for a specific schedule and year.

    Args:
        schedule_type: The schedule type (e.g., 'schedule_1', 'schedule_a', 'schedule_c')
        year: The tax year (e.g., 2024)

    Returns:
        Dictionary of field definitions with bounding boxes, or empty dict if not found.
    """
    if schedule_type not in SCHEDULE_MAPPINGS:
        return {}

    year_mappings = SCHEDULE_MAPPINGS[schedule_type]

    # Exact year match
    if year in year_mappings:
        return year_mappings[year]

    # Fallback to closest available year
    if year_mappings:
        closest = min(year_mappings.keys(), key=lambda y: abs(y - year))
        return year_mappings[closest]

    return {}


def get_schedule_supported_years(schedule_type: str) -> list:
    """Return list of years with calibrated mappings for a specific schedule."""
    if schedule_type in SCHEDULE_MAPPINGS:
        return sorted(SCHEDULE_MAPPINGS[schedule_type].keys())
    return []


# Schedule detection patterns
# Each schedule has multiple patterns to increase detection reliability
# IMPORTANT: Patterns must be specific enough to avoid matching references on Form 1040
SCHEDULE_PATTERNS: Dict[str, list] = {
    'schedule_1': [
        r'Schedule\s*1\s*\(Form\s*1040\)',
        r'SCHEDULE\s*1\s+Additional\s+Income',
    ],
    'schedule_a': [
        r'Schedule\s*A\s*\(Form\s*1040\)',
        r'SCHEDULE\s*A\s+Itemized\s+Deductions',
    ],
    'schedule_c': [
        r'Schedule\s*C\s*\(Form\s*1040\)',
        r'SCHEDULE\s*C\s+Profit\s+or\s+Loss',
    ],
}


def detect_schedules(pdf) -> Dict[str, Optional[int]]:
    """
    Detect which schedules are present in a multi-page PDF.

    Scans each page for schedule identifiers using regex patterns.
    Returns the page index where each schedule was found, or None if not found.

    Args:
        pdf: A pdfplumber PDF object

    Returns:
        Dictionary mapping schedule type to page index (0-based) or None.
        Example: {'schedule_1': 2, 'schedule_a': 3, 'schedule_c': None}
    """
    result: Dict[str, Optional[int]] = {key: None for key in SCHEDULE_PATTERNS}

    for page_idx, page in enumerate(pdf.pages):
        text = page.extract_text() or ""

        for schedule_type, patterns in SCHEDULE_PATTERNS.items():
            # Skip if already found this schedule
            if result[schedule_type] is not None:
                continue

            # Check each pattern for this schedule
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    result[schedule_type] = page_idx
                    break

    return result
