import type { TaxReturn, ExtractedField, ReturnSummary } from "../types/tax";

/** Display labels for field categories */
const CATEGORY_LABELS: Record<string, string> = {
  income: "Income Breakdown",
  adjustments: "Adjustments to Income",
  deductions: "Deductions",
  tax_computation: "Tax Computation",
  credits: "Credits",
  payments: "Payments & Withholding",
  refund_owed: "Refund or Amount Owed",
  filing_info: "Filing Information",
  schedule_1: "Schedule 1 (Additional Income & Adjustments)",
  schedule_2: "Schedule 2 (Additional Taxes)",
  schedule_a: "Schedule A (Itemized Deductions)",
  schedule_c: "Schedule C (Self-Employment)",
  schedule_d: "Schedule D (Capital Gains/Losses)",
};

/** Preferred category display order */
const CATEGORY_ORDER: string[] = [
  "filing_info",
  "income",
  "adjustments",
  "schedule_1",
  "schedule_2",
  "deductions",
  "tax_computation",
  "credits",
  "payments",
  "refund_owed",
  "schedule_a",
  "schedule_c",
  "schedule_d",
];

/**
 * Build a context string from tax data for LLM consumption.
 * Includes both summaries and detailed field data for comprehensive Q&A.
 */
export function buildTaxContext(
  returns: TaxReturn[],
  fields: Record<number, ExtractedField[]>,
  summaries: ReturnSummary[]
): string {
  if (returns.length === 0) {
    return "No tax returns have been uploaded yet.";
  }

  const parts: string[] = [];

  // Add summary information for each year
  parts.push("## Tax Return Summaries\n");

  const sortedSummaries = [...summaries].sort((a, b) => b.tax_year - a.tax_year);

  for (const summary of sortedSummaries) {
    parts.push(`### Tax Year ${summary.tax_year}`);
    parts.push(`- Filing Status: ${summary.filing_status}`);
    if (summary.total_income !== null) {
      parts.push(`- Total Income: ${formatCurrency(summary.total_income)}`);
    }
    if (summary.agi !== null) {
      parts.push(`- Adjusted Gross Income (AGI): ${formatCurrency(summary.agi)}`);
    }
    if (summary.taxable_income !== null) {
      parts.push(`- Taxable Income: ${formatCurrency(summary.taxable_income)}`);
    }
    if (summary.total_tax !== null) {
      parts.push(`- Total Tax: ${formatCurrency(summary.total_tax)}`);
    }
    if (summary.effective_tax_rate !== null) {
      parts.push(`- Effective Tax Rate: ${summary.effective_tax_rate.toFixed(2)}%`);
    }
    if (summary.total_payments !== null) {
      parts.push(`- Total Payments/Withholding: ${formatCurrency(summary.total_payments)}`);
    }
    if (summary.refund !== null && summary.refund > 0) {
      parts.push(`- Refund: ${formatCurrency(summary.refund)}`);
    }
    if (summary.amount_owed !== null && summary.amount_owed > 0) {
      parts.push(`- Amount Owed: ${formatCurrency(summary.amount_owed)}`);
    }
    parts.push("");
  }

  // Add year-over-year comparisons if multiple years
  if (sortedSummaries.length > 1) {
    parts.push("## Year-over-Year Changes\n");

    for (let i = 0; i < sortedSummaries.length - 1; i++) {
      const current = sortedSummaries[i];
      const previous = sortedSummaries[i + 1];

      parts.push(`### ${previous.tax_year} → ${current.tax_year}`);

      if (current.total_income !== null && previous.total_income !== null) {
        const change = calculateChange(previous.total_income, current.total_income);
        parts.push(`- Income: ${change}`);
      }

      if (current.total_tax !== null && previous.total_tax !== null) {
        const change = calculateChange(previous.total_tax, current.total_tax);
        parts.push(`- Total Tax: ${change}`);
      }

      if (current.effective_tax_rate !== null && previous.effective_tax_rate !== null) {
        const diff = current.effective_tax_rate - previous.effective_tax_rate;
        const direction = diff > 0 ? "increased" : diff < 0 ? "decreased" : "unchanged";
        parts.push(`- Effective Rate: ${direction} by ${Math.abs(diff).toFixed(2)} percentage points`);
      }

      parts.push("");
    }
  }

  // Add detailed field breakdown
  const detailedSection = serializeDetailedFields(fields, returns);
  if (detailedSection) {
    parts.push(detailedSection);
  }

  // Add lifetime totals
  const lifetimeTax = sortedSummaries.reduce((sum, s) => sum + (s.total_tax ?? 0), 0);
  const lifetimeRefunds = sortedSummaries.reduce((sum, s) => sum + (s.refund ?? 0), 0);
  const lifetimeOwed = sortedSummaries.reduce((sum, s) => sum + (s.amount_owed ?? 0), 0);

  parts.push("## Lifetime Totals\n");
  parts.push(`- Years of data: ${sortedSummaries.length}`);
  parts.push(`- Total tax paid: ${formatCurrency(lifetimeTax)}`);
  parts.push(`- Total refunds received: ${formatCurrency(lifetimeRefunds)}`);
  if (lifetimeOwed > 0) {
    parts.push(`- Total additional payments: ${formatCurrency(lifetimeOwed)}`);
  }

  return parts.join("\n");
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function calculateChange(previous: number, current: number): string {
  if (previous === 0) return "N/A (no previous data)";

  const diff = current - previous;
  const pctChange = ((diff / previous) * 100).toFixed(1);
  const direction = diff > 0 ? "increased" : diff < 0 ? "decreased" : "unchanged";
  const diffStr = formatCurrency(Math.abs(diff));

  return `${direction} by ${diffStr} (${diff > 0 ? "+" : ""}${pctChange}%)`;
}

/**
 * Serialize detailed extracted fields for LLM context.
 * Groups fields by category and includes line numbers and confidence warnings.
 */
function serializeDetailedFields(
  fields: Record<number, ExtractedField[]>,
  returns: TaxReturn[]
): string {
  // Check if we have any fields to serialize
  const hasFields = returns.some((ret) => (fields[ret.id] || []).length > 0);
  if (!hasFields) {
    return "";
  }

  const sections: string[] = ["## Detailed Breakdown by Year\n"];

  // Sort returns by year descending
  const sortedReturns = [...returns].sort((a, b) => b.tax_year - a.tax_year);

  for (const ret of sortedReturns) {
    const returnFields = fields[ret.id] || [];
    if (returnFields.length === 0) continue;

    sections.push(`### ${ret.tax_year} Tax Return Details`);

    // Group fields by category
    const byCategory = groupFieldsByCategory(returnFields);

    // Output fields in category order
    for (const category of CATEGORY_ORDER) {
      const catFields = byCategory[category];
      if (!catFields || catFields.length === 0) continue;

      const categoryLabel = CATEGORY_LABELS[category] || category;
      sections.push(`\n**${categoryLabel}:**`);

      for (const field of catFields) {
        const lineRef = field.line_number ? ` (Line ${field.line_number})` : "";
        const value = formatFieldValue(field.field_value, field.field_type);
        sections.push(`- ${field.field_label}${lineRef}: ${value}`);
      }
    }

    // Flag low-confidence items (confidence < 0.95)
    const lowConfidence = returnFields.filter((f) => f.confidence < 0.95);
    if (lowConfidence.length > 0) {
      sections.push("\n⚠️ Low confidence items (may need review):");
      for (const f of lowConfidence) {
        sections.push(
          `- ${f.field_label}: ${(f.confidence * 100).toFixed(0)}% confidence`
        );
      }
    } else {
      sections.push("\n⚠️ Low confidence items: None");
    }

    sections.push("");
  }

  return sections.join("\n");
}

/**
 * Group fields by their category.
 */
function groupFieldsByCategory(
  fields: ExtractedField[]
): Record<string, ExtractedField[]> {
  const grouped: Record<string, ExtractedField[]> = {};

  for (const field of fields) {
    const category = field.category || "other";
    if (!grouped[category]) {
      grouped[category] = [];
    }
    grouped[category].push(field);
  }

  return grouped;
}

/**
 * Format a field value based on its type.
 */
function formatFieldValue(value: string | null, fieldType: string): string {
  if (value === null || value === "") {
    return "Not specified";
  }

  // Handle currency types
  if (fieldType === "currency" || fieldType === "money") {
    const numValue = parseFloat(value.replace(/[^0-9.-]/g, ""));
    if (!isNaN(numValue)) {
      return formatCurrency(numValue);
    }
  }

  // Handle percentage types
  if (fieldType === "percentage" || fieldType === "percent") {
    const numValue = parseFloat(value);
    if (!isNaN(numValue)) {
      return `${numValue.toFixed(2)}%`;
    }
  }

  return value;
}
