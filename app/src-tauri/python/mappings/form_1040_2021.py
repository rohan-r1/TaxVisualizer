"""
Form 1040 (2021) field mappings - Calibrated for IRS blank templates.

Calibrated against: IRS blank template f1040--2021.pdf + generated test PDFs
Page dimensions: 612 x 792 points

The 2021 Form 1040 has a layout similar to 2020.
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

    # Line 1z: Total wages - measured mid_y=359.4
    "wages": {
        "page": 0,
        "bbox": (515, 356, 555, 363),
        "label": "Wages, salaries, tips",
        "category": "income",
        "line": "1z",
    },

    # Line 2b: Taxable interest - measured mid_y=371.4
    "taxable_interest": {
        "page": 0,
        "bbox": (530, 368, 555, 375),
        "label": "Taxable interest",
        "category": "income",
        "line": "2b",
    },

    # Line 3b: Ordinary dividends - measured mid_y=383.4
    "ordinary_dividends": {
        "page": 0,
        "bbox": (530, 380, 555, 387),
        "label": "Ordinary dividends",
        "category": "income",
        "line": "3b",
    },

    # Line 4b: IRA distributions (taxable) - estimate mid_y≈395
    "ira_distributions": {
        "page": 0,
        "bbox": (530, 392, 555, 399),
        "label": "IRA distributions",
        "category": "income",
        "line": "4b",
    },

    # Line 5b: Pensions (taxable) - estimate mid_y≈407
    "pensions": {
        "page": 0,
        "bbox": (530, 404, 555, 411),
        "label": "Pensions and annuities",
        "category": "income",
        "line": "5b",
    },

    # Line 6b: Social security benefits (taxable) - estimate mid_y≈419
    "social_security": {
        "page": 0,
        "bbox": (530, 416, 555, 423),
        "label": "Social security benefits",
        "category": "income",
        "line": "6b",
    },

    # Line 7: Capital gain or loss - measured mid_y=431.4
    "capital_gains": {
        "page": 0,
        "bbox": (525, 428, 555, 435),
        "label": "Capital gain or loss",
        "category": "income",
        "line": "7",
    },

    # Line 8: Other income - estimate mid_y≈443
    "other_income": {
        "page": 0,
        "bbox": (525, 440, 555, 447),
        "label": "Other income",
        "category": "income",
        "line": "8",
    },

    # Line 9: Total income - measured mid_y=455.4
    "total_income": {
        "page": 0,
        "bbox": (515, 452, 555, 459),
        "label": "Total income",
        "category": "income",
        "line": "9",
    },

    # Line 10: Adjustments to income - estimate mid_y≈467
    "adjustments": {
        "page": 0,
        "bbox": (515, 464, 555, 471),
        "label": "Adjustments to income",
        "category": "income",
        "line": "10",
    },

    # Line 11: Adjusted gross income - measured mid_y=479.4
    "agi": {
        "page": 0,
        "bbox": (515, 476, 555, 483),
        "label": "Adjusted gross income",
        "category": "income",
        "line": "11",
    },

    # Line 12: Standard deduction - measured mid_y=491.4
    "deductions": {
        "page": 0,
        "bbox": (515, 488, 555, 495),
        "label": "Deductions",
        "category": "deductions",
        "line": "12",
    },

    # Line 13: QBI deduction - estimate mid_y≈515
    "qbi_deduction": {
        "page": 0,
        "bbox": (515, 512, 555, 519),
        "label": "QBI deduction",
        "category": "deductions",
        "line": "13",
    },

    # Line 15: Taxable income - measured mid_y=551.4
    "taxable_income": {
        "page": 0,
        "bbox": (515, 548, 555, 555),
        "label": "Taxable income",
        "category": "income",
        "line": "15",
    },

    # === PAGE 1 (index 1): Tax computation ===

    # Line 16: Tax - measured mid_y=41.4
    "tax_amount": {
        "page": 1,
        "bbox": (515, 38, 555, 45),
        "label": "Tax",
        "category": "tax_computation",
        "line": "16",
    },

    # Line 17: Schedule 2 tax - estimate mid_y≈53
    "schedule_2_tax": {
        "page": 1,
        "bbox": (515, 50, 555, 57),
        "label": "Schedule 2 tax",
        "category": "tax_computation",
        "line": "17",
    },

    # Line 18: Tax before credits - estimate mid_y≈65
    "tax_before_credits": {
        "page": 1,
        "bbox": (515, 62, 555, 69),
        "label": "Tax before credits",
        "category": "tax_computation",
        "line": "18",
    },

    # Line 19: Child tax credit - estimate mid_y≈77
    "child_tax_credit": {
        "page": 1,
        "bbox": (515, 74, 555, 81),
        "label": "Child tax credit",
        "category": "credits",
        "line": "19",
    },

    # Line 20: Schedule 3 credits - estimate mid_y≈89
    "schedule_3_credits": {
        "page": 1,
        "bbox": (515, 86, 555, 93),
        "label": "Schedule 3 credits",
        "category": "credits",
        "line": "20",
    },

    # Line 22: Tax after credits - estimate mid_y≈113
    "tax_after_credits": {
        "page": 1,
        "bbox": (515, 110, 555, 117),
        "label": "Tax after credits",
        "category": "tax_computation",
        "line": "22",
    },

    # Line 23: Other taxes - estimate mid_y≈125
    "other_taxes": {
        "page": 1,
        "bbox": (515, 122, 555, 129),
        "label": "Other taxes",
        "category": "tax_computation",
        "line": "23",
    },

    # Line 24: Total tax - measured mid_y=137.4
    "total_tax": {
        "page": 1,
        "bbox": (515, 134, 555, 141),
        "label": "Total tax",
        "category": "tax_computation",
        "line": "24",
    },

    # Line 25d: Federal withholding - measured mid_y=197.4
    "federal_withholding": {
        "page": 1,
        "bbox": (515, 194, 555, 201),
        "label": "Federal withholding",
        "category": "payments",
        "line": "25d",
    },

    # Line 26: Estimated tax payments - estimate mid_y≈257
    "estimated_payments": {
        "page": 1,
        "bbox": (515, 254, 555, 261),
        "label": "Estimated tax payments",
        "category": "payments",
        "line": "26",
    },

    # Line 32: Other payments - estimate mid_y≈335
    "other_payments": {
        "page": 1,
        "bbox": (515, 332, 555, 339),
        "label": "Other payments",
        "category": "payments",
        "line": "32",
    },

    # Line 33: Total payments - measured mid_y=347.4
    "total_payments": {
        "page": 1,
        "bbox": (515, 344, 555, 351),
        "label": "Total payments",
        "category": "payments",
        "line": "33",
    },

    # Line 34: Amount overpaid - estimate mid_y≈359
    "overpaid": {
        "page": 1,
        "bbox": (515, 356, 555, 363),
        "label": "Amount overpaid",
        "category": "refund_owed",
        "line": "34",
    },

    # Line 35a: Refund - estimate mid_y≈371
    "refund": {
        "page": 1,
        "bbox": (515, 368, 555, 375),
        "label": "Refund",
        "category": "refund_owed",
        "line": "35a",
    },

    # Line 37: Amount you owe - measured mid_y=419.4
    "amount_owed": {
        "page": 1,
        "bbox": (525, 416, 555, 423),
        "label": "Amount you owe",
        "category": "refund_owed",
        "line": "37",
    },
}
