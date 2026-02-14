"""
Form 1040 (2022) field mappings - CALIBRATED.

Calibrated against: f1040--2022.pdf (IRS blank template)
Page dimensions: 612 x 792 points

The 2022 Form 1040 layout.
Page 0: Income (lines 1-15)
Page 1: Tax computation, payments, refund/owed (lines 16-38)

Coordinate system:
- Origin (0, 0) is top-left of the page
- x increases to the right
- y increases downward
- Units are PDF points (1/72 inch)

Bounding box format: (x0, y0, x1, y1)
Value fields are at x≈505-575 (right of line labels at x≈489-500)
"""

FIELDS = {
    # === PAGE 0 (index 0): Income ===

    # Line 1z: Total wages from W-2
    "wages": {
        "page": 0,
        "bbox": (505, 477, 575, 487),
        "label": "Wages, salaries, tips",
        "category": "income",
        "line": "1z",
    },

    # Line 2b: Taxable interest
    "taxable_interest": {
        "page": 0,
        "bbox": (505, 489, 575, 499),
        "label": "Taxable interest",
        "category": "income",
        "line": "2b",
    },

    # Line 3b: Ordinary dividends
    "ordinary_dividends": {
        "page": 0,
        "bbox": (505, 501, 575, 511),
        "label": "Ordinary dividends",
        "category": "income",
        "line": "3b",
    },

    # Line 4b: IRA distributions (taxable)
    "ira_distributions": {
        "page": 0,
        "bbox": (505, 513, 575, 523),
        "label": "IRA distributions",
        "category": "income",
        "line": "4b",
    },

    # Line 5b: Pensions and annuities (taxable)
    "pensions": {
        "page": 0,
        "bbox": (505, 525, 575, 535),
        "label": "Pensions and annuities",
        "category": "income",
        "line": "5b",
    },

    # Line 6b: Social security benefits (taxable)
    "social_security": {
        "page": 0,
        "bbox": (505, 537, 575, 547),
        "label": "Social security benefits",
        "category": "income",
        "line": "6b",
    },

    # Line 7: Capital gain or loss
    "capital_gains": {
        "page": 0,
        "bbox": (505, 561, 575, 571),
        "label": "Capital gain or loss",
        "category": "income",
        "line": "7",
    },

    # Line 8: Other income
    "other_income": {
        "page": 0,
        "bbox": (505, 573, 575, 583),
        "label": "Other income",
        "category": "income",
        "line": "8",
    },

    # Line 9: Total income
    "total_income": {
        "page": 0,
        "bbox": (505, 585, 575, 595),
        "label": "Total income",
        "category": "income",
        "line": "9",
    },

    # Line 10: Adjustments to income
    "adjustments": {
        "page": 0,
        "bbox": (505, 597, 575, 607),
        "label": "Adjustments to income",
        "category": "income",
        "line": "10",
    },

    # Line 11: Adjusted gross income
    "agi": {
        "page": 0,
        "bbox": (505, 609, 575, 619),
        "label": "Adjusted gross income",
        "category": "income",
        "line": "11",
    },

    # Line 12: Standard/itemized deduction
    "deductions": {
        "page": 0,
        "bbox": (505, 621, 575, 631),
        "label": "Deductions",
        "category": "deductions",
        "line": "12",
    },

    # Line 13: QBI deduction
    "qbi_deduction": {
        "page": 0,
        "bbox": (505, 633, 575, 643),
        "label": "QBI deduction",
        "category": "deductions",
        "line": "13",
    },

    # Line 14: Total deductions
    "total_deductions": {
        "page": 0,
        "bbox": (505, 645, 575, 655),
        "label": "Total deductions",
        "category": "deductions",
        "line": "14",
    },

    # Line 15: Taxable income
    "taxable_income": {
        "page": 0,
        "bbox": (505, 657, 575, 667),
        "label": "Taxable income",
        "category": "income",
        "line": "15",
    },

    # === PAGE 1 (index 1): Tax computation ===

    # Line 16: Tax
    "tax_amount": {
        "page": 1,
        "bbox": (505, 39, 575, 49),
        "label": "Tax",
        "category": "tax_computation",
        "line": "16",
    },

    # Line 17: Schedule 2 tax
    "schedule_2_tax": {
        "page": 1,
        "bbox": (505, 51, 575, 61),
        "label": "Schedule 2 tax",
        "category": "tax_computation",
        "line": "17",
    },

    # Line 18: Total tax before credits
    "tax_before_credits": {
        "page": 1,
        "bbox": (505, 63, 575, 73),
        "label": "Tax before credits",
        "category": "tax_computation",
        "line": "18",
    },

    # Line 19: Child tax credit
    "child_tax_credit": {
        "page": 1,
        "bbox": (505, 75, 575, 85),
        "label": "Child tax credit",
        "category": "credits",
        "line": "19",
    },

    # Line 20: Schedule 3 credits
    "schedule_3_credits": {
        "page": 1,
        "bbox": (505, 87, 575, 97),
        "label": "Schedule 3 credits",
        "category": "credits",
        "line": "20",
    },

    # Line 21: Total credits
    "total_credits": {
        "page": 1,
        "bbox": (505, 99, 575, 109),
        "label": "Total credits",
        "category": "credits",
        "line": "21",
    },

    # Line 22: Tax after credits
    "tax_after_credits": {
        "page": 1,
        "bbox": (505, 111, 575, 121),
        "label": "Tax after credits",
        "category": "tax_computation",
        "line": "22",
    },

    # Line 23: Other taxes
    "other_taxes": {
        "page": 1,
        "bbox": (505, 123, 575, 133),
        "label": "Other taxes",
        "category": "tax_computation",
        "line": "23",
    },

    # Line 24: Total tax
    "total_tax": {
        "page": 1,
        "bbox": (505, 135, 575, 145),
        "label": "Total tax",
        "category": "tax_computation",
        "line": "24",
    },

    # Line 25d: Federal income tax withheld
    "federal_withholding": {
        "page": 1,
        "bbox": (505, 195, 575, 205),
        "label": "Federal withholding",
        "category": "payments",
        "line": "25d",
    },

    # Line 26: Estimated tax payments
    "estimated_payments": {
        "page": 1,
        "bbox": (505, 207, 575, 217),
        "label": "Estimated tax payments",
        "category": "payments",
        "line": "26",
    },

    # Line 32: Other payments
    "other_payments": {
        "page": 1,
        "bbox": (505, 279, 575, 289),
        "label": "Other payments",
        "category": "payments",
        "line": "32",
    },

    # Line 33: Total payments
    "total_payments": {
        "page": 1,
        "bbox": (505, 291, 575, 301),
        "label": "Total payments",
        "category": "payments",
        "line": "33",
    },

    # Line 34: Amount overpaid
    "overpaid": {
        "page": 1,
        "bbox": (505, 303, 575, 313),
        "label": "Amount overpaid",
        "category": "refund_owed",
        "line": "34",
    },

    # Line 35a: Refund
    "refund": {
        "page": 1,
        "bbox": (505, 315, 575, 325),
        "label": "Refund",
        "category": "refund_owed",
        "line": "35a",
    },

    # Line 37: Amount you owe
    "amount_owed": {
        "page": 1,
        "bbox": (505, 375, 575, 385),
        "label": "Amount you owe",
        "category": "refund_owed",
        "line": "37",
    },
}
