import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { YearOverYearChart } from "../YearOverYearChart";
import { makeReturn, makeFieldSet, makeSummary, makeMultiYearData } from "../../test/fixtures";

describe("YearOverYearChart", () => {
  it("renders nothing with fewer than 2 summaries", () => {
    const { container } = render(
      <YearOverYearChart
        returns={[makeReturn()]}
        fields={{ 1: makeFieldSet(1) }}
        summaries={[makeSummary()]}
      />
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders nothing with empty summaries", () => {
    const { container } = render(
      <YearOverYearChart returns={[]} fields={{}} summaries={[]} />
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders the chart container with 2+ summaries", () => {
    const { returns, fields, summaries } = makeMultiYearData();

    const { container } = render(
      <YearOverYearChart
        returns={returns}
        fields={fields}
        summaries={summaries}
      />
    );

    expect(container.querySelector(".yoy-chart-widget")).toBeInTheDocument();
  });

  it("renders with exactly 2 summaries (minimum)", () => {
    const returns = [
      makeReturn({ id: 1, tax_year: 2022 }),
      makeReturn({ id: 2, tax_year: 2023 }),
    ];
    const fields = {
      1: makeFieldSet(1),
      2: makeFieldSet(2),
    };
    const summaries = [
      makeSummary({ tax_year: 2022 }),
      makeSummary({ tax_year: 2023 }),
    ];

    const { container } = render(
      <YearOverYearChart
        returns={returns}
        fields={fields}
        summaries={summaries}
      />
    );

    expect(container.querySelector(".yoy-chart-widget")).toBeInTheDocument();
  });

  it("handles null values in summaries by defaulting to 0", () => {
    const summaries = [
      makeSummary({ tax_year: 2022, total_income: null, total_tax: null }),
      makeSummary({ tax_year: 2023, refund: null, amount_owed: null }),
    ];

    // Should not throw
    const { container } = render(
      <YearOverYearChart
        returns={[makeReturn({ id: 1 }), makeReturn({ id: 2 })]}
        fields={{}}
        summaries={summaries}
      />
    );

    expect(container.querySelector(".yoy-chart-widget")).toBeInTheDocument();
  });
});
