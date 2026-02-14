"""
Form 1040 (2025) field mappings - CALIBRATED.

Calibrated against: f1040.pdf (IRS 2025 blank template)
Page dimensions: 612 x 792 points

IMPORTANT: The 2025 form has a significantly different layout!
- Lines 11-15 moved from page 0 to page 1
- Page 1 tax calculation starts at y=159 (not y=39)

Coordinate system:
- Origin (0, 0) is top-left of the page
- x increases to the right
- y increases downward
- Units are PDF points (1/72 inch)

Bounding box format: (x0, y0, x1, y1)
"""

FIELDS = {
    # === PAGE 0 (index 0): Income only ===

    "wages": {
        "page": 0,
        "bbox": (505, 561, 575, 573),
        "label": "Wages, salaries, tips",
        "category": "income",
        "line": "1z",
    },

    "taxable_interest": {
        "page": 0,
        "bbox": (505, 573, 575, 585),
        "label": "Taxable interest",
        "category": "income",
        "line": "2b",
    },

    "ordinary_dividends": {
        "page": 0,
        "bbox": (505, 585, 575, 597),
        "label": "Ordinary dividends",
        "category": "income",
        "line": "3b",
    },

    "ira_distributions": {
        "page": 0,
        "bbox": (505, 609, 575, 621),
        "label": "IRA distributions",
        "category": "income",
        "line": "4b",
    },

    "pensions": {
        "page": 0,
        "bbox": (505, 633, 575, 645),
        "label": "Pensions and annuities",
        "category": "income",
        "line": "5b",
    },

    "social_security": {
        "page": 0,
        "bbox": (505, 657, 575, 669),
        "label": "Social security benefits",
        "category": "income",
        "line": "6b",
    },

    "other_income": {
        "page": 0,
        "bbox": (505, 717, 575, 729),
        "label": "Other income",
        "category": "income",
        "line": "8",
    },

    "total_income": {
        "page": 0,
        "bbox": (505, 729, 575, 741),
        "label": "Total income",
        "category": "income",
        "line": "9",
    },

    "adjustments": {
        "page": 0,
        "bbox": (505, 741, 575, 753),
        "label": "Adjustments to income",
        "category": "income",
        "line": "10",
    },

    # === PAGE 1 (index 1): AGI, deductions, tax calculation ===

    "agi": {
        "page": 1,
        "bbox": (505, 39, 575, 51),
        "label": "Adjusted gross income",
        "category": "income",
        "line": "11b",
    },

    "deductions": {
        "page": 1,
        "bbox": (505, 99, 575, 111),
        "label": "Deductions",
        "category": "deductions",
        "line": "12e",
    },

    "qbi_deduction": {
        "page": 1,
        "bbox": (505, 111, 575, 123),
        "label": "QBI deduction",
        "category": "deductions",
        "line": "13a",
    },

    "total_deductions": {
        "page": 1,
        "bbox": (505, 135, 575, 147),
        "label": "Total deductions",
        "category": "deductions",
        "line": "14",
    },

    "taxable_income": {
        "page": 1,
        "bbox": (505, 147, 575, 159),
        "label": "Taxable income",
        "category": "income",
        "line": "15",
    },

    "tax_amount": {
        "page": 1,
        "bbox": (505, 159, 575, 171),
        "label": "Tax",
        "category": "tax_computation",
        "line": "16",
    },

    "schedule_2_tax": {
        "page": 1,
        "bbox": (505, 171, 575, 183),
        "label": "Schedule 2 tax",
        "category": "tax_computation",
        "line": "17",
    },

    "tax_before_credits": {
        "page": 1,
        "bbox": (505, 183, 575, 195),
        "label": "Tax before credits",
        "category": "tax_computation",
        "line": "18",
    },

    "child_tax_credit": {
        "page": 1,
        "bbox": (505, 195, 575, 207),
        "label": "Child tax credit",
        "category": "credits",
        "line": "19",
    },

    "schedule_3_credits": {
        "page": 1,
        "bbox": (505, 207, 575, 219),
        "label": "Schedule 3 credits",
        "category": "credits",
        "line": "20",
    },

    "total_credits": {
        "page": 1,
        "bbox": (505, 219, 575, 231),
        "label": "Total credits",
        "category": "credits",
        "line": "21",
    },

    "tax_after_credits": {
        "page": 1,
        "bbox": (505, 231, 575, 243),
        "label": "Tax after credits",
        "category": "tax_computation",
        "line": "22",
    },

    "other_taxes": {
        "page": 1,
        "bbox": (505, 243, 575, 255),
        "label": "Other taxes",
        "category": "tax_computation",
        "line": "23",
    },

    "total_tax": {
        "page": 1,
        "bbox": (505, 255, 575, 267),
        "label": "Total tax",
        "category": "tax_computation",
        "line": "24",
    },

    "federal_withholding": {
        "page": 1,
        "bbox": (505, 315, 575, 327),
        "label": "Federal withholding",
        "category": "payments",
        "line": "25d",
    },

    "estimated_payments": {
        "page": 1,
        "bbox": (505, 327, 575, 339),
        "label": "Estimated tax payments",
        "category": "payments",
        "line": "26",
    },

    "other_payments": {
        "page": 1,
        "bbox": (505, 459, 575, 471),
        "label": "Other payments",
        "category": "payments",
        "line": "32",
    },

    "total_payments": {
        "page": 1,
        "bbox": (505, 471, 575, 483),
        "label": "Total payments",
        "category": "payments",
        "line": "33",
    },

    "overpaid": {
        "page": 1,
        "bbox": (505, 483, 575, 495),
        "label": "Amount overpaid",
        "category": "refund_owed",
        "line": "34",
    },

    "refund": {
        "page": 1,
        "bbox": (505, 495, 575, 507),
        "label": "Refund",
        "category": "refund_owed",
        "line": "35a",
    },

    "amount_owed": {
        "page": 1,
        "bbox": (505, 555, 575, 567),
        "label": "Amount you owe",
        "category": "refund_owed",
        "line": "37",
    },
}
