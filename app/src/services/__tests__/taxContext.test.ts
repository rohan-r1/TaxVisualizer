import { describe, it, expect } from "vitest";
import { buildTaxContext } from "../taxContext";
import { makeReturn, makeSummary, makeFieldSet, makeMultiYearData } from "../../test/fixtures";

describe("buildTaxContext", () => {
  it("returns message when no returns uploaded", () => {
    const result = buildTaxContext([], {}, []);

    expect(result).toBe("No tax returns have been uploaded yet.");
  });

  it("includes summary information for single year", () => {
    const returns = [makeReturn()];
    const fields = { 1: makeFieldSet(1) };
    const summaries = [makeSummary({ tax_year: 2023, total_income: 75000 })];

    const result = buildTaxContext(returns, fields, summaries);

    expect(result).toContain("Tax Year 2023");
    expect(result).toContain("$75,000");
    expect(result).toContain("Filing Status: Single");
  });

  it("includes effective tax rate", () => {
    const returns = [makeReturn()];
    const fields = { 1: makeFieldSet(1) };
    const summaries = [makeSummary({ effective_tax_rate: 10.93 })];

    const result = buildTaxContext(returns, fields, summaries);

    expect(result).toContain("Effective Tax Rate: 10.93%");
  });

  it("includes year-over-year changes for multiple years", () => {
    const { returns, fields, summaries } = makeMultiYearData();

    const result = buildTaxContext(returns, fields, summaries);

    expect(result).toContain("Year-over-Year Changes");
    expect(result).toContain("2022 → 2023");
    expect(result).toContain("2021 → 2022");
  });

  it("includes lifetime totals", () => {
    const { returns, fields, summaries } = makeMultiYearData();

    const result = buildTaxContext(returns, fields, summaries);

    expect(result).toContain("Lifetime Totals");
    expect(result).toContain("Years of data: 3");
    expect(result).toContain("Total tax paid:");
  });

  it("sorts summaries by year descending", () => {
    const { returns, fields, summaries } = makeMultiYearData();

    const result = buildTaxContext(returns, fields, summaries);

    const idx2023 = result.indexOf("Tax Year 2023");
    const idx2022 = result.indexOf("Tax Year 2022");
    const idx2021 = result.indexOf("Tax Year 2021");

    expect(idx2023).toBeLessThan(idx2022);
    expect(idx2022).toBeLessThan(idx2021);
  });

  it("shows refund when present", () => {
    const returns = [makeReturn()];
    const fields = { 1: makeFieldSet(1) };
    const summaries = [makeSummary({ refund: 1500, amount_owed: 0 })];

    const result = buildTaxContext(returns, fields, summaries);

    expect(result).toContain("Refund: $1,500");
    expect(result).not.toContain("Amount Owed:");
  });

  it("shows amount owed when present", () => {
    const returns = [makeReturn()];
    const fields = { 1: makeFieldSet(1) };
    const summaries = [makeSummary({ refund: 0, amount_owed: 500 })];

    const result = buildTaxContext(returns, fields, summaries);

    expect(result).toContain("Amount Owed: $500");
    expect(result).not.toContain("Refund:");
  });
});
