"""
Form 1040 (2018) field mappings - BACKFILLED to full coverage.

Calibrated against: 1040_2018_sample.pdf
Page dimensions: 612 x 1008 points (sample PDF)
Note: Official IRS template has 612 x 792 and different page structure.

The 2018 Form 1040 was a major redesign (the "postcard" form).
Page 0: Personal info, filing status, signature
Page 1: Income, tax, payments, refund (this is "Page 2" printed on form)

Line structure for 2018 Form 1040:
- Lines 1-5: Income components (wages, interest, dividends, IRA, pensions)
- Line 6: Total income (add lines 1-5 + Schedule 1, line 22)
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

    # Line 2b: Taxable interest (right column of line 2)
    "taxable_interest": {
        "page": 1,
        "bbox": (547, 140, 594, 153),
        "label": "Taxable interest",
        "category": "income",
        "line": "2b",
    },

    # Line 3b: Ordinary dividends (right column of line 3)
    "ordinary_dividends": {
        "page": 1,
        "bbox": (547, 152, 594, 165),
        "label": "Ordinary dividends",
        "category": "income",
        "line": "3b",
    },

    # Line 4b: IRA distributions taxable (right column of line 4)
    "ira_distributions": {
        "page": 1,
        "bbox": (547, 164, 594, 177),
        "label": "IRA distributions",
        "category": "income",
        "line": "4b",
    },

    # Line 5b: Pensions taxable (right column of line 5)
    "pensions": {
        "page": 1,
        "bbox": (547, 176, 594, 189),
        "label": "Pensions and annuities",
        "category": "income",
        "line": "5b",
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

    # Line 9: QBI deduction
    "qbi_deduction": {
        "page": 1,
        "bbox": (547, 236, 594, 249),
        "label": "QBI deduction",
        "category": "deductions",
        "line": "9",
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
    "tax_amount": {
        "page": 1,
        "bbox": (216, 262, 249, 275),
        "label": "Tax",
        "category": "tax_computation",
        "line": "11a",
    },

    # Line 11b: Schedule 2 tax (additional tax)
    "schedule_2_tax": {
        "page": 1,
        "bbox": (554, 262, 595, 275),
        "label": "Schedule 2 tax",
        "category": "tax_computation",
        "line": "11b",
    },

    # Line 12a: Child tax credit (left column)
    "child_tax_credit": {
        "page": 1,
        "bbox": (216, 284, 249, 297),
        "label": "Child tax credit",
        "category": "credits",
        "line": "12a",
    },

    # Line 12b: Credits from Schedule 3 (right column)
    "schedule_3_credits": {
        "page": 1,
        "bbox": (554, 284, 595, 297),
        "label": "Schedule 3 credits",
        "category": "credits",
        "line": "12b",
    },

    # Line 13: Tax minus credits
    "tax_after_credits": {
        "page": 1,
        "bbox": (547, 296, 594, 309),
        "label": "Tax after credits",
        "category": "tax_computation",
        "line": "13",
    },

    # Line 14: Other taxes from Schedule 4
    "other_taxes": {
        "page": 1,
        "bbox": (554, 308, 595, 321),
        "label": "Other taxes",
        "category": "tax_computation",
        "line": "14",
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
    "federal_withholding": {
        "page": 1,
        "bbox": (554, 348, 595, 361),
        "label": "Federal withholding",
        "category": "payments",
        "line": "16",
    },

    # Line 17: Refundable credits from Schedule 5
    "other_payments": {
        "page": 1,
        "bbox": (554, 360, 595, 373),
        "label": "Refundable credits",
        "category": "payments",
        "line": "17",
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
    "applied_to_next_year": {
        "page": 1,
        "bbox": (554, 452, 595, 465),
        "label": "Applied to next year",
        "category": "refund_owed",
        "line": "21",
    },

    # Line 22: Amount you owe
    "amount_owed": {
        "page": 1,
        "bbox": (554, 464, 595, 477),
        "label": "Amount you owe",
        "category": "refund_owed",
        "line": "22",
    },

    # Note: Some 2024-style fields don't exist in 2018:
    # - social_security: Reported differently in 2018 (not a separate line on main form)
    # - capital_gains: Reported on Schedule D, flows to Schedule 1
    # - adjustments: Part of AGI calculation (line 6 to 7), not a separate field
    # - estimated_payments: Included in line 18 total
}
