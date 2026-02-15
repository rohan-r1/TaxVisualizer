"""
Schedule A (2022) field mappings - Itemized Deductions.

Calibrated against: f1040sa--2022.pdf (IRS blank template)
Page dimensions: 612 x 792 points
Note: IRS 2022 template file contains 2022 form year due to IRS release timing.

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
        "bbox": (417, 210, 489, 222),  # Calibrated from manual PDF: top=216
        "label": "State and local income taxes",
        "category": "schedule_a",
        "line": "5a",
    },

    "scheda_real_estate_taxes": {
        "page": 0,
        "bbox": (417, 246, 489, 258),
        "label": "State and local real estate taxes",
        "category": "schedule_a",
        "line": "5b",
    },

    "scheda_personal_property_taxes": {
        "page": 0,
        "bbox": (417, 270, 489, 282),
        "label": "Personal property taxes",
        "category": "schedule_a",
        "line": "5c",
    },

    "scheda_salt_total_before_limit": {
        "page": 0,
        "bbox": (417, 282, 489, 294),
        "label": "Total SALT before limit",
        "category": "schedule_a",
        "line": "5d",
    },

    "scheda_salt_deduction": {
        "page": 0,
        "bbox": (504, 306, 576, 318),  # Calibrated from manual PDF: top=312
        "label": "SALT deduction (limited)",
        "category": "schedule_a",
        "line": "5e",
    },

    "scheda_other_taxes": {
        "page": 0,
        "bbox": (504, 342, 576, 354),
        "label": "Other taxes",
        "category": "schedule_a",
        "line": "6",
    },

    "scheda_total_taxes": {
        "page": 0,
        "bbox": (504, 354, 576, 366),
        "label": "Total taxes paid",
        "category": "schedule_a",
        "line": "7",
    },

    # === Interest You Paid ===

    "scheda_mortgage_interest_1098": {
        "page": 0,
        "bbox": (417, 366, 489, 378),  # Calibrated from manual PDF: top=372
        "label": "Home mortgage interest (Form 1098)",
        "category": "schedule_a",
        "line": "8a",
    },

    "scheda_mortgage_interest_other": {
        "page": 0,
        "bbox": (417, 456, 489, 468),
        "label": "Home mortgage interest (not on 1098)",
        "category": "schedule_a",
        "line": "8b",
    },

    "scheda_points": {
        "page": 0,
        "bbox": (417, 468, 489, 480),
        "label": "Points not reported on Form 1098",
        "category": "schedule_a",
        "line": "8c",
    },

    "scheda_mortgage_interest_total": {
        "page": 0,
        "bbox": (417, 486, 489, 498),
        "label": "Total home mortgage interest",
        "category": "schedule_a",
        "line": "8e",
    },

    "scheda_investment_interest": {
        "page": 0,
        "bbox": (417, 498, 489, 510),
        "label": "Investment interest",
        "category": "schedule_a",
        "line": "9",
    },

    "scheda_total_interest": {
        "page": 0,
        "bbox": (504, 510, 576, 522),  # Calibrated from manual PDF: top=516
        "label": "Total interest paid",
        "category": "schedule_a",
        "line": "10",
    },

    # === Gifts to Charity ===

    "scheda_charity_cash": {
        "page": 0,
        "bbox": (417, 534, 489, 546),  # Calibrated from manual PDF: top=540
        "label": "Charitable gifts by cash or check",
        "category": "schedule_a",
        "line": "11",
    },

    "scheda_charity_noncash": {
        "page": 0,
        "bbox": (417, 570, 489, 582),
        "label": "Charitable gifts other than cash",
        "category": "schedule_a",
        "line": "12",
    },

    "scheda_charity_carryover": {
        "page": 0,
        "bbox": (417, 582, 489, 594),
        "label": "Carryover from prior year",
        "category": "schedule_a",
        "line": "13",
    },

    "scheda_total_charity": {
        "page": 0,
        "bbox": (504, 582, 576, 594),  # Calibrated from manual PDF: top=588
        "label": "Total charitable contributions",
        "category": "schedule_a",
        "line": "14",
    },

    # === Casualty, Theft, and Other Deductions ===

    "scheda_casualty_loss": {
        "page": 0,
        "bbox": (504, 630, 576, 642),
        "label": "Casualty and theft losses",
        "category": "schedule_a",
        "line": "15",
    },

    "scheda_other_deductions": {
        "page": 0,
        "bbox": (504, 666, 576, 678),
        "label": "Other itemized deductions",
        "category": "schedule_a",
        "line": "16",
    },

    # === Total ===

    "scheda_total_itemized": {
        "page": 0,
        "bbox": (504, 678, 576, 690),  # Calibrated from manual PDF: top=684
        "label": "Total itemized deductions",
        "category": "schedule_a",
        "line": "17",
    },
}
