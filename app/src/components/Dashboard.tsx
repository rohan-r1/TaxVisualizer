import { widgetRegistry } from "../widgets/registry";
import type { TaxReturn, ExtractedField, ReturnSummary } from "../types/tax";

interface DashboardProps {
  returns: TaxReturn[];
  fields: Record<number, ExtractedField[]>;
  summaries: ReturnSummary[];
}

export function Dashboard({ returns, fields, summaries }: DashboardProps) {
  if (returns.length === 0) {
    return (
      <div className="empty-state">
        <h2>No tax returns uploaded yet</h2>
        <p>Upload a tax return PDF to get started.</p>
      </div>
    );
  }

  const visibleWidgets = widgetRegistry.filter(
    (w) => returns.length >= (w.minReturns ?? 1)
  );

  return (
    <div className="dashboard">
      {visibleWidgets.map((widget) => (
        <section key={widget.id} className="widget-section">
          <h2 className="widget-title">{widget.title}</h2>
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
