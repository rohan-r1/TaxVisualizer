import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { ChartConfig } from "../types/chart";
import type { ReturnSummary, ExtractedField } from "../types/tax";
import { AVAILABLE_METRICS } from "../types/chart";

interface CustomChartProps {
  config: ChartConfig;
  summaries: ReturnSummary[];
  fields: Record<number, ExtractedField[]>;
  returnYears: Record<number, number>; // returnId -> tax_year mapping
}

function formatValue(value: number, format: "currency" | "percent" | "number"): string {
  if (format === "currency") {
    if (Math.abs(value) >= 1000) {
      return `$${(value / 1000).toFixed(0)}k`;
    }
    return `$${value.toFixed(0)}`;
  }
  if (format === "percent") {
    return `${(value * 100).toFixed(1)}%`;
  }
  return value.toLocaleString();
}

function formatTooltipValue(value: number, format: "currency" | "percent" | "number"): string {
  if (format === "currency") {
    return value.toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
    });
  }
  if (format === "percent") {
    return `${(value * 100).toFixed(2)}%`;
  }
  return value.toLocaleString();
}

const TOOLTIP_STYLE = {
  backgroundColor: "#1e1c18",
  border: "1px solid #3d3831",
  borderRadius: 8,
};

const TOOLTIP_ITEM_STYLE = {
  color: "#ffffff",
};

const TOOLTIP_LABEL_STYLE = {
  color: "#cccccc",
};

