# Plan: Add LLM validation layer for PDF extraction

**Issue:** [ROH-39](https://linear.app/rohanr/issue/ROH-39/add-llm-validation-layer-for-pdf-extraction)
**Priority:** High
**Status:** Planning

---

## Context

After PaddleOCR-based PDF extraction, we have no way to verify that extracted values are correct. The current system:
- Uses label-based detection with PaddleOCR, which provides real OCR confidence scores (0.0-1.0) per field
- Captures `raw_text` for each extracted value (the actual OCR text before parsing)
- Stores a `needs_review` flag in the database but never shows it to users
- Has mathematical relationships between fields (e.g., `total_income = sum of income components`) that are never checked

While PaddleOCR is more robust than coordinate-based extraction, OCR can still misread values (e.g., "8" vs "0", commas vs periods). Math validation catches these errors by cross-checking field relationships. This is step 2 of the intended flow from CLAUDE.md: **Extract → LLM Validate → User Review → Confirm**.

## Summary

Add a validation layer that runs after extraction but before database storage. It performs two types of validation:
1. **Local math validation** — Check known mathematical relationships between fields (no API needed)
2. **LLM validation** — Use Claude to verify low-confidence fields against raw PDF text

Validation results update confidence scores and display issues to users in the upload summary overlay.

## Technical Approach

### Why This Approach

We're building validation in two layers:
- **Local math validation** catches obvious errors (totals don't match sums) instantly, with no API cost. This is especially valuable now that PaddleOCR can misread individual digits — math validation cross-checks relationships to catch these.
- **LLM validation** (Phase 2) handles ambiguous cases where human-like judgment helps, using the `raw_text` already captured by extraction.

This separation means the app remains functional even without API access, while providing enhanced validation when available.

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| LLM-only validation | Simpler code | API cost for every upload, fails without API | Too dependent on external service |
| Validate after database storage | Could batch validate | Loses raw_text context, harder to correct | Can't fix errors before they're stored |
| User manually reviews all fields | No code needed | Terrible UX, users won't do it | Defeats the purpose of extraction |

The chosen approach (local math + optional LLM) provides immediate value with graceful degradation.

## Phased Approach

This is a complex feature broken into phases. Each phase delivers value independently.

| Phase | Scope | Issue |
|-------|-------|-------|
| 1 | Local math validation + UI integration | To be created |
| 2 | LLM validation with raw text | To be created |

**Phase 1** (this plan) focuses on local math validation — no API calls, immediate value, lower risk.

---

## Task List

- 🟢 **Create validation service**
  - 🟢 Create `app/src/services/extractionValidator.ts`
  - 🟢 Implement `ValidationResult` and `ValidationIssue` interfaces
  - 🟢 Implement `runMathValidation()` with tax field relationship checks

- 🟢 **Integrate validation into upload flow**
  - 🟢 Add `validating` state to App.tsx
  - 🟢 Call validation after extraction, before `setPendingUpload()`
  - 🟢 Pass validation results to UploadSummaryOverlay

- 🟢 **Display validation results in UI**
  - 🟢 Add validation status indicator to UploadSummaryOverlay
  - 🟢 Show expandable list of issues with severity icons
  - 🟢 Add CSS styles for validation status (green/yellow/red)

- 🟢 **Add tests**
  - 🟢 Unit tests for math validation rules
  - 🟢 Tests for edge cases (missing fields, zero values)

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

---

## Major Changes

### 1. New Validation Service (extractionValidator.ts)

**Purpose:** Encapsulate all validation logic in a single service, following the pattern of existing services like `claude.ts` and `taxContext.ts`.

```typescript
// Key interfaces
interface ValidationResult {
  isValid: boolean;
  issues: ValidationIssue[];
  fieldUpdates: Map<string, number>; // fieldKey -> new confidence
}

interface ValidationIssue {
  severity: 'error' | 'warning';
  field: string;
  message: string;
  expected?: string;
  actual?: string;
}

// Main function
function validateExtraction(result: ExtractionResult): ValidationResult {
  const issues = runMathValidation(result.fields);
  // Update confidence for fields with issues
  // Return structured result
}
```

**Why:** Keeps validation logic separate from UI, making it testable and reusable for future LLM integration.

### 2. Math Validation Rules

These relationships are defined by IRS Form 1040 structure. Field keys match `extract.py`:

```typescript
const VALIDATION_RULES = [
  // Income waterfall (Form 1040 lines 1-9)
  // Note: Not all income components may be present; skip missing fields
  {
    name: 'income_sum',
    check: (f) => sum(['wages', 'taxable_interest', 'ordinary_dividends',
                       'capital_gains', 'other_income']) ≈ f.total_income,
    message: 'Income components don\'t sum to total income'
  },

  // AGI calculation (line 9 - line 10 = line 11)
  {
    name: 'agi_calc',
    check: (f) => f.total_income - f.adjustments ≈ f.agi,
    message: 'AGI doesn\'t match total income minus adjustments'
  },

  // Taxable income (line 11 - line 14 = line 15)
  {
    name: 'taxable_income_calc',
    check: (f) => f.agi - f.total_deductions ≈ f.taxable_income,
    message: 'Taxable income doesn\'t match AGI minus deductions'
  },

  // Payments sum (lines 25d + 26 + 27 ≈ line 33)
  // Note: EIC (line 27) is also a payment/credit
  {
    name: 'payments_sum',
    check: (f) => sum(['federal_withholding', 'estimated_payments', 'eic']) ≈ f.total_payments,
    message: 'Payment components don\'t sum to total payments'
  },

  // Refund/Owed logic (line 33 - line 24 = line 34 or line 37)
  {
    name: 'refund_owed',
    check: (f) => (f.total_payments - f.total_tax ≈ f.refund) ||
                  (f.total_tax - f.total_payments ≈ f.amount_owed),
    message: 'Refund/owed amount doesn\'t match payments minus tax'
  }
];
```

**Tolerance:** All checks use $1 tolerance to account for rounding.

**Note:** The `tax_credits` rule from the original plan is removed because we don't extract individual credit components that would sum to a total. The `total_tax` field (line 24) is the final tax after all credits.

**Why:** These relationships are defined by tax law and IRS forms — if they don't hold, something was extracted incorrectly.

### 3. Upload Flow Integration (App.tsx)

**Current flow:**
```
extractPdf() → setPendingUpload() → show overlay → confirm → store in DB
```

**After:**
```
extractPdf() → validateExtraction() → setPendingUpload(with validation) → show overlay → confirm → store in DB
```

**Code changes in handleFileSelected():**
```typescript
// After extraction succeeds
const validationResult = validateExtraction(result);

// Apply confidence updates to fields
if (validationResult.fieldUpdates.size > 0) {
  result.fields = result.fields.map(f => ({
    ...f,
    confidence: validationResult.fieldUpdates.get(f.key) ?? f.confidence
  }));
}

// Include validation in pending upload
setPendingUpload({
  path,
  filename,
  result,
  validationResult  // NEW
});
```

**Why:** Validation runs synchronously (no API call in Phase 1), so it doesn't add latency or complexity.

### 4. Upload Summary UI Enhancement

**Current:** Shows year, filing status, detected forms, field counts.

**After:** Adds validation status section:

```
┌─────────────────────────────────────────┐
│  Upload Summary                    2024 │
├─────────────────────────────────────────┤
│  ✓ Form 1040           31 fields        │
│  ✓ Schedule 1          22 fields        │
│  ✓ Schedule C          45 fields        │
│                                         │
│  Filing Status: Married Filing Jointly  │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  ⚠ Validation Warnings (2)         [v] │
│  ┌─────────────────────────────────────┐│
│  │ ⚠ total_income                     ││
│  │   Income components sum to $125,000 ││
│  │   but total_income is $130,000     ││
│  │                                     ││
│  │ ⚠ refund                           ││
│  │   Expected $5,234 based on         ││
│  │   payments - tax, got $5,134       ││
│  └─────────────────────────────────────┘│
│                                         │
│  [Re-upload]              [Continue →]  │
└─────────────────────────────────────────┘
```

**Visual design:**
- ✓ Green (#4ade80): All validations passed
- ⚠ Amber (#fbbf24): Warnings found (allow continue)
- ✗ Red (#ef4444): Errors found (still allow continue, but prominent warning)

**Why:** Users need to see validation results to make an informed decision about whether to proceed or re-upload a corrected PDF.

---

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Create | `app/src/services/extractionValidator.ts` | Validation logic and math checks |
| Create | `app/src/services/__tests__/extractionValidator.test.ts` | Unit tests |
| Modify | `app/src/App.tsx` | Integrate validation into upload flow |
| Modify | `app/src/components/UploadSummary/UploadSummaryOverlay.tsx` | Display validation results |
| Modify | `app/src/App.css` | Add validation status styles |

---

## Implementation Details

### Key Code: extractionValidator.ts

```typescript
import type { ExtractionResult, ExtractedField } from './pdfExtractor';

export interface ValidationIssue {
  severity: 'error' | 'warning';
  field: string;
  message: string;
  expected?: string;
  actual?: string;
}

export interface ValidationResult {
  isValid: boolean;
  issues: ValidationIssue[];
  fieldUpdates: Map<string, number>;
}

export function validateExtraction(result: ExtractionResult): ValidationResult {
  const issues: ValidationIssue[] = [];
  const fieldUpdates = new Map<string, number>();

  // Build field lookup (key -> value)
  const fields = new Map<string, number>();
  for (const f of result.fields) {
    if (f.value !== null) {
      fields.set(f.key, parseInt(f.value, 10));
    }
  }

  // Run validation rules
  issues.push(...checkIncomeSum(fields));
  issues.push(...checkAgiCalculation(fields));
  issues.push(...checkTaxableIncome(fields));
  issues.push(...checkPaymentsSum(fields));
  issues.push(...checkRefundOwed(fields));

  // Reduce confidence for fields with issues
  // Use multiplicative reduction since OCR confidence varies (not fixed 0.95)
  for (const issue of issues) {
    const currentConf = result.fields.find(f => f.key === issue.field)?.confidence ?? 0.9;
    const multiplier = issue.severity === 'error' ? 0.6 : 0.8;
    fieldUpdates.set(issue.field, Math.max(0.3, currentConf * multiplier));
  }

  return {
    isValid: issues.filter(i => i.severity === 'error').length === 0,
    issues,
    fieldUpdates
  };
}

// Helper: check if values are approximately equal (within $1)
function approxEqual(a: number | undefined, b: number | undefined): boolean {
  if (a === undefined || b === undefined) return true; // Can't validate missing
  return Math.abs(a - b) <= 1;
}
```

### Data Flow

```
PDF Upload
    │
    ▼
extractPdf() ──────────────────────────────────────┐
    │                                              │
    ▼                                              │
ExtractionResult                                   │
  - fields[] with values + confidence              │
    │                                              │
    ▼                                              │
validateExtraction() ◄─────────────────────────────┘
    │
    ├─► checkIncomeSum()
    ├─► checkAgiCalculation()
    ├─► checkTaxableIncome()
    ├─► checkPaymentsSum()
    └─► checkRefundOwed()
    │
    ▼
ValidationResult
  - issues[]
  - fieldUpdates (confidence adjustments)
    │
    ▼
setPendingUpload({ result, validationResult })
    │
    ▼
UploadSummaryOverlay
  - Shows detected forms
  - Shows validation status ◄── NEW
  - Shows issue list        ◄── NEW
    │
    ▼
User confirms → insertReturn() + insertFieldsBatch()
```

---

## Testing Strategy

### What to Test

1. **Income sum validation** — Catches when components don't sum to total
2. **AGI calculation** — Catches when AGI ≠ total_income - adjustments
3. **Missing fields** — Gracefully skips validation when required fields are null
4. **Zero values** — Handles $0 values correctly (common for credits, adjustments)
5. **Rounding tolerance** — Allows $1 variance without flagging

### How to Verify

1. Run unit tests:
   ```bash
   cd app && npm test -- extractionValidator
   ```

2. Manual test with real PDF:
   - Upload `test-data/choc3884_24i_FC.pdf`
   - Check that validation runs and issues display (if any)
   - Verify continue still works

3. Manual test with test PDF:
   - Upload `test-data/generated/alex_chen/1040_2024.pdf`
   - Should show validation passed (test data is mathematically consistent)

---

## Risks & Considerations

- **False positives:** Validation rules may flag legitimate edge cases (e.g., amended returns, partial-year returns). *Mitigation:* Use warnings, not errors; always allow user to continue.

- **Missing field handling:** Some PDFs may not have all fields extracted. *Mitigation:* Skip validation rules that require missing fields (fields with `value: null` or `confidence: 0`).

- **OCR confidence variability:** PaddleOCR confidence can vary widely (0.6-0.99). A field with 0.95 OCR confidence can still have wrong values if digits look similar. *Mitigation:* Math validation catches these regardless of OCR confidence.

- **Performance:** Math validation is O(n) where n = number of fields, which is negligible (<100 fields).

---

## Phase 2 Preview (Future)

Phase 2 will add LLM validation:
- `raw_text` is already captured by PaddleOCR extraction (no changes needed)
- Send low-confidence fields + raw_text to Claude for interpretation
- Handle OCR errors and ambiguous characters (e.g., "8" vs "0", "1" vs "l")
- Requires API key configured
- Can cross-reference against math validation issues to prioritize fields for LLM review

This plan focuses on Phase 1 only.

---

*This plan adds local math validation to catch PaddleOCR extraction errors before they reach the database.*
