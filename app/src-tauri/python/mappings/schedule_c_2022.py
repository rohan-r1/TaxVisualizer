"""
Schedule C (2022) field mappings - Profit or Loss From Business.

Calibrated against: f1040sc--2022.pdf (IRS blank template)
Page dimensions: 612 x 792 points
Note: IRS 2022 template file contains 2022 form year due to IRS release timing.

Coordinate system:
- Origin (0, 0) is top-left of the page
- x increases to the right
- y increases downward
- Units are PDF points (1/72 inch)

Bounding box format: (x0, y0, x1, y1)

Schedule C has 2 pages:
- Page 0: Part I Income (Lines 1-7), Part II Expenses (Lines 8-28), Net Profit (Lines 29-31)
- Page 1: Part III Cost of Goods Sold (Lines 33-42), Part IV Vehicle Info, Part V Other Expenses

Note: The form has two columns of expenses on page 0:
- Left column: Lines 8-17 (around x=215-285)
- Right column: Lines 18-27 (around x=455-525)
- Summary lines (28-31) use the right-side value column (x=505-575)
"""

FIELDS = {
    # === PAGE 0: Part I - Income ===

    "schedc_gross_receipts": {
        "page": 0,
        "bbox": (505, 264, 575, 276),
        "label": "Gross receipts or sales",
        "category": "schedule_c",
        "line": "1",
    },

    "schedc_returns": {
        "page": 0,
        "bbox": (505, 276, 575, 288),
        "label": "Returns and allowances",
        "category": "schedule_c",
        "line": "2",
    },

    "schedc_net_receipts": {
        "page": 0,
        "bbox": (505, 288, 575, 300),
        "label": "Net receipts (line 1 minus line 2)",
        "category": "schedule_c",
        "line": "3",
    },

    "schedc_cogs": {
        "page": 0,
        "bbox": (505, 300, 575, 312),
        "label": "Cost of goods sold (from line 42)",
        "category": "schedule_c",
        "line": "4",
    },

    "schedc_gross_profit": {
        "page": 0,
        "bbox": (505, 312, 575, 324),
        "label": "Gross profit",
        "category": "schedule_c",
        "line": "5",
    },

    "schedc_other_income": {
        "page": 0,
        "bbox": (505, 324, 575, 336),
        "label": "Other income",
        "category": "schedule_c",
        "line": "6",
    },

    "schedc_gross_income": {
        "page": 0,
        "bbox": (505, 336, 575, 348),
        "label": "Gross income",
        "category": "schedule_c",
        "line": "7",
    },

    # === PAGE 0: Part II - Expenses (Left Column) ===

    "schedc_advertising": {
        "page": 0,
        "bbox": (215, 360, 285, 372),
        "label": "Advertising",
        "category": "schedule_c",
        "line": "8",
    },

    "schedc_car_expenses": {
        "page": 0,
        "bbox": (215, 372, 285, 384),
        "label": "Car and truck expenses",
        "category": "schedule_c",
        "line": "9",
    },

    "schedc_commissions": {
        "page": 0,
        "bbox": (215, 396, 285, 408),
        "label": "Commissions and fees",
        "category": "schedule_c",
        "line": "10",
    },

    "schedc_contract_labor": {
        "page": 0,
        "bbox": (215, 408, 285, 420),
        "label": "Contract labor",
        "category": "schedule_c",
        "line": "11",
    },

    "schedc_depletion": {
        "page": 0,
        "bbox": (215, 420, 285, 432),
        "label": "Depletion",
        "category": "schedule_c",
        "line": "12",
    },

    "schedc_depreciation": {
        "page": 0,
        "bbox": (215, 432, 285, 444),
        "label": "Depreciation (Form 4562)",
        "category": "schedule_c",
        "line": "13",
    },

    "schedc_employee_benefits": {
        "page": 0,
        "bbox": (215, 456, 285, 468),
        "label": "Employee benefit programs",
        "category": "schedule_c",
        "line": "14",
    },

    "schedc_insurance": {
        "page": 0,
        "bbox": (215, 492, 285, 504),
        "label": "Insurance (other than health)",
        "category": "schedule_c",
        "line": "15",
    },

    "schedc_interest_mortgage": {
        "page": 0,
        "bbox": (215, 504, 285, 516),
        "label": "Interest on business debt",
        "category": "schedule_c",
        "line": "16a",
    },

    "schedc_interest_other": {
        "page": 0,
        "bbox": (215, 528, 285, 540),
        "label": "Interest - other",
        "category": "schedule_c",
        "line": "16b",
    },

    "schedc_legal": {
        "page": 0,
        "bbox": (215, 540, 285, 552),
        "label": "Legal and professional services",
        "category": "schedule_c",
        "line": "17",
    },

    # === PAGE 0: Part II - Expenses (Right Column) ===

    "schedc_office_expense": {
        "page": 0,
        "bbox": (455, 360, 525, 372),
        "label": "Office expense",
        "category": "schedule_c",
        "line": "18",
    },

    "schedc_pension": {
        "page": 0,
        "bbox": (455, 372, 525, 384),
        "label": "Pension and profit-sharing",
        "category": "schedule_c",
        "line": "19",
    },

    "schedc_rent_vehicles": {
        "page": 0,
        "bbox": (455, 396, 525, 408),
        "label": "Rent - vehicles, machinery",
        "category": "schedule_c",
        "line": "20a",
    },

    "schedc_rent_other": {
        "page": 0,
        "bbox": (455, 408, 525, 420),
        "label": "Rent - other business property",
        "category": "schedule_c",
        "line": "20b",
    },

    "schedc_repairs": {
        "page": 0,
        "bbox": (455, 420, 525, 432),
        "label": "Repairs and maintenance",
        "category": "schedule_c",
        "line": "21",
    },

    "schedc_supplies": {
        "page": 0,
        "bbox": (455, 432, 525, 444),
        "label": "Supplies",
        "category": "schedule_c",
        "line": "22",
    },

    "schedc_taxes_licenses": {
        "page": 0,
        "bbox": (455, 444, 525, 456),
        "label": "Taxes and licenses",
        "category": "schedule_c",
        "line": "23",
    },

    "schedc_travel": {
        "page": 0,
        "bbox": (455, 468, 525, 480),
        "label": "Travel",
        "category": "schedule_c",
        "line": "24a",
    },

    "schedc_meals": {
        "page": 0,
        "bbox": (455, 480, 525, 492),
        "label": "Deductible meals",
        "category": "schedule_c",
        "line": "24b",
    },

    "schedc_utilities": {
        "page": 0,
        "bbox": (455, 492, 525, 504),
        "label": "Utilities",
        "category": "schedule_c",
        "line": "25",
    },

    "schedc_wages": {
        "page": 0,
        "bbox": (455, 504, 525, 516),
        "label": "Wages (less employment credits)",
        "category": "schedule_c",
        "line": "26",
    },

    "schedc_other_expenses_total": {
        "page": 0,
        "bbox": (455, 540, 525, 552),
        "label": "Total other expenses",
        "category": "schedule_c",
        "line": "27b",
    },

    # === PAGE 0: Summary Lines ===

    "schedc_total_expenses": {
        "page": 0,
        "bbox": (505, 552, 575, 564),
        "label": "Total expenses",
        "category": "schedule_c",
        "line": "28",
    },

    "schedc_tentative_profit": {
        "page": 0,
        "bbox": (505, 564, 575, 576),
        "label": "Tentative profit or loss",
        "category": "schedule_c",
        "line": "29",
    },

    "schedc_home_expense": {
        "page": 0,
        "bbox": (505, 624, 575, 636),
        "label": "Expenses for business use of home",
        "category": "schedule_c",
        "line": "30",
    },

    "schedc_net_profit": {
        "page": 0,
        "bbox": (505, 660, 575, 672),
        "label": "Net profit or loss",
        "category": "schedule_c",
        "line": "31",
    },

    # === PAGE 1: Part III - Cost of Goods Sold ===

    "schedc_inventory_begin": {
        "page": 1,
        "bbox": (505, 132, 575, 144),
        "label": "Inventory at beginning of year",
        "category": "schedule_c",
        "line": "35",
    },

    "schedc_purchases": {
        "page": 1,
        "bbox": (505, 156, 575, 168),
        "label": "Purchases less personal use",
        "category": "schedule_c",
        "line": "36",
    },

    "schedc_labor": {
        "page": 1,
        "bbox": (505, 180, 575, 192),
        "label": "Cost of labor",
        "category": "schedule_c",
        "line": "37",
    },

    "schedc_materials": {
        "page": 1,
        "bbox": (505, 204, 575, 216),
        "label": "Materials and supplies",
        "category": "schedule_c",
        "line": "38",
    },

    "schedc_other_costs": {
        "page": 1,
        "bbox": (505, 228, 575, 240),
        "label": "Other costs",
        "category": "schedule_c",
        "line": "39",
    },

    "schedc_cogs_subtotal": {
        "page": 1,
        "bbox": (505, 252, 575, 264),
        "label": "Total lines 35-39",
        "category": "schedule_c",
        "line": "40",
    },

    "schedc_inventory_end": {
        "page": 1,
        "bbox": (505, 276, 575, 288),
        "label": "Inventory at end of year",
        "category": "schedule_c",
        "line": "41",
    },

    "schedc_cogs_final": {
        "page": 1,
        "bbox": (505, 300, 575, 312),
        "label": "Cost of goods sold (to line 4)",
        "category": "schedule_c",
        "line": "42",
    },
}
