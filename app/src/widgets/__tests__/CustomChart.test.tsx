import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { CustomChart } from "../CustomChart";
import { makeSummary } from "../../test/fixtures";
import type { ChartConfig } from "../../types/chart";

function makeChartConfig(overrides: Partial<ChartConfig> = {}): ChartConfig {
  return {
    id: "test-chart-1",
    type: "bar",
    title: "Test Chart",
    metrics: ["total_tax"],
    createdAt: new Date(),
    ...overrides,
  };
}

describe("CustomChart", () => {
  const defaultSummaries = [
    makeSummary({ tax_year: 2021, total_income: 65000, total_tax: 7000 }),
    makeSummary({ tax_year: 2022, total_income: 75000, total_tax: 8500 }),
    makeSummary({ tax_year: 2023, total_income: 85000, total_tax: 10000 }),
  ];

  const defaultFields = {};
  const defaultReturnYears = { 1: 2021, 2: 2022, 3: 2023 };

  it("renders the chart container", () => {
    const { container } = render(
      <CustomChart
        config={makeChartConfig()}
        summaries={defaultSummaries}
        fields={defaultFields}
        returnYears={defaultReturnYears}
      />
    );

    expect(container.querySelector(".custom-chart")).toBeInTheDocument();
  });

  it("renders a bar chart without crashing", () => {
    const { container } = render(
      <CustomChart
        config={makeChartConfig({ type: "bar" })}
        summaries={defaultSummaries}
        fields={defaultFields}
        returnYears={defaultReturnYears}
      />
    );

    expect(container.querySelector(".custom-chart")).toBeInTheDocument();
  });

  it("renders a line chart without crashing", () => {
    const { container } = render(
      <CustomChart
        config={makeChartConfig({ type: "line" })}
        summaries={defaultSummaries}
        fields={defaultFields}
        returnYears={defaultReturnYears}
      />
    );

    expect(container.querySelector(".custom-chart")).toBeInTheDocument();
  });

  it("renders a pie chart without crashing", () => {
    const { container } = render(
      <CustomChart
        config={makeChartConfig({ type: "pie", metrics: ["total_income", "total_tax"] })}
        summaries={defaultSummaries}
        fields={defaultFields}
        returnYears={defaultReturnYears}
      />
    );

    expect(container.querySelector(".custom-chart")).toBeInTheDocument();
  });

  it("renders a stacked bar chart without crashing", () => {
    const { container } = render(
      <CustomChart
        config={makeChartConfig({ type: "stacked_bar", metrics: ["total_income", "total_tax"] })}
        summaries={defaultSummaries}
        fields={defaultFields}
        returnYears={defaultReturnYears}
      />
    );

    expect(container.querySelector(".custom-chart")).toBeInTheDocument();
  });

  it("handles multiple metrics without crashing", () => {
    const { container } = render(
      <CustomChart
        config={makeChartConfig({ type: "line", metrics: ["total_income", "total_tax", "refund"] })}
        summaries={defaultSummaries}
        fields={defaultFields}
        returnYears={defaultReturnYears}
      />
    );

    expect(container.querySelector(".custom-chart")).toBeInTheDocument();
  });

  it("handles empty summaries", () => {
    const { container } = render(
      <CustomChart
        config={makeChartConfig()}
        summaries={[]}
        fields={defaultFields}
        returnYears={defaultReturnYears}
      />
    );

    expect(container.querySelector(".custom-chart")).toBeInTheDocument();
  });

  it("handles null values in summaries", () => {
    const summariesWithNulls = [
      makeSummary({ tax_year: 2022, total_tax: null }),
      makeSummary({ tax_year: 2023, total_tax: 8500 }),
    ];

    const { container } = render(
      <CustomChart
        config={makeChartConfig()}
        summaries={summariesWithNulls}
        fields={defaultFields}
        returnYears={defaultReturnYears}
      />
    );

    expect(container.querySelector(".custom-chart")).toBeInTheDocument();
  });

  it("sorts summaries by year", () => {
    const unsortedSummaries = [
      makeSummary({ tax_year: 2023 }),
      makeSummary({ tax_year: 2021 }),
      makeSummary({ tax_year: 2022 }),
    ];

    const { container } = render(
      <CustomChart
        config={makeChartConfig()}
        summaries={unsortedSummaries}
        fields={defaultFields}
        returnYears={defaultReturnYears}
      />
    );

    expect(container.querySelector(".custom-chart")).toBeInTheDocument();
  });
});
