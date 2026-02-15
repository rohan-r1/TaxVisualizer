"""
Form 1040 (2018) field mappings - Calibrated for IRS blank templates.

Calibrated against: IRS blank template f1040--2018.pdf + generated test PDFs
Page dimensions: 612 x 792 points
Note: Template has coversheet on page 0; after removal, form is on page 0 of output.

The 2018 Form 1040 was a major redesign (the "postcard" form).
After coversheet removal in generated PDFs:
Page 0: Income, tax, payments, refund (the main form)

Coordinate system:
- Origin (0, 0) is top-left
- x increases right, y increases down
- Units are PDF points (1/72 inch)

Bounding box format: (x0, y0, x1, y1)
- Values are right-aligned around x=547
- Use x0=510 to capture full numbers without template text
- Use tight vertical ranges (~10pts) based on measured character midpoints
"""

FIELDS = {
    # === PAGE 0 (index 0): Main income and tax ===
    # Values measured: characters have mid_y values at specific positions
    # Using ±5pt around mid_y for tight capture

    # Line 1: Wages - measured mid_y=43.4
    "wages": {
        "page": 0,
        "bbox": (510, 38, 575, 48),
        "label": "Wages, salaries, tips",
        "category": "income",
        "line": "1",
    },

    # Line 2b: Taxable interest - measured mid_y=55.4
    # Template text at mid_y=53.6, value at mid_y=55.4
    # Tightened y0 to 54 to exclude template text
    "taxable_interest": {
        "page": 0,
        "bbox": (525, 54, 575, 58),
        "label": "Taxable interest",
        "category": "income",
        "line": "2b",
    },

    # Line 3b: Ordinary dividends - estimate mid_y≈67
    "ordinary_dividends": {
        "page": 0,
        "bbox": (510, 62, 575, 72),
        "label": "Ordinary dividends",
        "category": "income",
        "line": "3b",
    },

    # Line 4b: IRA distributions - estimate mid_y≈79
    "ira_distributions": {
        "page": 0,
        "bbox": (510, 74, 575, 84),
        "label": "IRA distributions",
        "category": "income",
        "line": "4b",
    },

    # Line 5b: Pensions - estimate mid_y≈91
    "pensions": {
        "page": 0,
        "bbox": (510, 86, 575, 96),
        "label": "Pensions and annuities",
        "category": "income",
        "line": "5b",
    },

    # Line 6: Total income - measured mid_y=103.4
    "total_income": {
        "page": 0,
        "bbox": (510, 98, 575, 108),
        "label": "Total income",
        "category": "income",
        "line": "6",
    },

    # Line 7: AGI - measured mid_y=121.4
    "agi": {
        "page": 0,
        "bbox": (510, 116, 575, 126),
        "label": "Adjusted gross income",
        "category": "income",
        "line": "7",
    },

    # Line 8: Deductions - measured mid_y=133.4
    "deductions": {
        "page": 0,
        "bbox": (510, 128, 575, 138),
        "label": "Standard/itemized deduction",
        "category": "deductions",
        "line": "8",
    },

    # Line 9: QBI deduction - estimate mid_y≈145
    "qbi_deduction": {
        "page": 0,
        "bbox": (510, 140, 575, 150),
        "label": "QBI deduction",
        "category": "deductions",
        "line": "9",
    },

    # Line 10: Taxable income - measured mid_y=157.4
    "taxable_income": {
        "page": 0,
        "bbox": (510, 152, 575, 162),
        "label": "Taxable income",
        "category": "income",
        "line": "10",
    },

    # Line 11a: Tax - LEFT COLUMN - estimate mid_y≈170
    "tax_amount": {
        "page": 0,
        "bbox": (150, 165, 250, 175),
        "label": "Tax",
        "category": "tax_computation",
        "line": "11a",
    },

    # Line 11b: Schedule 2 tax - RIGHT COLUMN
    "schedule_2_tax": {
        "page": 0,
        "bbox": (510, 165, 575, 175),
        "label": "Schedule 2 tax",
        "category": "tax_computation",
        "line": "11b",
    },

    # Line 12a: Child tax credit - LEFT COLUMN
    "child_tax_credit": {
        "page": 0,
        "bbox": (150, 189, 250, 199),
        "label": "Child tax credit",
        "category": "credits",
        "line": "12a",
    },

    # Line 12b: Schedule 3 credits - RIGHT COLUMN
    "schedule_3_credits": {
        "page": 0,
        "bbox": (510, 189, 575, 199),
        "label": "Schedule 3 credits",
        "category": "credits",
        "line": "12b",
    },

    # Line 13: Tax after credits - estimate mid_y≈205
    "tax_after_credits": {
        "page": 0,
        "bbox": (510, 200, 575, 210),
        "label": "Tax after credits",
        "category": "tax_computation",
        "line": "13",
    },

    # Line 14: Other taxes - estimate mid_y≈217
    "other_taxes": {
        "page": 0,
        "bbox": (510, 212, 575, 222),
        "label": "Other taxes",
        "category": "tax_computation",
        "line": "14",
    },

    # Line 15: Total tax - measured mid_y=229.4
    "total_tax": {
        "page": 0,
        "bbox": (510, 224, 575, 234),
        "label": "Total tax",
        "category": "tax_computation",
        "line": "15",
    },

    # Line 16: Federal withholding - measured mid_y=241.4
    "federal_withholding": {
        "page": 0,
        "bbox": (510, 236, 575, 246),
        "label": "Federal withholding",
        "category": "payments",
        "line": "16",
    },

    # Line 17: Other payments - estimate mid_y≈253
    "other_payments": {
        "page": 0,
        "bbox": (510, 248, 575, 258),
        "label": "Refundable credits",
        "category": "payments",
        "line": "17",
    },

    # Line 18: Total payments - measured mid_y=277.4
    # Value at mid_y=277.4, template text at mid_y=282.0
    # Tightened y1 to 280 to exclude template text
    "total_payments": {
        "page": 0,
        "bbox": (525, 275, 575, 280),
        "label": "Total payments",
        "category": "payments",
        "line": "18",
    },

    # Line 19: Overpaid - measured mid_y=289.4
    "overpaid": {
        "page": 0,
        "bbox": (510, 284, 575, 294),
        "label": "Amount overpaid",
        "category": "refund_owed",
        "line": "19",
    },

    # Line 20a: Refund - measured mid_y=301.4
    # Template text at mid_y=299.6, value at mid_y=301.4
    # Tightened y0 to 300 to exclude template text
    "refund": {
        "page": 0,
        "bbox": (525, 300, 575, 304),
        "label": "Refund",
        "category": "refund_owed",
        "line": "20a",
    },

    # Line 21: Applied to next year - estimate mid_y≈337
    "applied_to_next_year": {
        "page": 0,
        "bbox": (510, 332, 575, 342),
        "label": "Applied to next year",
        "category": "refund_owed",
        "line": "21",
    },

    # Line 22: Amount owed - estimate mid_y≈349
    "amount_owed": {
        "page": 0,
        "bbox": (510, 344, 575, 354),
        "label": "Amount you owe",
        "category": "refund_owed",
        "line": "22",
    },
}
