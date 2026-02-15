# Plan: Add schedule data to charts and visualizations

**Issue:** [ROH-36](https://linear.app/rohanr/issue/ROH-36/add-schedule-data-to-charts-and-visualizations)
**Priority:** Medium
**Status:** Planning

---

## Context

Schedule fields (Schedule 1, A, C) are already being extracted from PDFs and stored in the database. The chatbot can answer questions about them because they flow through the `taxContext` serialization. However, users cannot create charts with schedule data because of a **naming mismatch** between what the chart system expects and what the Python extraction produces.

This issue fixes that mismatch and adds the missing Schedule 1 metrics.

## Summary

The chart system (`AVAILABLE_METRICS` in chart.ts) uses keys like `sched_a_salt` but Python extraction produces `scheda_salt_deduction`. Since `CustomChart.getMetricValue()` looks up values by `field_key`, schedule charts silently return 0. The fix is to update the TypeScript metric definitions to match Python output, not change Python (which would require regenerating all test data).

## Technical Approach

### Why This Approach

Updating `AVAILABLE_METRICS` to match Python output is the cleanest solution because:
1. **No test data regeneration** - Python mappings are deployed and used to generate test PDFs
2. **Single file change** - Only chart.ts needs key updates
3. **Consistent with existing data** - The database already contains fields with `scheda_`, `schedc_`, `sched1_` keys
4. **Low risk** - CustomChart already handles the lookup pattern correctly

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| Update Python mappings | Cleaner naming | Requires regenerating all test PDFs (14 files per persona x 2 personas), updating 21 Python mapping files | Too much churn for a cosmetic change |
| Add a mapping/alias layer | Would work with either naming convention | More code, more complexity, potential for bugs | Over-engineering for a simple fix |
| Keep both naming conventions in AVAILABLE_METRICS | Backwards compatible | Confusing, duplicated entries | Creates maintenance burden |

## Task List

- 🔴 **Update AVAILABLE_METRICS** — Fix Schedule A/C keys to match Python, add Schedule 1
  - 🔴 Change `sched_a_*` to `scheda_*` keys
  - 🔴 Change `sched_c_*` to `schedc_*` keys
  - 🔴 Add `sched1_*` keys for Schedule 1
- 🔴 **Update Claude system prompt** — List corrected metric keys
- 🔴 **Verify charts work** — Test with uploaded returns

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### 1. AVAILABLE_METRICS (chart.ts)

**Current state (broken):**
```typescript
// Keys don't match Python output - charts return 0
sched_a_salt: { label: "SALT", format: "currency", color: "#26c6da" },
sched_c_net_profit: { label: "Net Profit", format: "currency", color: "#7e57c2" },
// Schedule 1 not defined at all
```

**After this change:**
```typescript
// Keys match Python extraction - charts work
scheda_salt_deduction: { label: "SALT", format: "currency", color: "#26c6da" },
schedc_net_profit: { label: "Net Profit", format: "currency", color: "#7e57c2" },
sched1_hsa_deduction: { label: "HSA Contributions", format: "currency", color: "#00bcd4" },
```

**Why:** The `getMetricValue()` function in CustomChart.tsx looks up values by field_key. Python extracts fields with keys like `scheda_salt_deduction`, so the chart metric key must match exactly.

### 2. Claude System Prompt (claude.ts)

The system prompt lists available metrics so Claude can generate valid chart configs. Update the schedule sections to use the corrected keys.

**Current (lines 74-76):**
```
- Schedule A: sched_a_medical, sched_a_salt, sched_a_mortgage_interest, sched_a_charity, sched_a_total
- Schedule C: sched_c_gross_receipts, sched_c_cogs, sched_c_gross_profit, sched_c_expenses, sched_c_net_profit
- Schedule D: sched_d_short_term, sched_d_long_term, sched_d_net, sched_d_carryover
```

**After:**
```
- Schedule A: scheda_medical_deduction, scheda_salt_deduction, scheda_mortgage_interest_1098, scheda_total_charity, scheda_total_itemized
- Schedule C: schedc_gross_receipts, schedc_cogs, schedc_gross_profit, schedc_total_expenses, schedc_net_profit
- Schedule 1: sched1_hsa_deduction, sched1_student_loan_interest, sched1_educator_expenses, sched1_total_adjustments
```

## Implementation Details

### Schedule Metrics Mapping (Python → TypeScript)

**Schedule A (Itemized Deductions):**
| Python field_key | TypeScript metric key | Label |
|-----------------|----------------------|-------|
| `scheda_medical_deduction` | `scheda_medical_deduction` | Medical Expenses |
| `scheda_salt_deduction` | `scheda_salt_deduction` | SALT |
| `scheda_mortgage_interest_1098` | `scheda_mortgage_interest_1098` | Mortgage Interest |
| `scheda_total_charity` | `scheda_total_charity` | Charitable Giving |
| `scheda_total_itemized` | `scheda_total_itemized` | Total Itemized |

**Schedule C (Self-Employment):**
| Python field_key | TypeScript metric key | Label |
|-----------------|----------------------|-------|
| `schedc_gross_receipts` | `schedc_gross_receipts` | Gross Receipts |
| `schedc_cogs` | `schedc_cogs` | Cost of Goods Sold |
| `schedc_gross_profit` | `schedc_gross_profit` | Gross Profit |
| `schedc_total_expenses` | `schedc_total_expenses` | Business Expenses |
| `schedc_net_profit` | `schedc_net_profit` | Net Profit |

**Schedule 1 (Adjustments - NEW):**
| Python field_key | TypeScript metric key | Label |
|-----------------|----------------------|-------|
| `sched1_hsa_deduction` | `sched1_hsa_deduction` | HSA Contributions |
| `sched1_student_loan_interest` | `sched1_student_loan_interest` | Student Loan Interest |
| `sched1_educator_expenses` | `sched1_educator_expenses` | Educator Expenses |
| `sched1_total_adjustments` | `sched1_total_adjustments` | Total Adjustments |

### Data Flow (unchanged)

```
Python extraction → extracted_fields (field_key = "scheda_salt_deduction")
                         ↓
CustomChart.getMetricValue("scheda_salt_deduction") → field.field_value
                         ↓
AVAILABLE_METRICS["scheda_salt_deduction"] → {label, format, color}
                         ↓
                   Recharts rendering
```

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/types/chart.ts` | Update Schedule A/C metric keys, add Schedule 1 |
| Modify | `app/src/services/claude.ts` | Update system prompt metric list |

## Testing Strategy

### What to Test
- Schedule A charts render with real data (SALT, mortgage interest, charity)
- Schedule C charts render with real data (gross receipts, expenses, net profit)
- Schedule 1 charts render with real data (HSA, student loan interest)
- Chatbot correctly generates chart configs with new metric keys

### How to Verify
1. Upload a test PDF with schedule data (alex_chen or maria_garcia personas)
2. Test each schedule via chatbot:
   - "Chart my SALT deductions over time"
   - "Show my charitable giving by year"
   - "Graph my business net profit"
   - "Show my HSA contributions"
3. Verify charts display non-zero values that match the PDF data

```bash
cd app && npm test
```

## Risks & Considerations

- **Old chart configs:** Any saved charts using old metric keys (sched_a_*, sched_c_*) will fail validation and show 0. This is acceptable - users can recreate charts with the chatbot.
  - *Impact:* Minor inconvenience for any alpha testers with cached charts
  - *Mitigation:* This is a pre-release app; no production data at risk

- **Schedule D unchanged:** Schedule D metrics are listed in AVAILABLE_METRICS but Python mappings don't include Schedule D yet. Leave Schedule D as-is (future work).

## Not In Scope

- Adding Schedule D extraction (separate issue)
- Pre-built schedule widgets for the registry (custom charts via chatbot suffice)
- Extending `buildSummary()` with schedule fields (CustomChart handles field lookup directly)

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
