"""
Schedule 1 (2020) field mappings - Additional Income and Adjustments to Income.

Calibrated against: f1040s1--2020.pdf (IRS blank template)
Page dimensions: 612 x 792 points
Note: IRS 2020 template file contains 2020 form year due to IRS release timing.

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

    # === Part II - Adjustments to Income (2020: single page form) ===

    "sched1_educator_expenses": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 366, 576, 378),
        "label": "Educator expenses",
        "category": "schedule_1",
        "line": "11",
    },

    "sched1_business_expenses": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 378, 576, 390),
        "label": "Certain business expenses of reservists",
        "category": "schedule_1",
        "line": "12",
    },

    "sched1_hsa_deduction": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 396, 576, 408),  # Calibrated from manual PDF: top=402
        "label": "Health savings account deduction",
        "category": "schedule_1",
        "line": "13",
    },

    "sched1_moving_expenses": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 414, 576, 426),
        "label": "Moving expenses for Armed Forces",
        "category": "schedule_1",
        "line": "14",
    },

    "sched1_se_tax_deduction": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 426, 576, 438),
        "label": "Deductible part of self-employment tax",
        "category": "schedule_1",
        "line": "15",
    },

    "sched1_sep_simple": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 438, 576, 450),
        "label": "Self-employed SEP, SIMPLE plans",
        "category": "schedule_1",
        "line": "16",
    },

    "sched1_se_health_insurance": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 450, 576, 462),
        "label": "Self-employed health insurance deduction",
        "category": "schedule_1",
        "line": "17",
    },

    "sched1_early_withdrawal_penalty": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 462, 576, 474),
        "label": "Penalty on early withdrawal of savings",
        "category": "schedule_1",
        "line": "18",
    },

    "sched1_alimony_paid": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 474, 576, 486),
        "label": "Alimony paid",
        "category": "schedule_1",
        "line": "19a",
    },

    "sched1_ira_deduction": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 558, 576, 570),
        "label": "IRA deduction",
        "category": "schedule_1",
        "line": "20",
    },

    "sched1_student_loan_interest": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 576, 576, 588),  # Calibrated from manual PDF: top=582
        "label": "Student loan interest deduction",
        "category": "schedule_1",
        "line": "21",
    },

    "sched1_archer_msa": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 600, 576, 612),
        "label": "Archer MSA deduction",
        "category": "schedule_1",
        "line": "23",
    },

    "sched1_total_other_adjustments": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 612, 576, 624),
        "label": "Total other adjustments",
        "category": "schedule_1",
        "line": "25",
    },

    "sched1_total_adjustments": {
        "page": 0,  # 2020 Schedule 1 is single page
        "bbox": (504, 624, 576, 636),  # Calibrated from manual PDF: top=630
        "label": "Total adjustments to income",
        "category": "schedule_1",
        "line": "22",  # 2020 uses line 22 for total adjustments
    },
}
