# Plan: Create test data generator with realistic multi-year tax returns

**Issue:** [ROH-25](https://linear.app/rohanr/issue/ROH-25/create-test-data-generator-with-realistic-multi-year-tax-returns)
**Priority:** High
**Status:** Complete

---

## Context

We need reliable test data to validate PDF extraction accuracy across multiple years. Currently:
- `generate_sample_returns.py` exists but only creates 3 single-year personas (2024)
- Test data folder is flat/unorganized
- No multi-year continuity testing exists

This issue creates a proper test data infrastructure: a generator that produces mathematically-correct, year-over-year consistent returns, plus folder reorganization.

## Summary

Enhance the existing `generate_sample_returns.py` to create multi-year persona sequences (2018-2024), ensure all tax math is correct, and reorganize `test-data/` into `blank-templates/`, `generated/`, and `samples/` subfolders.

## Technical Approach

### Why This Approach

Continue using **ReportLab** (already in use) rather than PDF form-filling because:
1. Form-filling requires knowing exact field coordinates for each year's form (different every year)
2. ReportLab generation already works and matches our extraction bounding boxes
3. Faster iteration — no need to map IRS form fields

### Persona Design: "Alex Chen" — Software Engineer

A realistic 7-year career progression (2018-2024):

| Year | Age | Status | Salary | Key Events |
|------|-----|--------|--------|------------|
| 2018 | 25 | Single | $65,000 | First job out of grad school |
| 2019 | 26 | Single | $72,000 | 10% raise |
| 2020 | 27 | Single | $75,000 | Small raise (COVID year) |
| 2021 | 28 | Single | $85,000 | Job switch, big bump |
| 2022 | 29 | MFJ | $95,000 | Got married, spouse works |
| 2023 | 30 | MFJ | $105,000 | Promotion |
| 2024 | 31 | MFJ | $115,000 | Continued growth + baby (child tax credit) |

**Financial progression:**
- Withholding calibrated to result in small refund ($500-2000) most years
- Investment income grows over time ($0 → $500 → $2000)
- One year with amount owed (2021 — job switch, underwithholding)
- 2024: Child tax credit kicks in

## Task List

- 🟢 **Reorganize test-data folder** — Create proper subfolder structure
  - 🟢 Create `blank-templates/`, `generated/`, `samples/` folders
  - 🟢 Move existing files to appropriate locations
  - 🟢 Update any hardcoded paths in tests
- 🟢 **Create TaxCalculator class** — Ensure all math is correct
  - 🟢 Implement income aggregation (wages + interest + dividends + capital gains)
  - 🟢 Implement deduction logic (standard vs itemized)
  - 🟢 Implement tax bracket calculation (2018-2024 brackets)
  - 🟢 Implement credits (child tax credit, etc.)
  - 🟢 Calculate refund vs amount owed
- 🟢 **Create PersonaGenerator class** — Multi-year sequences
  - 🟢 Define persona data structure (base values + yearly progression)
  - 🟢 Implement "Alex Chen" persona with 7 years
  - 🟢 Generate consistent year-over-year data
- 🟢 **Enhance PDF generation** — Support all years
  - 🟢 Update ReportLab code to handle 2018-2024 layouts
  - 🟢 Generate JSON sidecars for each PDF
- 🟢 **Verify extraction accuracy** — Run accuracy tests
  - 🟢 Extract all generated PDFs
  - 🟢 Compare against expected values
  - 🟢 Achieve 100% accuracy on generated data

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### Folder Structure

**Current:**
```
test-data/
├── generate_sample_returns.py
└── sample-returns/
    ├── custom/
    ├── expected/
    ├── irs_1040_blank.pdf
    ├── f1040--2018.pdf ... f1040--2024.pdf
    └── 1040_2018_sample.pdf ... 1040_2022_sample.pdf
```

**After:**
```
test-data/
├── generate_sample_returns.py
├── blank-templates/           # IRS official blanks
│   ├── f1040--2018.pdf
│   ├── f1040--2019.pdf
│   ├── ... (through 2024)
│   └── schedules/
│       ├── irs_schedule_a_blank.pdf
│       └── ...
├── generated/                 # Output from generator
│   └── alex_chen/             # Persona folder
│       ├── 1040_2018.pdf
│       ├── 1040_2018.json
│       ├── 1040_2019.pdf
│       ├── 1040_2019.json
│       └── ... (through 2024)
└── samples/                   # Other samples (existing)
    ├── custom/
    ├── expected/
    └── historical/
        ├── 1040_2018_sample.pdf
        └── ...
```

### TaxCalculator Class

```python
class TaxCalculator:
    """Calculate tax liability with correct math for any year."""

    def __init__(self, year: int):
        self.year = year
        self.brackets = TAX_BRACKETS[year]
        self.standard_deduction = STANDARD_DEDUCTIONS[year]

    def calculate(self, income: TaxIncome, filing_status: str) -> TaxResult:
        # 1. Total income
        total_income = income.wages + income.interest + income.dividends + income.capital_gains

        # 2. AGI (after above-the-line deductions)
        agi = total_income - income.adjustments

        # 3. Taxable income
        deduction = self.standard_deduction[filing_status]
        taxable_income = max(0, agi - deduction)

        # 4. Tax liability (bracket calculation)
        tax = self._calculate_bracket_tax(taxable_income, filing_status)

        # 5. Credits
        tax_after_credits = max(0, tax - income.credits)

        # 6. Refund or owed
        payments = income.withholding + income.estimated_payments
        if payments > tax_after_credits:
            return TaxResult(refund=payments - tax_after_credits, ...)
        else:
            return TaxResult(amount_owed=tax_after_credits - payments, ...)
```

### Persona Data Structure

```python
@dataclass
class YearlyData:
    wages: int
    interest: int = 0
    dividends: int = 0
    capital_gains: int = 0
    withholding: int = 0
    filing_status: str = "Single"
    has_children: int = 0

ALEX_CHEN_PERSONA = {
    2018: YearlyData(wages=65000, interest=50, withholding=9500),
    2019: YearlyData(wages=72000, interest=120, withholding=10800),
    2020: YearlyData(wages=75000, interest=200, dividends=100, withholding=11200),
    2021: YearlyData(wages=85000, interest=350, dividends=200, withholding=11000),  # Underwithholding
    2022: YearlyData(wages=95000, interest=500, dividends=400, filing_status="MFJ", withholding=14000),
    2023: YearlyData(wages=105000, interest=800, dividends=600, capital_gains=1200, filing_status="MFJ", withholding=16000),
    2024: YearlyData(wages=115000, interest=1000, dividends=800, capital_gains=2000, filing_status="MFJ", has_children=1, withholding=17500),
}
```

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `test-data/generate_sample_returns.py` | Add TaxCalculator, PersonaGenerator, multi-year support |
| Create | `test-data/generated/alex_chen/` | Output folder for persona |
| Move | Various PDFs | Reorganize into blank-templates/, samples/ |
| Modify | `app/src-tauri/python/tests/test_accuracy.py` | Update paths after reorganization |

## Testing Strategy

### What to Test
- Generated PDFs extract correctly (100% accuracy)
- Tax math is correct (AGI = income - adjustments, etc.)
- Year-over-year values are realistic
- All filing statuses handled correctly

### How to Verify

```bash
# Generate the persona
cd test-data && python generate_sample_returns.py --persona alex_chen

# Run extraction accuracy tests
cd app/src-tauri/python && python -m pytest tests/test_accuracy.py -v

# Manual spot-check
python extract.py test-data/generated/alex_chen/1040_2022.pdf --pretty
```

## Risks & Considerations

- **Tax bracket changes:** Each year has different brackets. Need to encode 2018-2024 brackets accurately.
- **Form layout changes:** ReportLab coordinates may need adjustment per year (existing mappings can guide this).
- **Path updates:** Tests referencing old paths will break — need to update.

## Dependencies

- Existing `generate_sample_returns.py` as starting point
- ReportLab library (already installed)
- Tax bracket data for 2018-2024 (publicly available from IRS)

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
