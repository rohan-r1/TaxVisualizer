import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { WidgetProps } from "../types/tax";

const COLORS = {
  income: "#ff4700",
  tax: "#ff6b6b",
  refund: "#4ade80",
  owed: "#ffaa00",
};

function formatDollar(value: number) {
  if (Math.abs(value) >= 1000) {
    return `$${(value / 1000).toFixed(0)}k`;
  }
  return `$${value}`;
}

export function YearOverYearChart({ summaries }: WidgetProps) {
  if (summaries.length < 2) return null;

  const data = [...summaries]
    .sort((a, b) => a.tax_year - b.tax_year)
    .map((s) => ({
      year: s.tax_year.toString(),
      "Total Income": s.total_income ?? 0,
      "Total Tax": s.total_tax ?? 0,
      Refund: s.refund ?? 0,
      "Amount Owed": s.amount_owed ?? 0,
    }));

  return (
    <div className="yoy-chart-widget">
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#3d3831" />
          <XAxis dataKey="year" stroke="#888880" tick={{ fill: "#cccccc" }} />
          <YAxis tickFormatter={formatDollar} stroke="#888880" tick={{ fill: "#cccccc" }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e1c18",
              border: "1px solid #3d3831",
              borderRadius: 8,
              color: "#ffffff",
            }}
            formatter={(value: number) =>
              value.toLocaleString("en-US", {
                style: "currency",
                currency: "USD",
                minimumFractionDigits: 0,
              })
            }
          />
          <Legend wrapperStyle={{ color: "#cccccc" }} />
          <Line type="monotone" dataKey="Total Income" stroke={COLORS.income} strokeWidth={2.5} dot={{ r: 5, fill: COLORS.income }} activeDot={{ r: 7 }} />
          <Line type="monotone" dataKey="Total Tax" stroke={COLORS.tax} strokeWidth={2.5} dot={{ r: 5, fill: COLORS.tax }} activeDot={{ r: 7 }} />
          <Line type="monotone" dataKey="Refund" stroke={COLORS.refund} strokeWidth={2.5} dot={{ r: 5, fill: COLORS.refund }} activeDot={{ r: 7 }} />
          <Line type="monotone" dataKey="Amount Owed" stroke={COLORS.owed} strokeWidth={2.5} dot={{ r: 5, fill: COLORS.owed }} activeDot={{ r: 7 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
