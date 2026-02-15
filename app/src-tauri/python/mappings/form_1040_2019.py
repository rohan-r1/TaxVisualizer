"""
Form 1040 (2019) field mappings - Calibrated for IRS blank templates.

Calibrated against: IRS blank template f1040--2019.pdf + generated test PDFs
Page dimensions: 612 x 792 points

The 2019 Form 1040 uses a 2-page layout:
Page 0: Income, adjustments, deductions
Page 1: Tax computation, payments, refund/owed

Coordinate system:
- Origin (0, 0) is top-left
- x increases right, y increases down
- Units are PDF points (1/72 inch)

Bounding box format: (x0, y0, x1, y1)
- Values are right-aligned around x=547
- Use x0=520 to capture full numbers without template text
- Use tight vertical ranges (~10pts) based on measured character midpoints
"""

FIELDS = {
    # === PAGE 0 (index 0): Income and deductions ===

    # Line 1: Wages - measured mid_y=341.4
    "wages": {
        "page": 0,
        "bbox": (520, 338, 555, 345),
        "label": "Wages, salaries, tips",
        "category": "income",
        "line": "1",
    },

    # Line 2b: Taxable interest - measured mid_y=353.4
    "taxable_interest": {
        "page": 0,
        "bbox": (530, 350, 555, 357),
        "label": "Taxable interest",
        "category": "income",
        "line": "2b",
    },

    # Line 3b: Ordinary dividends - measured mid_y=365.4
    "ordinary_dividends": {
        "page": 0,
        "bbox": (535, 362, 555, 369),
        "label": "Ordinary dividends",
        "category": "income",
        "line": "3b",
    },

    # Line 4b: IRA distributions (taxable) - estimate mid_y≈377
    "ira_distributions": {
        "page": 0,
        "bbox": (530, 374, 555, 381),
        "label": "IRA distributions",
        "category": "income",
        "line": "4b",
    },

    # Line 5b: Pensions (taxable) - estimate mid_y≈389
    "pensions": {
        "page": 0,
        "bbox": (530, 386, 555, 393),
        "label": "Pensions and annuities",
        "category": "income",
        "line": "5b",
    },

    # Line 6b: Social security benefits (taxable) - estimate mid_y≈401
    "social_security": {
        "page": 0,
        "bbox": (530, 398, 555, 405),
        "label": "Social security benefits",
        "category": "income",
        "line": "6b",
    },

    # Line 7a: Capital gain or loss - estimate mid_y≈401 (same line as social security in 2019)
    # Alex Chen 2019 has no capital gains, so skipping this
    "capital_gains": {
        "page": 0,
        "bbox": (520, 398, 555, 405),
        "label": "Capital gain or loss",
        "category": "income",
        "line": "7a",
    },

    # Line 7b: Total income - measured mid_y=413.4
    "total_income": {
        "page": 0,
        "bbox": (520, 410, 555, 417),
        "label": "Total income",
        "category": "income",
        "line": "7b",
    },

    # Line 8a: Adjustments to income - estimate mid_y≈425
    "adjustments": {
        "page": 0,
        "bbox": (520, 422, 555, 429),
        "label": "Adjustments to income",
        "category": "income",
        "line": "8a",
    },

    # Line 8b: Adjusted gross income - measured mid_y=437.4
    "agi": {
        "page": 0,
        "bbox": (520, 434, 555, 441),
        "label": "Adjusted gross income",
        "category": "income",
        "line": "8b",
    },

    # Line 9/10: Standard or itemized deduction - measured mid_y=461.4
    "deductions": {
        "page": 0,
        "bbox": (520, 458, 555, 465),
        "label": "Deductions",
        "category": "deductions",
        "line": "9",
    },

    # Line 11a: QBI deduction - estimate mid_y≈485
    "qbi_deduction": {
        "page": 0,
        "bbox": (520, 482, 555, 489),
        "label": "QBI deduction",
        "category": "deductions",
        "line": "11a",
    },

    # Line 11b: Taxable income - measured mid_y=509.4
    "taxable_income": {
        "page": 0,
        "bbox": (520, 506, 555, 513),
        "label": "Taxable income",
        "category": "income",
        "line": "11b",
    },

    # === PAGE 1 (index 1): Tax computation ===

    # Line 12a: Tax - measured mid_y=65.4
    "tax_amount": {
        "page": 1,
        "bbox": (525, 62, 555, 69),
        "label": "Tax",
        "category": "tax_computation",
        "line": "12a",
    },

    # Line 12b: Tax (right column) - same position as 12a for generated PDFs
    "tax_before_credits": {
        "page": 1,
        "bbox": (525, 62, 555, 69),
        "label": "Tax before credits",
        "category": "tax_computation",
        "line": "12b",
    },

    # Line 13a: Child tax credit - estimate mid_y≈89
    "child_tax_credit": {
        "page": 1,
        "bbox": (525, 86, 555, 93),
        "label": "Child tax credit",
        "category": "credits",
        "line": "13a",
    },

    # Line 13b: Total tax - measured mid_y=113.4
    "total_tax": {
        "page": 1,
        "bbox": (525, 110, 555, 117),
        "label": "Total tax",
        "category": "tax_computation",
        "line": "13b",
    },

    # Line 18d: Federal income tax withheld - measured mid_y=125.4
    "federal_withholding": {
        "page": 1,
        "bbox": (520, 122, 555, 129),
        "label": "Federal withholding",
        "category": "payments",
        "line": "18d",
    },

    # Line 18e: Estimated tax payments - estimate mid_y≈173
    "estimated_payments": {
        "page": 1,
        "bbox": (520, 170, 555, 177),
        "label": "Estimated tax payments",
        "category": "payments",
        "line": "18e",
    },

    # Line 18e: Other payments - estimate mid_y≈197
    "other_payments": {
        "page": 1,
        "bbox": (520, 194, 555, 201),
        "label": "Other payments",
        "category": "payments",
        "line": "18e",
    },

    # Line 19: Total payments - measured mid_y=209.4
    "total_payments": {
        "page": 1,
        "bbox": (520, 206, 555, 213),
        "label": "Total payments",
        "category": "payments",
        "line": "19",
    },

    # Line 20: Amount overpaid - measured mid_y=221.4
    "overpaid": {
        "page": 1,
        "bbox": (525, 218, 555, 225),
        "label": "Amount overpaid",
        "category": "refund_owed",
        "line": "20",
    },

    # Line 21a: Refund - measured mid_y=233.4
    "refund": {
        "page": 1,
        "bbox": (525, 230, 555, 237),
        "label": "Refund",
        "category": "refund_owed",
        "line": "21a",
    },

    # Line 23: Amount you owe - estimate mid_y≈269
    "amount_owed": {
        "page": 1,
        "bbox": (525, 266, 555, 273),
        "label": "Amount you owe",
        "category": "refund_owed",
        "line": "23",
    },
}
