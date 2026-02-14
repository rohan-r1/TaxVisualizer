"""
Form 1040 (2021) field mappings - BACKFILLED to full coverage.

Calibrated against: 1040_2021_sample.pdf
Page dimensions: 612 x 792 points

The 2021 Form 1040 has a layout similar to 2020.
Page 0: Income, adjustments, deductions
Page 1: Tax computation, payments, refund/owed

Line structure for 2021 Form 1040:
- Line 1: Total wages (1a-1z format)
- Lines 2a/2b: Tax-exempt/taxable interest
- Lines 3a/3b: Qualified/ordinary dividends
- Lines 4a/4b: IRA distributions
- Lines 5a/5b: Pensions and annuities
- Lines 6a/6b: Social security benefits
- Line 7: Capital gain or loss
- Line 8: Other income
- Line 9: Total income
- Line 10: Adjustments
- Line 11: AGI
- Line 12: Standard/itemized deduction
- Line 13: QBI deduction
- Line 15: Taxable income
- Lines 16-24: Tax computation
- Lines 25-33: Payments
- Lines 34-37: Refund/owed

Coordinate system:
- Origin (0, 0) is top-left of the page
- x increases to the right
- y increases downward
- Units are PDF points (1/72 inch)

Bounding box format: (x0, y0, x1, y1)
"""

