# Plan: Give chatbot deeper access to parsed tax return data

**Issue:** [ROH-13](https://linear.app/rohanr/issue/ROH-13/give-chatbot-deeper-access-to-parsed-tax-return-data)
**Priority:** Urgent
**Status:** Complete

---

## Context

The chatbot currently only sees high-level summary data (total income, AGI, total tax, etc.). When users ask detailed questions like "What made up my income?" or "What deductions did I take?", Claude can't answer because `buildTaxContext` ignores the detailed `fields` data it already receives.

**The good news:** The detailed field data already exists in the database and is already passed to `buildTaxContext` — it's just not being serialized into the LLM context. This is a relatively small change with high impact.

**Phase 1 scope (this plan):**
- Make the chatbot aware of all extracted fields, not just summaries
- Structure the context to help Claude answer detailed questions
- No new parsing, no new schedules, no encryption (those are Phase 2+)

## Summary

Modify `buildTaxContext` in `app/src/services/taxContext.ts` to serialize the detailed `fields` data alongside the existing summaries. This gives Claude visibility into individual income components, deductions, credits, and payments — enabling much richer tax conversations.

## Technical Approach

### Why This Approach

The simplest path to impact: we already have the data and the plumbing. The `fields` parameter is passed to `buildTaxContext` but completely ignored. By serializing it, we unlock detailed Q&A without changing the database, parsing, or API integration.

Think of it like having a detailed report in your filing cabinet but only showing the executive summary to your assistant. We're just opening the full report.

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| **On-demand field queries** | Only fetch relevant fields per question | Requires tool-use/function-calling architecture | Over-engineering for current needs |
| **Separate "detailed" chatbot mode** | User controls verbosity | More UI complexity, confusing UX | Users shouldn't have to choose |
| **Store pre-built context in DB** | Faster at chat time | Stale if data changes, more storage | Unnecessary optimization |

Simply expanding `buildTaxContext` is the right balance: minimal change, immediate value, no new complexity.

## Task List

- 🟢 **Enhance buildTaxContext** — Serialize detailed fields into LLM context
  - 🟢 Add `serializeFields()` helper function
  - 🟢 Group fields by category for readability
  - 🟢 Include confidence scores for low-confidence items
  - 🟢 Include line numbers for Form 1040 references
- 🟢 **Update context structure** — Organize for LLM comprehension
  - 🟢 Add "Detailed Breakdown" section after summaries
  - 🟢 Format values consistently (currency, percentages)
- 🟢 **Add tests** — Verify new context format
  - 🟢 Test that fields are serialized correctly
  - 🟢 Test confidence flagging works
- 🟢 **Run full test suite** — Ensure no regressions (105 tests passing)

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### taxContext.ts — Adding Field Serialization

**Current state:**
```typescript
export function buildTaxContext(
  returns: TaxReturn[],
  fields: Record<number, ExtractedField[]>,  // ← IGNORED!
  summaries: ReturnSummary[]
): string {
  // Only uses summaries, never touches fields
  return serializeSummaries(summaries) + yearOverYear + lifetimeTotals;
}
```

**After this change:**
```typescript
export function buildTaxContext(
  returns: TaxReturn[],
  fields: Record<number, ExtractedField[]>,  // ← NOW USED
  summaries: ReturnSummary[]
): string {
  const summarySection = serializeSummaries(summaries);
  const detailSection = serializeDetailedFields(fields, returns);
  const yoySection = serializeYearOverYear(summaries);
  const lifetimeSection = serializeLifetimeTotals(summaries);

  return [summarySection, detailSection, yoySection, lifetimeSection].join('\n\n');
}
```

**Why:** The `fields` data contains line-item details that enable Claude to answer specific questions. Currently wasted.

### New Context Section — Detailed Breakdown

**New section added to context:**
```markdown
## Detailed Breakdown by Year

### 2023 Tax Return Details

**Income Breakdown:**
- Wages, salaries, tips (Line 1a): $85,000
- Total income (Line 9): $92,500

**Adjustments:**
- Adjustments to income (Line 10): $2,500
- Adjusted gross income (Line 11): $90,000

**Deductions:**
- Standard deduction (Line 12): $14,600
- Taxable income (Line 15): $75,400

**Tax Computation:**
- Total tax (Line 24): $12,500

**Payments:**
- Total payments (Line 33): $14,000

**Refund/Amount Owed:**
- Refund (Line 34): $1,500

⚠️ Low confidence items (may need review):
- [None for this return]
```

**Why:** Organizing by category mirrors how the Form 1040 is structured, making it intuitive for both Claude and users who reference their actual returns.

## Implementation Details

### Key Code Changes

**New helper function — serializeDetailedFields:**
```typescript
function serializeDetailedFields(
  fields: Record<number, ExtractedField[]>,
  returns: TaxReturn[]
): string {
  const sections: string[] = ['## Detailed Breakdown by Year'];

  // Sort returns by year descending
  const sortedReturns = [...returns].sort((a, b) => b.tax_year - a.tax_year);

  for (const ret of sortedReturns) {
    const returnFields = fields[ret.id] || [];
    if (returnFields.length === 0) continue;

    sections.push(`### ${ret.tax_year} Tax Return Details`);

    // Group by category
    const byCategory = groupBy(returnFields, 'category');

    for (const [category, catFields] of Object.entries(byCategory)) {
      sections.push(`\n**${formatCategory(category)}:**`);
      for (const field of catFields) {
        const lineRef = field.line_number ? ` (Line ${field.line_number})` : '';
        const value = formatValue(field.field_value, field.field_type);
        sections.push(`- ${field.field_label}${lineRef}: ${value}`);
      }
    }

    // Flag low-confidence items
    const lowConfidence = returnFields.filter(f => f.confidence < 0.95);
    if (lowConfidence.length > 0) {
      sections.push('\n⚠️ Low confidence items (may need review):');
      for (const f of lowConfidence) {
        sections.push(`- ${f.field_label}: ${(f.confidence * 100).toFixed(0)}% confidence`);
      }
    } else {
      sections.push('\n⚠️ Low confidence items: None');
    }
  }

  return sections.join('\n');
}
```

### Data Flow

```
User asks "What made up my income in 2023?"
    ↓
