import type { WidgetProps, ReturnSummary } from "../types/tax";

function formatCurrency(value: number | null): string {
  if (value === null) return "—";
  return value.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
}

function formatPercent(value: number | null): string {
  if (value === null) return "—";
  return `${value.toFixed(2)}%`;
}

interface MetricRow {
  label: string;
  key: keyof ReturnSummary;
  format: (v: number | null) => string;
}

const metrics: MetricRow[] = [
  { label: "Filing Status", key: "filing_status", format: (v) => v as unknown as string ?? "—" },
  { label: "Total Income", key: "total_income", format: formatCurrency },
  { label: "AGI", key: "agi", format: formatCurrency },
  { label: "Taxable Income", key: "taxable_income", format: formatCurrency },
  { label: "Total Tax", key: "total_tax", format: formatCurrency },
  { label: "Effective Rate", key: "effective_tax_rate", format: formatPercent },
  { label: "Total Payments", key: "total_payments", format: formatCurrency },
  { label: "Refund", key: "refund", format: formatCurrency },
  { label: "Amount Owed", key: "amount_owed", format: formatCurrency },
];

export function KeyNumbersWidget({ summaries }: WidgetProps) {
  if (summaries.length === 0) return null;

  const sorted = [...summaries].sort((a, b) => a.tax_year - b.tax_year);

  return (
    <div className="key-numbers-table">
      <div className="kn-header-row">
        <div className="kn-label-cell" />
        {sorted.map((s) => (
          <div key={s.tax_year} className="kn-year-cell">
            {s.tax_year}
          </div>
        ))}
      </div>
      {metrics.map((m) => (
        <div key={m.key} className="kn-row">
          <div className="kn-label-cell">{m.label}</div>
          {sorted.map((s) => (
            <div key={s.tax_year} className="kn-value-cell">
              {m.key === "filing_status"
                ? (s.filing_status ?? "—")
                : m.format(s[m.key] as number | null)}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
