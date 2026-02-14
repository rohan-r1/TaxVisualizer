"""
Form 1040 (2019) field mappings - BACKFILLED to full coverage.

Calibrated against: 1040_2019_sample.pdf
Page dimensions: 612 x 792 points

The 2019 Form 1040 returned to a more traditional 2-page layout.
Page 0: Income, adjustments, deductions
Page 1: Tax computation, payments, refund/owed

Line structure for 2019 Form 1040:
- Line 1: Wages, salaries, tips
- Lines 2a/2b: Tax-exempt/taxable interest
- Lines 3a/3b: Qualified/ordinary dividends
- Lines 4a/4b: IRA distributions
- Lines 5a/5b: Pensions and annuities
- Lines 6a/6b: Social security benefits
- Line 7a: Capital gain/loss
- Line 7b: Total income
- Line 8a: Adjustments
- Line 8b: AGI
- Lines 9-10: Standard/itemized deduction
- Line 11a: QBI deduction
- Line 11b: Taxable income
- Line 12: Tax
- Line 13: Total tax
- Lines 14-18: Payments
- Lines 19-23: Refund/owed

Coordinate system:
- Origin (0, 0) is top-left of the page
- x increases to the right
- y increases downward
- Units are PDF points (1/72 inch)

Bounding box format: (x0, y0, x1, y1)
"""

FIELDS = {
    # === PAGE 0 (index 0): Income and deductions ===

    # Line 1: Wages, salaries, tips - Value: 526,918
    "wages": {
        "page": 0,
        "bbox": (523, 338, 575, 350),
        "label": "Wages, salaries, tips",
        "category": "income",
        "line": "1",
    },

    # Line 2b: Taxable interest - Value: 2,099
    "taxable_interest": {
        "page": 0,
        "bbox": (535, 350, 575, 362),
        "label": "Taxable interest",
        "category": "income",
        "line": "2b",
    },

    # Line 3b: Ordinary dividends - Value: 334
    "ordinary_dividends": {
        "page": 0,
        "bbox": (547, 363, 575, 375),
        "label": "Ordinary dividends",
        "category": "income",
        "line": "3b",
    },

    # Line 4b: IRA distributions (taxable)
    "ira_distributions": {
        "page": 0,
        "bbox": (535, 375, 575, 387),
        "label": "IRA distributions",
        "category": "income",
        "line": "4b",
    },

    # Line 5b: Pensions (taxable)
    "pensions": {
        "page": 0,
        "bbox": (535, 387, 575, 399),
        "label": "Pensions and annuities",
        "category": "income",
        "line": "5b",
    },

    # Line 6b: Social security benefits (taxable)
    "social_security": {
        "page": 0,
        "bbox": (535, 399, 575, 411),
        "label": "Social security benefits",
        "category": "income",
        "line": "6b",
    },

    # Line 7a: Capital gain or loss
    "capital_gains": {
        "page": 0,
        "bbox": (523, 410, 575, 422),
        "label": "Capital gain or loss",
        "category": "income",
        "line": "7a",
    },

    # Line 7b: Total income - Value: 529,351
    "total_income": {
        "page": 0,
        "bbox": (523, 434, 575, 446),
        "label": "Total income",
        "category": "income",
        "line": "7b",
    },

    # Line 8a: Adjustments to income
    "adjustments": {
        "page": 0,
        "bbox": (523, 446, 575, 458),
        "label": "Adjustments to income",
        "category": "income",
        "line": "8a",
    },

    # Line 8b: Adjusted gross income - Value: 529,351
    "agi": {
        "page": 0,
        "bbox": (523, 458, 575, 470),
        "label": "Adjusted gross income",
        "category": "income",
        "line": "8b",
    },

    # Line 9/10: Standard or itemized deduction
    "deductions": {
        "page": 0,
        "bbox": (523, 482, 575, 494),
        "label": "Deductions",
        "category": "deductions",
        "line": "9",
    },

    # Line 11a: QBI deduction
    "qbi_deduction": {
        "page": 0,
        "bbox": (523, 494, 575, 506),
        "label": "QBI deduction",
        "category": "deductions",
        "line": "11a",
    },

    # Line 11b: Taxable income - Value: 499,450
    "taxable_income": {
        "page": 0,
        "bbox": (523, 507, 575, 519),
        "label": "Taxable income",
        "category": "income",
        "line": "11b",
    },

    # === PAGE 1 (index 1): Tax computation ===

    # Line 12a: Tax - Value: 125,189
    "tax_amount": {
        "page": 1,
        "bbox": (428, 39, 480, 51),
        "label": "Tax",
        "category": "tax_computation",
        "line": "12a",
    },

    # Line 12b: Tax (right column) - Value: 125,189
    "tax_before_credits": {
        "page": 1,
        "bbox": (522, 50, 574, 62),
        "label": "Tax before credits",
        "category": "tax_computation",
        "line": "12b",
    },

    # Line 13a: Child tax credit
    "child_tax_credit": {
        "page": 1,
        "bbox": (440, 62, 480, 74),
        "label": "Child tax credit",
        "category": "credits",
        "line": "13a",
    },

    # Line 13b: Total tax - Value: 125,189
    "total_tax": {
        "page": 1,
        "bbox": (522, 74, 574, 86),
        "label": "Total tax",
        "category": "tax_computation",
        "line": "13b",
    },

    # Line 18a: Federal income tax withheld
    "federal_withholding": {
        "page": 1,
        "bbox": (440, 183, 480, 195),
        "label": "Federal withholding",
        "category": "payments",
        "line": "18d",
    },

    # Line 18b: Estimated tax payments
    "estimated_payments": {
        "page": 1,
        "bbox": (440, 195, 480, 207),
        "label": "Estimated tax payments",
        "category": "payments",
        "line": "18e",
    },

    # Line 18e: Total other payments - Value: 2,000
    "other_payments": {
        "page": 1,
        "bbox": (534, 194, 574, 206),
        "label": "Other payments",
        "category": "payments",
        "line": "18e",
    },

    # Line 19: Total payments - Value: 2,000
    "total_payments": {
        "page": 1,
        "bbox": (534, 206, 574, 218),
        "label": "Total payments",
        "category": "payments",
        "line": "19",
    },

    # Line 20: Amount overpaid - Value: 2,000
    "overpaid": {
        "page": 1,
        "bbox": (534, 218, 574, 230),
        "label": "Amount overpaid",
        "category": "refund_owed",
        "line": "20",
    },

    # Line 21a: Refund - Value: 1,500
    "refund": {
        "page": 1,
        "bbox": (534, 230, 574, 242),
        "label": "Refund",
        "category": "refund_owed",
        "line": "21a",
    },

    # Line 23: Amount you owe - Value: 500
    "amount_owed": {
        "page": 1,
        "bbox": (452, 266, 480, 278),
        "label": "Amount you owe",
        "category": "refund_owed",
        "line": "23",
    },
}
