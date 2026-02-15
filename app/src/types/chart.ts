export type ChartType = "bar" | "line" | "pie" | "stacked_bar";

export interface ChartConfig {
  id: string;
  type: ChartType;
  title: string;
  metrics: string[];
  year?: number; // Optional: filter to single year (especially for pie charts)
  createdAt: Date;
}

export interface MetricDefinition {
  label: string;
  format: "currency" | "percent" | "number";
  color: string;
}

/** All chartable metrics - matches all extracted fields */
export const AVAILABLE_METRICS: Record<string, MetricDefinition> = {
  // === Form 1040 - Income ===
  wages: { label: "Wages", format: "currency", color: "#ff4700" },
  taxable_interest: { label: "Taxable Interest", format: "currency", color: "#ff5722" },
  ordinary_dividends: { label: "Ordinary Dividends", format: "currency", color: "#ff6f00" },
  qualified_dividends: { label: "Qualified Dividends", format: "currency", color: "#ff8f00" },
  ira_distributions: { label: "IRA Distributions", format: "currency", color: "#ffa000" },
  pensions: { label: "Pensions & Annuities", format: "currency", color: "#ffb300" },
  social_security: { label: "Social Security", format: "currency", color: "#ffc107" },
  capital_gains: { label: "Capital Gain/Loss", format: "currency", color: "#ffd54f" },
  other_income: { label: "Other Income", format: "currency", color: "#ffe082" },
  total_income: { label: "Total Income", format: "currency", color: "#ff7043" },
  adjustments: { label: "Adjustments", format: "currency", color: "#ff8a65" },
  agi: { label: "AGI", format: "currency", color: "#ff8c42" },
  taxable_income: { label: "Taxable Income", format: "currency", color: "#ffb74d" },

  // === Form 1040 - Deductions ===
  deduction: { label: "Deduction", format: "currency", color: "#81c784" },
  deductions: { label: "Deductions", format: "currency", color: "#66bb6a" },
  standard_deduction: { label: "Standard Deduction", format: "currency", color: "#4caf50" },
  qbi_deduction: { label: "QBI Deduction", format: "currency", color: "#43a047" },
  total_deductions: { label: "Total Deductions", format: "currency", color: "#388e3c" },

  // === Form 1040 - Tax Computation ===
  tax_amount: { label: "Tax", format: "currency", color: "#ef5350" },
  schedule_2_tax: { label: "Schedule 2 Tax", format: "currency", color: "#f44336" },
  tax_before_credits: { label: "Tax Before Credits", format: "currency", color: "#e53935" },
  tax_after_credits: { label: "Tax After Credits", format: "currency", color: "#d32f2f" },
  other_taxes: { label: "Other Taxes", format: "currency", color: "#c62828" },
  total_tax: { label: "Total Tax", format: "currency", color: "#ff6b6b" },

  // === Form 1040 - Credits ===
  child_tax_credit: { label: "Child Tax Credit", format: "currency", color: "#42a5f5" },
  schedule_3_credits: { label: "Schedule 3 Credits", format: "currency", color: "#2196f3" },
  total_credits: { label: "Total Credits", format: "currency", color: "#1e88e5" },

  // === Form 1040 - Payments ===
  federal_withholding: { label: "Federal Withholding", format: "currency", color: "#26a69a" },
  estimated_payments: { label: "Estimated Payments", format: "currency", color: "#009688" },
  other_payments: { label: "Other Payments", format: "currency", color: "#00897b" },
  total_payments: { label: "Total Payments", format: "currency", color: "#4ade80" },

  // === Form 1040 - Refund/Owed ===
  overpaid: { label: "Amount Overpaid", format: "currency", color: "#66bb6a" },
  refund: { label: "Refund", format: "currency", color: "#4caf50" },
  amount_owed: { label: "Amount Owed", format: "currency", color: "#ef5350" },

  // === Computed Metrics ===
  effective_tax_rate: { label: "Effective Tax Rate", format: "percent", color: "#8b5cf6" },

  // === Schedule A - Itemized Deductions ===
  sched_a_medical: { label: "Medical Expenses", format: "currency", color: "#26a69a" },
  sched_a_salt: { label: "SALT", format: "currency", color: "#26c6da" },
  sched_a_mortgage_interest: { label: "Mortgage Interest", format: "currency", color: "#29b6f6" },
  sched_a_charity: { label: "Charitable Giving", format: "currency", color: "#42a5f5" },
  sched_a_total: { label: "Total Itemized", format: "currency", color: "#5c6bc0" },

  // === Schedule C - Self-Employment ===
  sched_c_gross_receipts: { label: "Gross Receipts", format: "currency", color: "#ab47bc" },
  sched_c_cogs: { label: "Cost of Goods Sold", format: "currency", color: "#ba68c8" },
  sched_c_gross_profit: { label: "Gross Profit", format: "currency", color: "#ce93d8" },
  sched_c_expenses: { label: "Business Expenses", format: "currency", color: "#9575cd" },
  sched_c_net_profit: { label: "Net Profit", format: "currency", color: "#7e57c2" },

  // === Schedule D - Capital Gains ===
  sched_d_short_term: { label: "Short-Term Gains", format: "currency", color: "#ffca28" },
  sched_d_long_term: { label: "Long-Term Gains", format: "currency", color: "#ffd54f" },
  sched_d_net: { label: "Net Capital Gain", format: "currency", color: "#ffe082" },
  sched_d_carryover: { label: "Loss Carryover", format: "currency", color: "#fff176" },
};

export function isValidMetric(key: string): boolean {
  return key in AVAILABLE_METRICS;
}

export function isValidChartType(type: string): type is ChartType {
  return ["bar", "line", "pie", "stacked_bar"].includes(type);
}