ChatbotPanel calls buildTaxContext(returns, fields, summaries)
    ↓
buildTaxContext now includes:
  - Summary section (existing)
  - NEW: Detailed breakdown section ← fields serialized here
  - YoY changes (existing)
  - Lifetime totals (existing)
    ↓
Claude sees detailed income breakdown
    ↓
Claude responds: "Your 2023 income of $92,500 came from:
  - Wages: $85,000 (Line 1a)
  - Other income: $7,500..."
```

### Category Display Names

```typescript
const CATEGORY_LABELS: Record<string, string> = {
  'income': 'Income Breakdown',
  'adjustments': 'Adjustments to Income',
  'deductions': 'Deductions',
  'tax_computation': 'Tax Computation',
  'credits': 'Credits',
  'payments': 'Payments & Withholding',
  'refund_owed': 'Refund or Amount Owed',
  'filing_info': 'Filing Information',
};
```

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src/services/taxContext.ts` | Add `serializeDetailedFields`, update `buildTaxContext` |
| Modify | `app/src/services/__tests__/taxContext.test.ts` | Add tests for field serialization |

## Testing Strategy

### What to Test
- **Field serialization** — Verify fields are grouped by category and formatted correctly
- **Low confidence flagging** — Verify items with confidence < 0.95 are flagged
- **Empty fields handling** — Verify graceful handling when no fields exist
- **Line number formatting** — Verify "(Line X)" appears when line_number exists

### How to Verify
1. Run tests: `cd app && npm test`
2. Launch app, open chatbot, ask detailed questions:
   - "What made up my income in 2023?"
   - "What deductions did I take?"
   - "What's on Line 11 of my 2023 return?"
3. Verify Claude can now answer with specific line-item details

## Risks & Considerations

- **Context size:**
  - *Impact:* More fields = longer context = higher token usage
  - *Mitigation:* Currently only ~10 fields per return; scales linearly. Monitor if/when we add more fields.

- **Mock data limitations:**
  - *Impact:* Mock extraction only generates 10 fields; chatbot can only discuss those
  - *Mitigation:* This is expected behavior. Phase 2 (enhanced parsing) will add more fields.

## Performance Implications

Minimal. We're adding string concatenation for ~10 fields per return. The serialization is fast (< 1ms) and only happens when the user sends a chat message.

## Dependencies

None — this change is self-contained within the taxContext service.

## Open Questions

None for Phase 1. Future phases will address:
- **Phase 2:** Enhanced parsing for Schedules A, C, D
- **Phase 3:** Encryption at rest with SQLCipher
- **Phase 4:** Real PDF extraction pipeline (replacing mock)

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
