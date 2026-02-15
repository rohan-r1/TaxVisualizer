"""
Schedule A (2018) field mappings - Itemized Deductions.

Calibrated against: f1040sa--2018.pdf (IRS blank template)
Page dimensions: 612 x 792 points
Note: IRS 2018 template file contains 2018 form year due to IRS release timing.

Coordinate system:
- Origin (0, 0) is top-left of the page
- x increases to the right
- y increases downward
- Units are PDF points (1/72 inch)

Bounding box format: (x0, y0, x1, y1)

Schedule A is a single page with sections:
- Medical and Dental Expenses (Lines 1-4)
- Taxes You Paid (Lines 5a-7)
- Interest You Paid (Lines 8a-10)
- Gifts to Charity (Lines 11-14)
- Casualty and Theft Losses (Line 15)
- Other Itemized Deductions (Line 16)
- Total Itemized Deductions (Line 17)

Value boxes:
- Sub-items (5a-5e, 8a-8e): x=420-490 (left column)
- Main items (4, 7, 10, 14-17): x=545-580 (right column)
"""

FIELDS = {
    # === Medical and Dental Expenses ===

    "scheda_medical_expenses": {
        "page": 0,
        "bbox": (545, 118, 580, 132),
        "label": "Medical and dental expenses",
        "category": "schedule_a",
        "line": "1",
    },

    "scheda_medical_threshold": {
        "page": 0,
        "bbox": (545, 154, 580, 168),
        "label": "7.5% of AGI threshold",
        "category": "schedule_a",
        "line": "3",
    },

    "scheda_medical_deduction": {
        "page": 0,
        "bbox": (545, 166, 580, 180),
        "label": "Medical and dental deduction",
        "category": "schedule_a",
        "line": "4",
    },

    # === Taxes You Paid (SALT) ===

    "scheda_state_local_income_tax": {
        "page": 0,
        "bbox": (420, 220, 490, 234),
        "label": "State and local income taxes",
        "category": "schedule_a",
        "line": "5a",
    },

    "scheda_real_estate_taxes": {
        "page": 0,
        "bbox": (420, 232, 490, 246),
        "label": "State and local real estate taxes",
        "category": "schedule_a",
        "line": "5b",
    },

    "scheda_personal_property_taxes": {
        "page": 0,
        "bbox": (420, 244, 490, 258),
        "label": "Personal property taxes",
        "category": "schedule_a",
        "line": "5c",
    },

    "scheda_salt_total_before_limit": {
        "page": 0,
        "bbox": (420, 256, 490, 270),
        "label": "Total SALT before limit",
        "category": "schedule_a",
        "line": "5d",
    },

    "scheda_salt_deduction": {
        "page": 0,
        "bbox": (545, 300, 580, 314),
        "label": "SALT deduction (limited)",
        "category": "schedule_a",
        "line": "5e",
    },

    "scheda_other_taxes": {
        "page": 0,
        "bbox": (545, 340, 580, 354),
        "label": "Other taxes",
        "category": "schedule_a",
        "line": "6",
    },

    "scheda_total_taxes": {
        "page": 0,
        "bbox": (545, 352, 580, 366),
        "label": "Total taxes paid",
        "category": "schedule_a",
        "line": "7",
    },

    # === Interest You Paid ===

    "scheda_mortgage_interest_1098": {
        "page": 0,
        "bbox": (420, 412, 490, 426),
        "label": "Home mortgage interest (Form 1098)",
        "category": "schedule_a",
        "line": "8a",
    },

    "scheda_mortgage_interest_other": {
        "page": 0,
        "bbox": (420, 454, 490, 468),
        "label": "Home mortgage interest (not on 1098)",
        "category": "schedule_a",
        "line": "8b",
    },

    "scheda_points": {
        "page": 0,
        "bbox": (420, 502, 490, 516),
        "label": "Points not reported on Form 1098",
        "category": "schedule_a",
        "line": "8c",
    },

    "scheda_mortgage_interest_total": {
        "page": 0,
        "bbox": (420, 526, 490, 540),
        "label": "Total home mortgage interest",
        "category": "schedule_a",
        "line": "8e",
    },

    "scheda_investment_interest": {
        "page": 0,
        "bbox": (420, 538, 490, 552),
        "label": "Investment interest",
        "category": "schedule_a",
        "line": "9",
    },

    "scheda_total_interest": {
        "page": 0,
        "bbox": (545, 550, 580, 564),
        "label": "Total interest paid",
        "category": "schedule_a",
        "line": "10",
    },

    # === Gifts to Charity ===

    "scheda_charity_cash": {
        "page": 0,
        "bbox": (420, 574, 490, 588),
        "label": "Charitable gifts by cash or check",
        "category": "schedule_a",
        "line": "11",
    },

    "scheda_charity_noncash": {
        "page": 0,
        "bbox": (420, 598, 490, 612),
        "label": "Charitable gifts other than cash",
        "category": "schedule_a",
        "line": "12",
    },

    "scheda_charity_carryover": {
        "page": 0,
        "bbox": (420, 610, 490, 624),
        "label": "Carryover from prior year",
        "category": "schedule_a",
        "line": "13",
    },

    "scheda_total_charity": {
        "page": 0,
        "bbox": (545, 622, 580, 636),
        "label": "Total charitable contributions",
        "category": "schedule_a",
        "line": "14",
    },

    # === Casualty, Theft, and Other Deductions ===

    "scheda_casualty_loss": {
        "page": 0,
        "bbox": (545, 658, 580, 672),
        "label": "Casualty and theft losses",
        "category": "schedule_a",
        "line": "15",
    },

    "scheda_other_deductions": {
        "page": 0,
        "bbox": (545, 694, 580, 708),
        "label": "Other itemized deductions",
        "category": "schedule_a",
        "line": "16",
    },

    # === Total ===

    "scheda_total_itemized": {
        "page": 0,
        "bbox": (545, 714, 580, 728),
        "label": "Total itemized deductions",
        "category": "schedule_a",
        "line": "17",
    },
}
