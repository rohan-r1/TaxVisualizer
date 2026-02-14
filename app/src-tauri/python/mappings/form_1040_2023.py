"""
Form 1040 (2023) field mappings - CALIBRATED.

Calibrated against: f1040--2023.pdf (IRS blank template)
Page dimensions: 612 x 792 points

Coordinate system:
- Origin (0, 0) is top-left of the page
- x increases to the right
- y increases downward
- Units are PDF points (1/72 inch)

Bounding box format: (x0, y0, x1, y1)
"""

FIELDS = {
    # === PAGE 0 (index 0): Income ===

    "wages": {
        "page": 0,
        "bbox": (505, 513, 575, 525),
        "label": "Wages, salaries, tips",
        "category": "income",
        "line": "1z",
    },

    "taxable_interest": {
        "page": 0,
        "bbox": (505, 525, 575, 537),
        "label": "Taxable interest",
        "category": "income",
        "line": "2b",
    },

    "ordinary_dividends": {
        "page": 0,
        "bbox": (505, 537, 575, 549),
        "label": "Ordinary dividends",
        "category": "income",
        "line": "3b",
    },

    "ira_distributions": {
        "page": 0,
        "bbox": (505, 549, 575, 561),
        "label": "IRA distributions",
        "category": "income",
        "line": "4b",
    },

    "pensions": {
        "page": 0,
        "bbox": (505, 561, 575, 573),
        "label": "Pensions and annuities",
        "category": "income",
        "line": "5b",
    },

    "social_security": {
        "page": 0,
        "bbox": (505, 573, 575, 585),
        "label": "Social security benefits",
        "category": "income",
        "line": "6b",
    },

    "capital_gains": {
        "page": 0,
        "bbox": (505, 597, 575, 609),
        "label": "Capital gain or loss",
        "category": "income",
        "line": "7",
    },

    "other_income": {
        "page": 0,
        "bbox": (505, 609, 575, 621),
        "label": "Other income",
        "category": "income",
        "line": "8",
    },

    "total_income": {
        "page": 0,
        "bbox": (505, 621, 575, 633),
        "label": "Total income",
        "category": "income",
        "line": "9",
    },

    "adjustments": {
        "page": 0,
        "bbox": (505, 633, 575, 645),
        "label": "Adjustments to income",
        "category": "income",
        "line": "10",
    },

    "agi": {
        "page": 0,
        "bbox": (505, 645, 575, 657),
        "label": "Adjusted gross income",
        "category": "income",
        "line": "11",
    },

    "deductions": {
        "page": 0,
        "bbox": (505, 657, 575, 669),
        "label": "Deductions",
        "category": "deductions",
        "line": "12",
    },

    "qbi_deduction": {
        "page": 0,
        "bbox": (505, 669, 575, 681),
        "label": "QBI deduction",
        "category": "deductions",
        "line": "13",
    },

    "total_deductions": {
        "page": 0,
        "bbox": (505, 681, 575, 693),
        "label": "Total deductions",
        "category": "deductions",
        "line": "14",
    },

    "taxable_income": {
        "page": 0,
        "bbox": (505, 693, 575, 705),
        "label": "Taxable income",
        "category": "income",
        "line": "15",
    },

    # === PAGE 1 (index 1): Tax computation ===

    "tax_amount": {
        "page": 1,
        "bbox": (505, 39, 575, 51),
        "label": "Tax",
        "category": "tax_computation",
        "line": "16",
    },

    "schedule_2_tax": {
        "page": 1,
        "bbox": (505, 51, 575, 63),
        "label": "Schedule 2 tax",
        "category": "tax_computation",
        "line": "17",
    },

    "tax_before_credits": {
        "page": 1,
        "bbox": (505, 63, 575, 75),
        "label": "Tax before credits",
        "category": "tax_computation",
        "line": "18",
    },

    "child_tax_credit": {
        "page": 1,
        "bbox": (505, 75, 575, 87),
        "label": "Child tax credit",
        "category": "credits",
        "line": "19",
    },

    "schedule_3_credits": {
        "page": 1,
        "bbox": (505, 87, 575, 99),
        "label": "Schedule 3 credits",
        "category": "credits",
        "line": "20",
    },

    "total_credits": {
        "page": 1,
        "bbox": (505, 99, 575, 111),
        "label": "Total credits",
        "category": "credits",
        "line": "21",
    },

    "tax_after_credits": {
        "page": 1,
        "bbox": (505, 111, 575, 123),
        "label": "Tax after credits",
        "category": "tax_computation",
        "line": "22",
    },

    "other_taxes": {
        "page": 1,
        "bbox": (505, 123, 575, 135),
        "label": "Other taxes",
        "category": "tax_computation",
        "line": "23",
    },

    "total_tax": {
        "page": 1,
        "bbox": (505, 135, 575, 147),
        "label": "Total tax",
        "category": "tax_computation",
        "line": "24",
    },

    "federal_withholding": {
        "page": 1,
        "bbox": (505, 195, 575, 207),
        "label": "Federal withholding",
        "category": "payments",
        "line": "25d",
    },

    "estimated_payments": {
        "page": 1,
        "bbox": (505, 207, 575, 219),
        "label": "Estimated tax payments",
        "category": "payments",
        "line": "26",
    },

    "other_payments": {
        "page": 1,
        "bbox": (505, 279, 575, 291),
        "label": "Other payments",
        "category": "payments",
        "line": "32",
    },

    "total_payments": {
        "page": 1,
        "bbox": (505, 291, 575, 303),
        "label": "Total payments",
        "category": "payments",
        "line": "33",
    },

    "overpaid": {
        "page": 1,
        "bbox": (505, 303, 575, 315),
        "label": "Amount overpaid",
        "category": "refund_owed",
        "line": "34",
    },

    "refund": {
        "page": 1,
        "bbox": (505, 315, 575, 327),
        "label": "Refund",
        "category": "refund_owed",
        "line": "35a",
    },

    "amount_owed": {
        "page": 1,
        "bbox": (505, 375, 575, 387),
        "label": "Amount you owe",
        "category": "refund_owed",
        "line": "37",
    },
}
