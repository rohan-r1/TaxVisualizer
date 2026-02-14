"""
Form 1040 (2018) field mappings - CORRECTED.

Calibrated against: 1040_2018_sample.pdf
Page dimensions: 612 x 1008 points (sample PDF)
Note: Official IRS template has 612 x 792 and different page structure.

The 2018 Form 1040 was a major redesign (the "postcard" form).
Page 0: Personal info, filing status, signature
Page 1: Income, tax, payments, refund (this is "Page 2" printed on form)

Line structure for 2018 Form 1040:
- Lines 1-5: Income components
- Line 6: Total income
- Line 7: Adjusted gross income (AGI)
- Line 8: Standard or itemized deduction
- Line 9: QBI deduction
- Line 10: Taxable income
- Line 11a: Tax (left column)
- Line 11b: Additional tax from Schedule 2
- Line 12a: Child tax credit
- Line 12b: Additional credits from Schedule 3
- Line 13: Tax minus credits
- Line 14: Other taxes (Schedule 4)
- Line 15: Total tax
- Line 16: Federal withholding
- Line 17: Refundable credits
- Line 18: Total payments
- Line 19: Overpayment
- Line 20a: Refund
- Line 21: Applied to next year
- Line 22: Amount owed

Coordinate system:
- Origin (0, 0) is top-left
- x increases right, y increases down
- Units are PDF points (1/72 inch)

Bounding box format: (x0, y0, x1, y1)
"""

# Values found in sample:
# '30,262' at x=549-592, y=128-141 (Line 1 wages)
# '44,682' at x=405-448, y=188-201 (Schedule 1, line 22 amount shown near line 6)
# '74,944' at x=549-592, y=188-201 (Line 6 total income)
# '74,944' at x=549-592, y=212-225 (Line 7 AGI)
# '20,398' at x=549-592, y=224-237 (Line 8 standard deduction)
# '5,251' at x=218-247, y=262-272 (Line 11a tax - LEFT column)
# '8,635' at x=556-593, y=284-297 (Line 12b credits from Schedule 3)
# '46,014' at x=549-592, y=336-349 (Line 15 total tax)
# '4,972' at x=556-593, y=392-405 (Line 18 total payments)
# '1,663' at x=556-593, y=464-477 (Line 21 applied to next year)

FIELDS = {
    # === PAGE 1 (index 1): Main income and tax ===

    # Line 1: Wages, salaries, tips
    "wages": {
        "page": 1,
        "bbox": (547, 128, 594, 141),
        "label": "Wages, salaries, tips",
        "category": "income",
        "line": "1",
    },

    # Line 6: Total income (add lines 1-5 + Schedule 1, line 22)
    "total_income": {
        "page": 1,
        "bbox": (547, 188, 594, 201),
        "label": "Total income",
        "category": "income",
        "line": "6",
    },

    # Line 7: Adjusted gross income
    "agi": {
        "page": 1,
        "bbox": (547, 212, 594, 225),
        "label": "Adjusted gross income",
        "category": "income",
        "line": "7",
    },

    # Line 8: Standard or itemized deduction
    "deductions": {
        "page": 1,
        "bbox": (547, 224, 594, 237),
        "label": "Standard/itemized deduction",
        "category": "deductions",
        "line": "8",
    },

    # Line 10: Taxable income
    "taxable_income": {
        "page": 1,
        "bbox": (547, 248, 594, 261),
        "label": "Taxable income",
        "category": "income",
        "line": "10",
    },

    # Line 11a: Tax (from tax tables or Schedule 2)
    "tax": {
        "page": 1,
        "bbox": (216, 262, 249, 275),
        "label": "Tax",
        "category": "tax_computation",
        "line": "11a",
    },

    # Line 12: Credits (child tax credit + Schedule 3)
    "credits": {
        "page": 1,
        "bbox": (554, 284, 595, 297),
        "label": "Credits",
        "category": "credits",
        "line": "12",
    },

    # Line 15: Total tax
    "total_tax": {
        "page": 1,
        "bbox": (547, 336, 594, 349),
        "label": "Total tax",
        "category": "tax_computation",
        "line": "15",
    },

    # Line 16: Federal income tax withheld
    "withholding": {
        "page": 1,
        "bbox": (554, 348, 595, 361),
        "label": "Federal withholding",
        "category": "payments",
        "line": "16",
    },

    # Line 18: Total payments
    "total_payments": {
        "page": 1,
        "bbox": (554, 392, 595, 405),
        "label": "Total payments",
        "category": "payments",
        "line": "18",
    },

    # Line 19: Overpayment
    "overpaid": {
        "page": 1,
        "bbox": (554, 404, 595, 417),
        "label": "Amount overpaid",
        "category": "refund_owed",
        "line": "19",
    },

    # Line 20a: Refund amount
    "refund": {
        "page": 1,
        "bbox": (554, 416, 595, 429),
        "label": "Refund",
        "category": "refund_owed",
        "line": "20a",
    },

    # Line 21: Applied to next year estimated tax
    # Note: In this sample, line 21 is blank (person owes money, not getting refund)
    "applied_to_next_year": {
        "page": 1,
        "bbox": (554, 452, 595, 465),
        "label": "Applied to next year",
        "category": "refund_owed",
        "line": "21",
    },

    # Line 22: Amount you owe
    # Value 1,663 appears at y=464-477 (total_tax 6635 - payments 4972 = 1663)
    "amount_owed": {
        "page": 1,
        "bbox": (554, 464, 595, 477),
        "label": "Amount you owe",
        "category": "refund_owed",
        "line": "22",
    },
}
