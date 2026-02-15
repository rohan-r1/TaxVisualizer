"""
Schedule 1 (2018) field mappings - Additional Income and Adjustments to Income.

Calibrated against: f1040s1--2018.pdf (IRS blank template)
Page dimensions: 612 x 792 points
Note: IRS 2018 template file contains 2018 form year due to IRS release timing.

Coordinate system:
- Origin (0, 0) is top-left of the page
- x increases to the right
- y increases downward
- Units are PDF points (1/72 inch)

Bounding box format: (x0, y0, x1, y1)

Schedule 1 has 2 pages:
- Page 0: Part I - Additional Income (Lines 1-10)
- Page 1: Part II - Adjustments to Income (Lines 11-26)

Value boxes: x=545-580, height ~14 points
"""

FIELDS = {
    # === PAGE 0: Part I - Additional Income ===

    "sched1_taxable_refunds": {
        "page": 0,
        "bbox": (545, 170, 580, 184),
        "label": "Taxable refunds, credits, or offsets",
        "category": "schedule_1",
        "line": "1",
    },

    "sched1_alimony_received": {
        "page": 0,
        "bbox": (545, 182, 580, 196),
        "label": "Alimony received",
        "category": "schedule_1",
        "line": "2a",
    },

    "sched1_business_income": {
        "page": 0,
        "bbox": (545, 206, 580, 220),
        "label": "Business income or loss (Schedule C)",
        "category": "schedule_1",
        "line": "3",
    },

    "sched1_other_gains": {
        "page": 0,
        "bbox": (545, 218, 580, 232),
        "label": "Other gains or losses (Form 4797)",
        "category": "schedule_1",
        "line": "4",
    },

    "sched1_rental_income": {
        "page": 0,
        "bbox": (545, 230, 580, 244),
        "label": "Rental real estate, royalties, partnerships",
        "category": "schedule_1",
        "line": "5",
    },

    "sched1_farm_income": {
        "page": 0,
        "bbox": (545, 242, 580, 256),
        "label": "Farm income or loss (Schedule F)",
        "category": "schedule_1",
        "line": "6",
    },

    "sched1_unemployment": {
        "page": 0,
        "bbox": (545, 266, 580, 280),
        "label": "Unemployment compensation",
        "category": "schedule_1",
        "line": "7",
    },

    "sched1_total_additional_income": {
        "page": 0,
        "bbox": (545, 638, 580, 652),
        "label": "Total additional income",
        "category": "schedule_1",
        "line": "9",
    },

    "sched1_total_part1": {
        "page": 0,
        "bbox": (545, 662, 580, 676),
        "label": "Total from Part I (to Form 1040 line 8)",
        "category": "schedule_1",
        "line": "10",
    },

    # === Part II - Adjustments to Income (2018: single page form) ===
    # Note: 2018 Schedule 1 has a 2-column layout for adjustments
    # Left column (x: 381-453): educator, business_exp, hsa, moving, se_tax, sep, se_health, penalty, alimony, ira, student_loan
    # Right column (x: 489-561): total_adjustments (line 36)

    "sched1_educator_expenses": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 300, 453, 312),
        "label": "Educator expenses",
        "category": "schedule_1",
        "line": "11",
    },

    "sched1_business_expenses": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 312, 453, 324),
        "label": "Certain business expenses of reservists",
        "category": "schedule_1",
        "line": "12",
    },

    "sched1_hsa_deduction": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 336, 453, 348),
        "label": "Health savings account deduction",
        "category": "schedule_1",
        "line": "13",
    },

    "sched1_moving_expenses": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 348, 453, 360),
        "label": "Moving expenses for Armed Forces",
        "category": "schedule_1",
        "line": "14",
    },

    "sched1_se_tax_deduction": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 360, 453, 372),
        "label": "Deductible part of self-employment tax",
        "category": "schedule_1",
        "line": "15",
    },

    "sched1_sep_simple": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 372, 453, 384),
        "label": "Self-employed SEP, SIMPLE plans",
        "category": "schedule_1",
        "line": "16",
    },

    "sched1_se_health_insurance": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 384, 453, 396),
        "label": "Self-employed health insurance deduction",
        "category": "schedule_1",
        "line": "17",
    },

    "sched1_early_withdrawal_penalty": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 396, 453, 408),
        "label": "Penalty on early withdrawal of savings",
        "category": "schedule_1",
        "line": "18",
    },

    "sched1_alimony_paid": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 408, 453, 420),
        "label": "Alimony paid",
        "category": "schedule_1",
        "line": "19a",
    },

    "sched1_ira_deduction": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 420, 453, 432),
        "label": "IRA deduction",
        "category": "schedule_1",
        "line": "20",
    },

    "sched1_student_loan_interest": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 426, 453, 438),  # Calibrated from manual PDF: top=432
        "label": "Student loan interest deduction",
        "category": "schedule_1",
        "line": "21",
    },

    "sched1_archer_msa": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 444, 453, 456),
        "label": "Archer MSA deduction",
        "category": "schedule_1",
        "line": "23",
    },

    "sched1_total_other_adjustments": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (381, 456, 453, 468),
        "label": "Total other adjustments",
        "category": "schedule_1",
        "line": "25",
    },

    "sched1_total_adjustments": {
        "page": 0,  # 2018 Schedule 1 is single page
        "bbox": (489, 462, 561, 474),  # Calibrated from manual PDF: top=468, x: 489.6-560.9
        "label": "Total adjustments to income",
        "category": "schedule_1",
        "line": "36",  # 2018 uses line 36 for total adjustments
    },
}
