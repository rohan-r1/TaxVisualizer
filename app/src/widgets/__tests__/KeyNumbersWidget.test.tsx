import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { KeyNumbersWidget } from "../KeyNumbersWidget";
import { makeReturn, makeFieldSet, makeSummary, makeMultiYearData } from "../../test/fixtures";

describe("KeyNumbersWidget", () => {
  const defaultProps = {
    returns: [makeReturn()],
    fields: { 1: makeFieldSet(1) },
    summaries: [makeSummary()],
  };

  it("renders nothing when summaries are empty", () => {
    const { container } = render(
      <KeyNumbersWidget
        returns={[]}
        fields={{}}
        summaries={[]}
      />
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders the year column header", () => {
    render(<KeyNumbersWidget {...defaultProps} />);

    expect(screen.getByText("2023")).toBeInTheDocument();
  });

  it("displays all key metric labels as row headers", () => {
    render(<KeyNumbersWidget {...defaultProps} />);

    expect(screen.getByText("Total Income")).toBeInTheDocument();
    expect(screen.getByText("AGI")).toBeInTheDocument();
    expect(screen.getByText("Taxable Income")).toBeInTheDocument();
    expect(screen.getByText("Total Tax")).toBeInTheDocument();
    expect(screen.getByText("Effective Rate")).toBeInTheDocument();
    expect(screen.getByText("Total Payments")).toBeInTheDocument();
    expect(screen.getByText("Refund")).toBeInTheDocument();
    expect(screen.getByText("Amount Owed")).toBeInTheDocument();
  });

  it("formats currency values correctly", () => {
    render(<KeyNumbersWidget {...defaultProps} />);

    expect(screen.getByText("$75,000")).toBeInTheDocument();
  });

  it("formats percentage values correctly", () => {
    render(<KeyNumbersWidget {...defaultProps} />);

    expect(screen.getByText("10.93%")).toBeInTheDocument();
  });

  it("displays em dash for null values", () => {
    const summaries = [
      makeSummary({ total_income: null, agi: null, effective_tax_rate: null }),
    ];

    render(
      <KeyNumbersWidget
        returns={defaultProps.returns}
        fields={defaultProps.fields}
        summaries={summaries}
      />
    );

    const dashes = screen.getAllByText("—");
    expect(dashes.length).toBeGreaterThanOrEqual(3);
  });

  it("renders year columns for multiple returns", () => {
    const { returns, fields, summaries } = makeMultiYearData();

    render(
      <KeyNumbersWidget
        returns={returns}
        fields={fields}
        summaries={summaries}
      />
    );

    expect(screen.getByText("2021")).toBeInTheDocument();
    expect(screen.getByText("2022")).toBeInTheDocument();
    expect(screen.getByText("2023")).toBeInTheDocument();
  });

  it("renders tabular structure with correct CSS classes", () => {
    const { container } = render(<KeyNumbersWidget {...defaultProps} />);

    expect(container.querySelector(".key-numbers-table")).toBeInTheDocument();
    expect(container.querySelector(".kn-header-row")).toBeInTheDocument();
    expect(container.querySelector(".kn-row")).toBeInTheDocument();
    expect(container.querySelector(".kn-label-cell")).toBeInTheDocument();
    expect(container.querySelector(".kn-value-cell")).toBeInTheDocument();
  });

  it("displays $0 for zero-value fields", () => {
    const summaries = [makeSummary({ amount_owed: 0 })];

    render(
      <KeyNumbersWidget
        returns={defaultProps.returns}
        fields={defaultProps.fields}
        summaries={summaries}
      />
    );

    expect(screen.getByText("$0")).toBeInTheDocument();
  });

  it("shows filing status in the table", () => {
    render(<KeyNumbersWidget {...defaultProps} />);

    expect(screen.getByText("Filing Status")).toBeInTheDocument();
    expect(screen.getByText("Single")).toBeInTheDocument();
  });
});