FIELDS = {
    # === PAGE 0 (index 0): Income and deductions ===

    # Line 1z: Total wages from W-2 - Value: 60,500
    "wages": {
        "page": 0,
        "bbox": (531, 491, 577, 503),
        "label": "Wages, salaries, tips",
        "category": "income",
        "line": "1z",
    },

    # Line 2b: Taxable interest - Value: 322
    "taxable_interest": {
        "page": 0,
        "bbox": (549, 418, 577, 430),
        "label": "Taxable interest",
        "category": "income",
        "line": "2b",
    },

    # Line 3b: Ordinary dividends - Value: 3,908
    "ordinary_dividends": {
        "page": 0,
        "bbox": (537, 477, 577, 489),
        "label": "Ordinary dividends",
        "category": "income",
        "line": "3b",
    },

    # Line 4b: IRA distributions (taxable)
    "ira_distributions": {
        "page": 0,
        "bbox": (537, 430, 577, 442),
        "label": "IRA distributions",
        "category": "income",
        "line": "4b",
    },

    # Line 5b: Pensions (taxable)
    "pensions": {
        "page": 0,
        "bbox": (537, 442, 577, 454),
        "label": "Pensions and annuities",
        "category": "income",
        "line": "5b",
    },

    # Line 6b: Social security benefits (taxable)
    "social_security": {
        "page": 0,
        "bbox": (537, 454, 577, 466),
        "label": "Social security benefits",
        "category": "income",
        "line": "6b",
    },

    # Line 7: Capital gain or loss
    "capital_gains": {
        "page": 0,
        "bbox": (531, 466, 577, 478),
        "label": "Capital gain or loss",
        "category": "income",
        "line": "7",
    },

    # Line 8: Other income
    "other_income": {
        "page": 0,
        "bbox": (531, 478, 577, 490),
        "label": "Other income",
        "category": "income",
        "line": "8",
    },

    # Line 9: Total income - Value: 64,730
    "total_income": {
        "page": 0,
        "bbox": (531, 506, 577, 518),
        "label": "Total income",
        "category": "income",
        "line": "9",
    },

    # Line 10: Adjustments to income
    "adjustments": {
        "page": 0,
        "bbox": (531, 518, 577, 530),
        "label": "Adjustments to income",
        "category": "income",
        "line": "10",
    },

    # Line 11: Adjusted gross income - Value: 55,647
    "agi": {
        "page": 0,
        "bbox": (531, 535, 577, 547),
        "label": "Adjusted gross income",
        "category": "income",
        "line": "11",
    },

    # Line 12: Standard deduction - Value: 12,550
    "deductions": {
        "page": 0,
        "bbox": (531, 575, 577, 587),
        "label": "Deductions",
        "category": "deductions",
        "line": "12",
    },

    # Line 13: QBI deduction
    "qbi_deduction": {
        "page": 0,
        "bbox": (531, 587, 577, 599),
        "label": "QBI deduction",
        "category": "deductions",
        "line": "13",
    },

    # Line 15: Taxable income - Value: 35,300
    "taxable_income": {
        "page": 0,
        "bbox": (531, 621, 577, 633),
        "label": "Taxable income",
        "category": "income",
        "line": "15",
    },

    # === PAGE 1 (index 1): Tax computation ===

    # Line 16: Tax - Value: 3,542
    "tax_amount": {
        "page": 1,
        "bbox": (537, 66, 577, 78),
        "label": "Tax",
        "category": "tax_computation",
        "line": "16",
    },

    # Line 17: Schedule 2 tax
    "schedule_2_tax": {
        "page": 1,
        "bbox": (537, 78, 577, 90),
        "label": "Schedule 2 tax",
        "category": "tax_computation",
        "line": "17",
    },

    # Line 18: Tax before credits - Value: 3,542
    "tax_before_credits": {
        "page": 1,
        "bbox": (537, 95, 577, 107),
        "label": "Tax before credits",
        "category": "tax_computation",
        "line": "18",
    },

    # Line 19: Child tax credit
    "child_tax_credit": {
        "page": 1,
        "bbox": (537, 107, 577, 119),
        "label": "Child tax credit",
        "category": "credits",
        "line": "19",
    },

    # Line 20: Schedule 3 credits
    "schedule_3_credits": {
        "page": 1,
        "bbox": (537, 119, 577, 131),
        "label": "Schedule 3 credits",
        "category": "credits",
        "line": "20",
    },

    # Line 22: Tax after credits - Value: 3,542
    "tax_after_credits": {
        "page": 1,
        "bbox": (537, 152, 577, 164),
        "label": "Tax after credits",
        "category": "tax_computation",
        "line": "22",
    },

    # Line 23: Other taxes - Value: 7,645
    "other_taxes": {
        "page": 1,
        "bbox": (537, 167, 577, 179),
        "label": "Other taxes",
        "category": "tax_computation",
        "line": "23",
    },

    # Line 24: Total tax - Value: 11,187
    "total_tax": {
        "page": 1,
        "bbox": (531, 181, 577, 193),
        "label": "Total tax",
        "category": "tax_computation",
        "line": "24",
    },

    # Line 25d: Payments - Value: 29
    "federal_withholding": {
        "page": 1,
        "bbox": (555, 245, 577, 257),
        "label": "Federal withholding",
        "category": "payments",
        "line": "25d",
    },

    # Line 26: Estimated tax payments
    "estimated_payments": {
        "page": 1,
        "bbox": (537, 257, 577, 269),
        "label": "Estimated tax payments",
        "category": "payments",
        "line": "26",
    },

    # Line 32: Other payments - Value: 8,036
    "other_payments": {
        "page": 1,
        "bbox": (537, 405, 577, 417),
        "label": "Other payments",
        "category": "payments",
        "line": "32",
    },

    # Line 33: Total payments - Value: 8,065
    "total_payments": {
        "page": 1,
        "bbox": (537, 417, 577, 429),
        "label": "Total payments",
        "category": "payments",
        "line": "33",
    },

    # Line 34: Amount overpaid
    "overpaid": {
        "page": 1,
        "bbox": (537, 477, 577, 489),
        "label": "Amount overpaid",
        "category": "refund_owed",
        "line": "34",
    },

    # Line 35a: Refund - Value: 3,162
    "refund": {
        "page": 1,
        "bbox": (537, 490, 577, 502),
        "label": "Refund",
        "category": "refund_owed",
        "line": "35a",
    },

    # Line 37: Amount you owe - Value: 40
    "amount_owed": {
        "page": 1,
        "bbox": (450, 503, 472, 515),
        "label": "Amount you owe",
        "category": "refund_owed",
        "line": "37",
    },
}
