# Plan: Enhanced parsing for Schedules A, C, and D

**Issue:** [ROH-14](https://linear.app/rohanr/issue/ROH-14/enhanced-parsing-for-schedules-a-c-and-d)
**Priority:** Low
**Status:** Complete

---

## Context

The chatbot now has access to Form 1040 field data (thanks to ROH-13), but users often want to discuss details from their schedules — itemized deductions, self-employment income, capital gains. Currently, the mock extraction only generates Form 1040 fields. This issue extends the data model and mock extraction to include common schedules.

**Why now:** This is Phase 2 of the enhanced data access work. Phase 1 (ROH-13) built the foundation; now we expand what data is available.

## Summary

Extend `mockExtraction.ts` to generate schedule-specific fields for Schedules A, C, and D. Add new categories and field definitions, then update the taxContext serializer to handle these new categories gracefully.

## Technical Approach

### Why This Approach

The mock extraction pattern is already established and working well. We're extending it rather than replacing it. This lets us:
1. Test the full UI/chatbot flow with schedule data before building real PDF extraction
2. Define the field schema that real extraction will target
3. Validate that the context serialization handles new categories

Think of it like building a prototype with dummy data — we're defining the "shape" of schedule data so everything downstream is ready when real extraction comes.

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| **Wait for real PDF extraction** | Real data | Delays UI/chatbot testing, bigger scope | We need to validate the data model first |
| **Add schedules to database schema** | More structured | Over-engineering for mock data | Current schema is flexible enough (category + field_key) |
| **Separate schedule tables** | Cleaner data model | More complex joins, migrations | Single `extracted_fields` table is simpler |

The current `extracted_fields` table with `category` and `field_key` columns can handle schedule data without schema changes.

## Task List

- 🟢 **Define schedule field schemas** — Document fields for each schedule
  - 🟢 Schedule A (itemized deductions) field definitions
  - 🟢 Schedule C (self-employment) field definitions
  - 🟢 Schedule D (capital gains) field definitions
- 🟢 **Extend mockExtraction.ts** — Generate schedule fields
  - 🟢 Add `generateScheduleA()` helper function
  - 🟢 Add `generateScheduleC()` helper function
  - 🟢 Add `generateScheduleD()` helper function
  - 🟢 Randomly include schedules based on mock "taxpayer profile"
- 🟢 **Update taxContext.ts** — Handle new categories
  - 🟢 Add category labels for schedule_a, schedule_c, schedule_d
  - 🟢 Add categories to display order
- 🟢 **Update test fixtures** — Add schedule field helpers
  - 🟢 Add `makeScheduleAFields()` fixture
  - 🟢 Add `makeScheduleCFields()` fixture
  - 🟢 Add `makeScheduleDFields()` fixture
- 🟢 **Add tests** — Verify schedule serialization
- 🟢 **Run full test suite** — Ensure no regressions (112 tests passing)

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### mockExtraction.ts — Adding Schedule Generation

**Current state:**
```typescript
export function mockExtract(filename: string) {
  // Only generates Form 1040 fields
  return {
    year,
    filingStatus: "Single",
    fields: [/* 10 Form 1040 fields */],
  };
}
```

**After this change:**
```typescript
export function mockExtract(filename: string) {
  const form1040Fields = generateForm1040Fields(...);

  // Randomly add schedules based on "taxpayer profile"
  const scheduleFields: Field[] = [];

  if (shouldHaveItemizedDeductions(totalIncome)) {
    scheduleFields.push(...generateScheduleA(year));
  }
  if (shouldHaveSelfEmployment()) {
    scheduleFields.push(...generateScheduleC(year));
  }
  if (shouldHaveCapitalGains()) {
    scheduleFields.push(...generateScheduleD(year));
  }

  return {
    year,
    filingStatus,
    fields: [...form1040Fields, ...scheduleFields],
  };
}
```

**Why:** This simulates real-world variety — not every taxpayer has every schedule.

### New Categories for Schedules

**taxContext.ts additions:**
```typescript
const CATEGORY_LABELS: Record<string, string> = {
  // ... existing categories ...
  schedule_a: "Schedule A (Itemized Deductions)",
  schedule_c: "Schedule C (Self-Employment)",
  schedule_d: "Schedule D (Capital Gains/Losses)",
};

const CATEGORY_ORDER: string[] = [
  // ... existing order ...
  "schedule_a",
  "schedule_c",
  "schedule_d",
];
```

## Implementation Details

### Schedule A Fields (Itemized Deductions)

```typescript
function generateScheduleA(year: number): Field[] {
  return [
    { key: "sched_a_medical", label: "Medical and dental expenses", category: "schedule_a", lineNumber: "1" },
    { key: "sched_a_salt", label: "State and local taxes (SALT)", category: "schedule_a", lineNumber: "5d" },
    { key: "sched_a_mortgage_interest", label: "Home mortgage interest", category: "schedule_a", lineNumber: "8a" },
    { key: "sched_a_charity", label: "Gifts to charity", category: "schedule_a", lineNumber: "11" },
    { key: "sched_a_total", label: "Total itemized deductions", category: "schedule_a", lineNumber: "17" },
  ];
}
```

### Schedule C Fields (Self-Employment)

```typescript
function generateScheduleC(year: number): Field[] {
  return [
    { key: "sched_c_gross_receipts", label: "Gross receipts or sales", category: "schedule_c", lineNumber: "1" },
    { key: "sched_c_cogs", label: "Cost of goods sold", category: "schedule_c", lineNumber: "4" },
    { key: "sched_c_gross_profit", label: "Gross profit", category: "schedule_c", lineNumber: "5" },
    { key: "sched_c_expenses", label: "Total expenses", category: "schedule_c", lineNumber: "28" },
    { key: "sched_c_net_profit", label: "Net profit (or loss)", category: "schedule_c", lineNumber: "31" },
  ];
}
```

### Schedule D Fields (Capital Gains)

```typescript
function generateScheduleD(year: number): Field[] {
  return [
    { key: "sched_d_short_term_gain", label: "Short-term capital gain/loss", category: "schedule_d", lineNumber: "7" },
    { key: "sched_d_long_term_gain", label: "Long-term capital gain/loss", category: "schedule_d", lineNumber: "15" },
    { key: "sched_d_net_gain", label: "Net capital gain (or loss)", category: "schedule_d", lineNumber: "16" },
    { key: "sched_d_carryover", label: "Capital loss carryover", category: "schedule_d", lineNumber: "21" },
  ];
}
```

### Data Flow

```
User uploads PDF
    ↓
mockExtract() generates:
  - Form 1040 fields (always)
  - Schedule A fields (if itemizing)
  - Schedule C fields (if self-employed)
  - Schedule D fields (if investments)
    ↓
Fields stored in extracted_fields table
    ↓
buildTaxContext() serializes ALL fields by category
    ↓
Chatbot can answer: "What were my charitable contributions?"
```

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/db/mockExtraction.ts` | Add schedule generation functions |
| Modify | `app/src/services/taxContext.ts` | Add schedule category labels and order |
| Modify | `app/src/types/tax.ts` | Add schedule categories to FieldCategory type |
| Modify | `app/src/test/fixtures.ts` | Add schedule field fixtures |
| Modify | `app/src/services/__tests__/taxContext.test.ts` | Add schedule serialization tests |

## Testing Strategy

### What to Test
- **Schedule A serialization** — Verify itemized deductions appear correctly
- **Schedule C serialization** — Verify self-employment income appears
- **Schedule D serialization** — Verify capital gains appear
- **Mixed schedules** — Verify multiple schedules display in correct order
- **Empty schedules** — Verify graceful handling when no schedules present

### How to Verify
1. Run tests: `cd app && npm test`
2. Launch app, upload a PDF, open chatbot
3. Ask: "Did I have any self-employment income?"
4. Ask: "What were my itemized deductions?"
5. Verify Claude can answer with schedule-specific details

## Risks & Considerations

- **Context size growth:**
  - *Impact:* More fields = longer LLM context = higher token usage
  - *Mitigation:* Schedules add ~15 fields. Still reasonable for context window.

- **Mock data realism:**
  - *Impact:* Generated values may not be internally consistent
  - *Mitigation:* Add basic validation (e.g., Schedule A total = sum of parts)

## Performance Implications

Minimal. Adding ~15 more fields per return. Serialization remains fast (<1ms).

## Dependencies

- **ROH-13 (complete):** Field serialization must be working — it is.

## Open Questions

None — scope is well-defined.

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
