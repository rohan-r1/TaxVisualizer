import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Dashboard } from "../Dashboard";
import { makeReturn, makeSummary, makeFieldSet, makeMultiYearData } from "../../test/fixtures";

describe("Dashboard", () => {
  const noop = () => {};

  it("shows empty state when no returns", () => {
    render(<Dashboard returns={[]} fields={{}} summaries={[]} customCharts={[]} onRemoveChart={noop} onRemoveWidget={noop} hiddenWidgets={[]} />);

    expect(screen.getByText("No tax returns uploaded yet")).toBeInTheDocument();
    expect(
      screen.getByText("Upload a tax return PDF to get started.")
    ).toBeInTheDocument();
  });

  it("renders Key Numbers widget with 1 return", () => {
    const returns = [makeReturn({ id: 1 })];
    const fields = { 1: makeFieldSet(1) };
    const summaries = [makeSummary({ tax_year: 2023 })];

    render(
      <Dashboard returns={returns} fields={fields} summaries={summaries} customCharts={[]} onRemoveChart={noop} onRemoveWidget={noop} hiddenWidgets={[]} />
    );

    expect(screen.getByText("Key Numbers")).toBeInTheDocument();
  });

  it("does not render YoY chart with only 1 return", () => {
    const returns = [makeReturn({ id: 1 })];
    const fields = { 1: makeFieldSet(1) };
    const summaries = [makeSummary()];

    render(
      <Dashboard returns={returns} fields={fields} summaries={summaries} customCharts={[]} onRemoveChart={noop} onRemoveWidget={noop} hiddenWidgets={[]} />
    );

    expect(
      screen.queryByText("Year-over-Year Comparison")
    ).not.toBeInTheDocument();
  });

  it("renders both widgets with 2+ returns", () => {
    const { returns, fields, summaries } = makeMultiYearData();

    render(
      <Dashboard returns={returns} fields={fields} summaries={summaries} customCharts={[]} onRemoveChart={noop} onRemoveWidget={noop} hiddenWidgets={[]} />
    );

    expect(screen.getByText("Key Numbers")).toBeInTheDocument();
    expect(
      screen.getByText("Year-over-Year Comparison")
    ).toBeInTheDocument();
  });

  it("renders widget sections with correct structure", () => {
    const returns = [makeReturn()];
    const fields = { 1: makeFieldSet(1) };
    const summaries = [makeSummary()];

    const { container } = render(
      <Dashboard returns={returns} fields={fields} summaries={summaries} customCharts={[]} onRemoveChart={noop} onRemoveWidget={noop} hiddenWidgets={[]} />
    );

    expect(container.querySelector(".dashboard")).toBeInTheDocument();
    expect(container.querySelector(".widget-section")).toBeInTheDocument();
    expect(container.querySelector(".widget-title")).toBeInTheDocument();
  });
});
