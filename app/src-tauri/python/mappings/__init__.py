"""
Form 1040 field mappings by year.

Each year's Form 1040 has slightly different field positions.
This module provides coordinate mappings for each supported year.
"""

from typing import Dict, Any, Optional
import re

# Import year-specific mappings
from . import form_1040_2018
from . import form_1040_2019
from . import form_1040_2020
from . import form_1040_2021
from . import form_1040_2022
from . import form_1040_2023
from . import form_1040_2024
from . import form_1040_2025

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