export function CustomChart({ config, summaries, fields, returnYears }: CustomChartProps) {
  // Sort summaries by year
  const sortedSummaries = [...summaries].sort((a, b) => a.tax_year - b.tax_year);

  // Build fields lookup by year for quick access
  const fieldsByYear: Record<number, ExtractedField[]> = {};
  for (const [returnId, fieldList] of Object.entries(fields)) {
    const year = returnYears[Number(returnId)];
    if (year) {
      fieldsByYear[year] = fieldList;
    }
  }

  // Helper to get metric value - checks summaries first, then extracted fields
  const getMetricValue = (year: number, metric: string): number => {
    // Check if it's a summary field
    const summary = sortedSummaries.find((s) => s.tax_year === year);
    if (summary && metric in summary) {
      const val = summary[metric as keyof ReturnSummary];
      if (typeof val === "number") return val;
    }

    // Check extracted fields
    const yearFields = fieldsByYear[year];
    if (yearFields) {
      const field = yearFields.find((f) => f.field_key === metric);
      if (field && field.field_value !== null) {
        const parsed = parseFloat(field.field_value);
        if (!isNaN(parsed)) return parsed;
      }
    }

    return 0;
  };

  // Build data for charts
  const data = sortedSummaries.map((s) => {
    const point: Record<string, string | number> = { year: s.tax_year.toString() };
    for (const metric of config.metrics) {
      const metricDef = AVAILABLE_METRICS[metric];
      if (metricDef) {
        point[metricDef.label] = getMetricValue(s.tax_year, metric);
      }
    }
    return point;
  });

  // For pie chart, use single year if specified, otherwise aggregate across years
  const pieData = config.metrics.map((metric) => {
    const metricDef = AVAILABLE_METRICS[metric];
    let value: number;

    if (config.year) {
      // Single year specified - use just that year's value
      value = getMetricValue(config.year, metric);
    } else {
      // No year specified - aggregate across all years
      value = sortedSummaries.reduce((sum, s) => {
        return sum + getMetricValue(s.tax_year, metric);
      }, 0);
    }

    return {
      name: metricDef?.label || metric,
      value,
      color: metricDef?.color || "#888888",
    };
  });

  const renderChart = () => {
    switch (config.type) {
      case "bar":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#3d3831" />
              <XAxis dataKey="year" stroke="#888880" tick={{ fill: "#cccccc" }} />
              <YAxis
                tickFormatter={(v) => formatValue(v, config.metrics[0] ? AVAILABLE_METRICS[config.metrics[0]]?.format || "number" : "number")}
                stroke="#888880"
                tick={{ fill: "#cccccc" }}
              />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                itemStyle={TOOLTIP_ITEM_STYLE}
                labelStyle={TOOLTIP_LABEL_STYLE}
                formatter={(value) => {
                  const format = config.metrics[0] ? AVAILABLE_METRICS[config.metrics[0]]?.format || "number" : "number";
                  return formatTooltipValue(value as number, format);
                }}
              />
              <Legend wrapperStyle={{ color: "#cccccc" }} />
              {config.metrics.map((metric) => {
                const metricDef = AVAILABLE_METRICS[metric];
                return (
                  <Bar
                    key={metric}
                    dataKey={metricDef?.label || metric}
                    fill={metricDef?.color || "#888888"}
                    radius={[4, 4, 0, 0]}
                  />
                );
              })}
            </BarChart>
          </ResponsiveContainer>
        );

      case "line":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#3d3831" />
              <XAxis dataKey="year" stroke="#888880" tick={{ fill: "#cccccc" }} />
              <YAxis
                tickFormatter={(v) => formatValue(v, config.metrics[0] ? AVAILABLE_METRICS[config.metrics[0]]?.format || "number" : "number")}
                stroke="#888880"
                tick={{ fill: "#cccccc" }}
              />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                itemStyle={TOOLTIP_ITEM_STYLE}
                labelStyle={TOOLTIP_LABEL_STYLE}
                formatter={(value) => {
                  const format = config.metrics[0] ? AVAILABLE_METRICS[config.metrics[0]]?.format || "number" : "number";
                  return formatTooltipValue(value as number, format);
                }}
              />
              <Legend wrapperStyle={{ color: "#cccccc" }} />
              {config.metrics.map((metric) => {
                const metricDef = AVAILABLE_METRICS[metric];
                return (
                  <Line
                    key={metric}
                    type="monotone"
                    dataKey={metricDef?.label || metric}
                    stroke={metricDef?.color || "#888888"}
                    strokeWidth={2.5}
                    dot={{ r: 5, fill: metricDef?.color || "#888888" }}
                    activeDot={{ r: 7 }}
                  />
                );
              })}
            </LineChart>
          </ResponsiveContainer>
        );

      case "pie":
        // Calculate total for percentage threshold
        const pieTotal = pieData.reduce((sum, d) => sum + d.value, 0);

        // Custom label renderer with callout lines - only for slices > 5%
        const renderPieLabel = ({
          cx,
          cy,
          midAngle,
          outerRadius,
          name,
          percent,
          fill,
        }: {
          cx: number;
          cy: number;
          midAngle: number;
          outerRadius: number;
          name: string;
          percent: number;
          fill: string;
        }) => {
          // Hide labels for very small slices (< 5%) to prevent overlap
          if ((percent ?? 0) < 0.05) {
            return null;
          }

          const RADIAN = Math.PI / 180;
          const radius = outerRadius + 30;
          const x = cx + radius * Math.cos(-midAngle * RADIAN);
          const y = cy + radius * Math.sin(-midAngle * RADIAN);
          const textAnchor = x > cx ? "start" : "end";

          return (
            <text
              x={x}
              y={y}
              fill={fill}
              textAnchor={textAnchor}
              dominantBaseline="central"
              fontSize={12}
            >
              {`${name} (${((percent ?? 0) * 100).toFixed(0)}%)`}
            </text>
          );
        };

        // Custom label line renderer - hide for small slices
        const renderLabelLine = (props: {
          percent?: number;
          points?: Array<{ x: number; y: number }>;
        }) => {
          if ((props.percent ?? 0) < 0.05) {
            return null;
          }
          const { points } = props;
          if (!points || points.length < 2) return null;

          return (
            <path
              d={`M${points[0].x},${points[0].y}L${points[1].x},${points[1].y}`}
              stroke="#888880"
              strokeWidth={1}
              fill="none"
            />
          );
        };

        return (
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={renderLabelLine}
                label={renderPieLabel}
                outerRadius={90}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                itemStyle={TOOLTIP_ITEM_STYLE}
                labelStyle={TOOLTIP_LABEL_STYLE}
                formatter={(value, name) => [formatTooltipValue(value as number, "currency"), name]}
              />
              <Legend wrapperStyle={{ color: "#cccccc" }} />
            </PieChart>
          </ResponsiveContainer>
        );

      case "stacked_bar":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#3d3831" />
              <XAxis dataKey="year" stroke="#888880" tick={{ fill: "#cccccc" }} />
              <YAxis
                tickFormatter={(v) => formatValue(v, "currency")}
                stroke="#888880"
                tick={{ fill: "#cccccc" }}
              />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                itemStyle={TOOLTIP_ITEM_STYLE}
                labelStyle={TOOLTIP_LABEL_STYLE}
                formatter={(value) => formatTooltipValue(value as number, "currency")}
              />
              <Legend wrapperStyle={{ color: "#cccccc" }} />
              {config.metrics.map((metric) => {
                const metricDef = AVAILABLE_METRICS[metric];
                return (
                  <Bar
                    key={metric}
                    dataKey={metricDef?.label || metric}
                    stackId="stack"
                    fill={metricDef?.color || "#888888"}
                  />
                );
              })}
            </BarChart>
          </ResponsiveContainer>
        );

      default:
        return <div>Unsupported chart type</div>;
    }
  };

  return (
    <div className="custom-chart">
      {renderChart()}
    </div>
  );
}
