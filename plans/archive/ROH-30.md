# Plan: Custom Chart Creation via Chatbot

**Issue:** [ROH-30](https://linear.app/rohanr/issue/ROH-30/custom-chart-creation-via-chatbot)
**Priority:** High
**Status:** Implemented

---

## Context

Users can currently view fixed widgets (Key Numbers table, Year-over-Year chart), but have no way to create custom visualizations. The chatbot can answer questions about tax data but cannot generate visual output. This feature connects the conversational interface to the visualization layer, letting users describe charts in natural language and see them instantly.

## Summary

When users ask the chatbot to create a chart, Claude will detect the intent, select an appropriate chart type, and embed a JSON configuration in its response. The frontend parses this config, creates a dynamic chart widget, and displays it at the top of the dashboard. Charts are session-only (no persistence) and can be removed by the user.

---

## Technical Approach

### Why This Approach

We use **embedded JSON in Claude's text response** rather than tool use because:
1. Current streaming implementation works unchanged
2. No architectural changes to the API client
3. Simple regex parsing after streaming completes
4. Graceful fallback if parsing fails (user just sees text response)

Charts live in **React state** (not the static widget registry) because:
1. Dynamic creation/removal without modifying registry
2. Session-only scope is appropriate for exploratory visualizations
3. No database schema changes needed

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| Claude tool use | Structured output guaranteed | Requires streaming architecture changes, more complex error handling | Over-engineering for MVP |
| Persist charts to SQLite | Charts survive sessions | Schema migration, CRUD operations, sync complexity | Can add later if users want it |
| Generate React components dynamically | Maximum flexibility | Security concerns, eval complexity | Overkill for 4 chart types |

---

## Task List

- ✅ **Create type definitions** — New `types/chart.ts` with ChartConfig, MetricDefinition, validation
- ✅ **Update Claude service** — Add chart creation instructions to system prompt, add parsing functions
- ✅ **Update ChatbotPanel** — Detect chart configs in responses, call callback to create chart
- ✅ **Create CustomChart component** — Recharts-based component supporting bar/line/pie/stacked_bar
- ✅ **Update Dashboard** — Accept and render custom charts at top of widget stack
- ✅ **Update App.tsx** — State management for custom charts, wire callbacks
- ✅ **Add CSS styles** — Custom chart styling with accent border and remove button
- ✅ **Write tests** — Unit tests for parsing, component tests for chart rendering

---

## Implementation Details

### 1. Type Definitions

**File:** `app/src/types/chart.ts` (NEW)

```typescript
export type ChartType = "bar" | "line" | "pie" | "stacked_bar";

export interface ChartConfig {
  id: string;
  type: ChartType;
  title: string;
  metrics: string[];
  createdAt: Date;
}

export interface MetricDefinition {
  label: string;
  format: "currency" | "percent" | "number";
  color: string;
}

// Whitelist of chartable metrics from ReturnSummary
export const AVAILABLE_METRICS: Record<string, MetricDefinition> = {
  total_income: { label: "Total Income", format: "currency", color: "#ff4700" },
  agi: { label: "AGI", format: "currency", color: "#ff8c42" },
  taxable_income: { label: "Taxable Income", format: "currency", color: "#ffaa00" },
  total_tax: { label: "Total Tax", format: "currency", color: "#ff6b6b" },
  total_payments: { label: "Total Payments", format: "currency", color: "#4ade80" },
  refund: { label: "Refund", format: "currency", color: "#4ade80" },
  amount_owed: { label: "Amount Owed", format: "currency", color: "#ffaa00" },
  effective_tax_rate: { label: "Effective Tax Rate", format: "percent", color: "#8b5cf6" },
};

export function isValidMetric(key: string): boolean {
  return key in AVAILABLE_METRICS;
}
```

### 2. Claude Service Updates

**File:** `app/src/services/claude.ts`

Add to system prompt (after existing guidelines):

```
## Chart Creation

When the user asks to create, show, or visualize a chart:

1. Choose the appropriate chart type:
   - Single metric over multiple years → "bar"
   - Composition/share of a single value → "pie" (NEVER for time comparisons)
   - Multiple metrics over time → "line"
   - Stackable components over time → "stacked_bar"

2. Available metrics: total_income, agi, taxable_income, total_tax,
   total_payments, refund, amount_owed, effective_tax_rate

3. Include this JSON block in your response:

\`\`\`chart-config
{"type": "bar", "title": "Total Tax Over Time", "metrics": ["total_tax"]}
\`\`\`

4. If requested metrics aren't available, explain what IS available.
```

Add parsing functions:

```typescript
export function parseChartConfig(response: string): ChartConfig | null {
  const match = response.match(/```chart-config\n([\s\S]*?)\n```/);
  if (!match) return null;

  try {
    const parsed = JSON.parse(match[1]);
    if (!parsed.type || !parsed.title || !Array.isArray(parsed.metrics)) return null;
    if (!["bar", "line", "pie", "stacked_bar"].includes(parsed.type)) return null;
    if (!parsed.metrics.every(isValidMetric)) return null;

    return { id: crypto.randomUUID(), ...parsed, createdAt: new Date() };
  } catch {
    return null;
  }
}

export function stripChartConfig(response: string): string {
  return response.replace(/```chart-config\n[\s\S]*?\n```\n?/, "").trim();
}
```

### 3. ChatbotPanel Updates

**File:** `app/src/components/Chatbot/ChatbotPanel.tsx`

Add prop:
```typescript
export interface ChatbotPanelProps {
  // ... existing
  onCreateChart: (config: ChartConfig) => void;
}
```

In `handleSendMessage`, after streaming completes (line ~74):
```typescript
const finalContent = streamingContentRef.current;

// Check for chart creation
const { parseChartConfig, stripChartConfig } = await import("../../services/claude");
const chartConfig = parseChartConfig(finalContent);
if (chartConfig) {
  onCreateChart(chartConfig);
}

// Display content without JSON block
const displayContent = stripChartConfig(finalContent);
```

### 4. CustomChart Component

**File:** `app/src/widgets/CustomChart.tsx` (NEW)

Single component rendering bar/line/pie/stacked_bar based on `config.type`:
- Uses Recharts (BarChart, LineChart, PieChart)
- Dark theme styling matching existing charts
- Remove button (X) calls `onRemove` prop
- "Custom" badge to distinguish from built-in widgets

Key patterns from existing `YearOverYearChart.tsx`:
- `ResponsiveContainer` wrapper
- Tooltip with `backgroundColor: "#1e1c18"`, `border: "1px solid #3d3831"`
- Grid stroke: `#3d3831`
- Axis tick fill: `#cccccc`

### 5. Dashboard Updates

**File:** `app/src/components/Dashboard.tsx`

```typescript
interface DashboardProps {
  // ... existing
  customCharts: ChartConfig[];
  onRemoveChart: (id: string) => void;
}

// Render custom charts FIRST (at top):
{customCharts.map((chart) => (
  <section key={chart.id} className="widget-section widget-section--custom">
    <h2 className="widget-title">{chart.title}</h2>
    <CustomChart config={chart} summaries={summaries} onRemove={() => onRemoveChart(chart.id)} />
  </section>
))}
// Then render built-in widgets from registry
```

### 6. App.tsx State Management

**File:** `app/src/App.tsx`

```typescript
const [customCharts, setCustomCharts] = useState<ChartConfig[]>([]);

const handleCreateChart = useCallback((config: ChartConfig) => {
  setCustomCharts((prev) => [config, ...prev]);  // Add to front (top)
}, []);

const handleRemoveChart = useCallback((id: string) => {
  setCustomCharts((prev) => prev.filter((c) => c.id !== id));
}, []);
```

Pass to `ChatbotPanel` and `Dashboard`.

### 7. CSS Styles

**File:** `app/src/App.css`

```css
.widget-section--custom {
  border-color: var(--accent);
}

.custom-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.custom-chart-badge {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--accent);
  background: rgba(255, 71, 0, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.custom-chart-remove {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
}

.custom-chart-remove:hover {
  color: var(--danger);
}
```

---

## Files Created/Modified

| Action | File | Purpose |
|--------|------|---------|
| Create | `app/src/types/chart.ts` | Type definitions, metric whitelist |
| Modify | `app/src/services/claude.ts` | System prompt update, parsing functions |
| Modify | `app/src/components/Chatbot/ChatbotPanel.tsx` | Chart detection, callback |
| Create | `app/src/widgets/CustomChart.tsx` | Configurable chart component |
| Modify | `app/src/components/Dashboard.tsx` | Render custom charts at top |
| Modify | `app/src/App.tsx` | State management, wiring |
| Modify | `app/src/App.css` | Custom chart styles |
| Create | `app/src/services/__tests__/chartParsing.test.ts` | Parsing tests |
| Create | `app/src/widgets/__tests__/CustomChart.test.tsx` | Component tests |

---

## Testing Strategy

### What to Test
- `parseChartConfig` correctly extracts valid configs and rejects invalid ones
- `stripChartConfig` removes JSON block from display text
- `CustomChart` renders each chart type (bar, line, pie, stacked_bar)
- Remove button calls `onRemoveChart` callback
- Dashboard renders custom charts above built-in widgets

### Manual Verification
1. Run `cd app && npm run dev`
2. Upload test returns (Alex Chen or Maria Garcia)
3. In chatbot, ask: "Show me a bar chart of my total tax over time"
4. Verify chart appears at top of dashboard with "Custom" badge
5. Click X to remove chart
6. Ask: "Create a pie chart comparing my income and tax" — verify Claude explains this isn't valid (pie not for comparison)
7. Ask: "Chart my cryptocurrency gains" — verify Claude explains this metric isn't available

```bash
cd app && npm test
```

---

## Risks & Considerations

- **Claude response consistency:** JSON formatting may vary. Parser is lenient; on failure, user sees normal text response (graceful degradation).

- **Streaming timing:** Chart config detected after streaming completes. Brief delay before chart appears is acceptable UX.

- **Metric gaps:** Only 8 metrics available initially. Users may request metrics we don't have (e.g., "capital gains"). Claude instructed to explain limitations.

---

## Open Questions

None — requirements are clear from the Linear issue.

---

*Plan created for ROH-30. Implemented 2026-02-14.*
