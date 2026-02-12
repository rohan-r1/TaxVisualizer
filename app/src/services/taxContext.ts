import type { TaxReturn, ExtractedField, ReturnSummary } from "../types/tax";

/**
 * Build a context string from tax data for LLM consumption.
 * Prioritizes summaries (always included), with optional detailed fields.
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
