import type { WidgetConfig } from "../types/tax";
import { KeyNumbersWidget } from "./KeyNumbersWidget";
import { YearOverYearChart } from "./YearOverYearChart";

/**
 * Widget Registry
 *
 * To add a new widget:
 * 1. Create a component that accepts WidgetProps
 * 2. Add it to this array
 *
 * That's it. The dashboard renders all registered widgets automatically.
 */
export const widgetRegistry: WidgetConfig[] = [
  {
    id: "key-numbers",
    title: "Key Numbers",
    component: KeyNumbersWidget,
    minReturns: 1,
  },
  {
    id: "year-over-year",
    title: "Year-over-Year Comparison",
    component: YearOverYearChart,
    minReturns: 2,
  },
];
