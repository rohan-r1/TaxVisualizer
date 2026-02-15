import { widgetRegistry } from "../widgets/registry";
import { CustomChart } from "../widgets/CustomChart";
import type { TaxReturn, ExtractedField, ReturnSummary } from "../types/tax";
import type { ChartConfig } from "../types/chart";

interface DashboardProps {
  returns: TaxReturn[];
  fields: Record<number, ExtractedField[]>;
  summaries: ReturnSummary[];
  customCharts: ChartConfig[];
  onRemoveChart: (id: string) => void;
  onRemoveWidget: (id: string) => void;
  hiddenWidgets: string[];
}

const CloseIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);

export function Dashboard({ returns, fields, summaries, customCharts, onRemoveChart, onRemoveWidget, hiddenWidgets }: DashboardProps) {
  if (returns.length === 0) {
    return (
      <div className="empty-state">
        <h2>No tax returns uploaded yet</h2>
        <p>Upload a tax return PDF to get started.</p>
      </div>
    );
  }

  // Build returnId -> year mapping for CustomChart
  const returnYears: Record<number, number> = {};
  for (const r of returns) {
    returnYears[r.id] = r.tax_year;
  }

  const visibleWidgets = widgetRegistry.filter(
    (w) => returns.length >= (w.minReturns ?? 1) && !hiddenWidgets.includes(w.id)
  );

  return (
    <div className="dashboard">
      {/* Custom charts appear at the top */}
      {customCharts.map((chart) => (
        <section key={chart.id} className="widget-section widget-section--custom">
          <div className="widget-header">
            <h2 className="widget-title">
              {chart.title}
              <span className="widget-badge">Custom</span>
            </h2>
            <button
              className="widget-close"
              onClick={() => onRemoveChart(chart.id)}
              title="Remove chart"
              aria-label="Remove chart"
            >
              <CloseIcon />
            </button>
          </div>
          <CustomChart
            config={chart}
            summaries={summaries}
            fields={fields}
            returnYears={returnYears}
          />
        </section>
      ))}
      {/* Built-in widgets */}
      {visibleWidgets.map((widget) => (
        <section key={widget.id} className="widget-section">
          <div className="widget-header">
            <h2 className="widget-title">{widget.title}</h2>
            <button
              className="widget-close"
              onClick={() => onRemoveWidget(widget.id)}
              title="Hide widget"
              aria-label="Hide widget"
            >
              <CloseIcon />
            </button>
          </div>
          <widget.component
            returns={returns}
            fields={fields}
            summaries={summaries}
          />
        </section>
      ))}
    </div>
  );
}
