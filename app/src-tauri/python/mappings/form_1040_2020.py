"""
Form 1040 (2020) field mappings - BACKFILLED to full coverage.

Calibrated against: 1040_2020_sample.pdf
Page dimensions: 612 x 792 points

The 2020 Form 1040 has a similar layout to 2019.
Page 0: Income, adjustments, deductions
Page 1: Tax computation, payments, refund/owed

Line structure for 2020 Form 1040:
- Line 1: Total wages (new layout with 1a-1z)
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

    # Line 1: Wages, salaries, tips - Value: 502,213
    "wages": {
        "page": 0,
        "bbox": (523, 356, 575, 368),
        "label": "Wages, salaries, tips",
        "category": "income",
        "line": "1",
    },

    # Line 2b: Taxable interest - Value: 2,049
    "taxable_interest": {
        "page": 0,
        "bbox": (535, 368, 575, 380),
        "label": "Taxable interest",
        "category": "income",
        "line": "2b",
    },

    # Line 3b: Ordinary dividends - Value: 69
    "ordinary_dividends": {
        "page": 0,
        "bbox": (553, 381, 575, 393),
        "label": "Ordinary dividends",
        "category": "income",
        "line": "3b",
    },

    # Line 4b: IRA distributions (taxable)
    "ira_distributions": {
        "page": 0,
        "bbox": (535, 393, 575, 405),
        "label": "IRA distributions",
        "category": "income",
        "line": "4b",
    },

    # Line 5b: Pensions (taxable)
    "pensions": {
        "page": 0,
        "bbox": (535, 405, 575, 417),
        "label": "Pensions and annuities",
        "category": "income",
        "line": "5b",
    },

    # Line 6b: Social security benefits (taxable)
    "social_security": {
        "page": 0,
        "bbox": (535, 417, 575, 429),
        "label": "Social security benefits",
        "category": "income",
        "line": "6b",
    },

    # Line 7: Capital gain or loss
    "capital_gains": {
        "page": 0,
        "bbox": (523, 428, 575, 440),
        "label": "Capital gain or loss",
        "category": "income",
        "line": "7",
    },

    # Line 8: Other income
    "other_income": {
        "page": 0,
        "bbox": (523, 440, 575, 452),
        "label": "Other income",
        "category": "income",
        "line": "8",
    },

    # Line 9: Total income - Value: 504,331
    "total_income": {
        "page": 0,
        "bbox": (523, 452, 575, 464),
        "label": "Total income",
        "category": "income",
        "line": "9",
    },

    # Line 10: Adjustments to income
    "adjustments": {
        "page": 0,
        "bbox": (523, 500, 575, 512),
        "label": "Adjustments to income",
        "category": "income",
        "line": "10",
    },

    # Line 11: Adjusted gross income - Value: 504,331
    "agi": {
        "page": 0,
        "bbox": (523, 512, 575, 524),
        "label": "Adjusted gross income",
        "category": "income",
        "line": "11",
    },

    # Line 12: Standard/itemized deduction - Value: 24,800
    "deductions": {
        "page": 0,
        "bbox": (529, 525, 575, 537),
        "label": "Deductions",
        "category": "deductions",
        "line": "12",
    },

    # Line 13: QBI deduction
    "qbi_deduction": {
        "page": 0,
        "bbox": (523, 537, 575, 549),
        "label": "QBI deduction",
        "category": "deductions",
        "line": "13",
    },

    # Line 15: Taxable income - Value: 479,531
    "taxable_income": {
        "page": 0,
        "bbox": (523, 559, 575, 571),
        "label": "Taxable income",
        "category": "income",
        "line": "15",
    },

    # === PAGE 1 (index 1): Tax computation ===

    # Line 16: Tax - Value: 117,421
    "tax_amount": {
        "page": 1,
        "bbox": (521, 38, 573, 50),
        "label": "Tax",
        "category": "tax_computation",
        "line": "16",
    },

    # Line 17: Schedule 2 tax - Value: 32
    "schedule_2_tax": {
        "page": 1,
        "bbox": (551, 50, 573, 62),
        "label": "Schedule 2 tax",
        "category": "tax_computation",
        "line": "17",
    },

    # Line 18: Total tax before credits - Value: 117,453
    "tax_before_credits": {
        "page": 1,
        "bbox": (521, 62, 573, 74),
        "label": "Tax before credits",
        "category": "tax_computation",
        "line": "18",
    },

    # Line 19: Child tax credit
    "child_tax_credit": {
        "page": 1,
        "bbox": (521, 74, 573, 86),
        "label": "Child tax credit",
        "category": "credits",
        "line": "19",
    },

    # Line 20: Schedule 3 credits
    "schedule_3_credits": {
        "page": 1,
        "bbox": (521, 86, 573, 98),
        "label": "Schedule 3 credits",
        "category": "credits",
        "line": "20",
    },

    # Line 22: Tax after credits - Value: 117,421
    "tax_after_credits": {
        "page": 1,
        "bbox": (521, 98, 573, 110),
        "label": "Tax after credits",
        "category": "tax_computation",
        "line": "22",
    },

    # Line 23: Other taxes - Value: 32
    "other_taxes": {
        "page": 1,
        "bbox": (551, 110, 573, 122),
        "label": "Other taxes",
        "category": "tax_computation",
        "line": "23",
    },

    # Line 24: Total tax - Value: 32
    "total_tax": {
        "page": 1,
        "bbox": (551, 134, 573, 146),
        "label": "Total tax",
        "category": "tax_computation",
        "line": "24",
    },

    # Line 25d: Federal withholding - Value: 500
    "federal_withholding": {
        "page": 1,
        "bbox": (545, 206, 573, 218),
        "label": "Federal withholding",
        "category": "payments",
        "line": "25d",
    },

    # Line 26: Estimated tax payments
    "estimated_payments": {
        "page": 1,
        "bbox": (545, 218, 573, 230),
        "label": "Estimated tax payments",
        "category": "payments",
        "line": "26",
    },

    # Line 32: Other payments
    "other_payments": {
        "page": 1,
        "bbox": (545, 278, 573, 290),
        "label": "Other payments",
        "category": "payments",
        "line": "32",
    },

    # Line 33: Total payments - Value: 500
    "total_payments": {
        "page": 1,
        "bbox": (545, 290, 573, 302),
        "label": "Total payments",
        "category": "payments",
        "line": "33",
    },

    # Line 34: Amount overpaid - Value: 468
    "overpaid": {
        "page": 1,
        "bbox": (545, 302, 573, 314),
        "label": "Amount overpaid",
        "category": "refund_owed",
        "line": "34",
    },

    # Line 35a: Refund
    "refund": {
        "page": 1,
        "bbox": (545, 314, 573, 326),
        "label": "Refund",
        "category": "refund_owed",
        "line": "35a",
    },

    # Line 37: Amount you owe - Value: 468
    "amount_owed": {
        "page": 1,
        "bbox": (451, 350, 479, 362),
        "label": "Amount you owe",
        "category": "refund_owed",
        "line": "37",
    },
}
