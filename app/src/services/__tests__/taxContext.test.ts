import { describe, it, expect } from "vitest";
import { buildTaxContext } from "../taxContext";
import {
  makeReturn,
  makeSummary,
  makeField,
  makeFieldSet,
  makeMultiYearData,
  makeScheduleAFields,
  makeScheduleCFields,
  makeScheduleDFields,
} from "../../test/fixtures";

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

  it("shows refund when present in summary", () => {
    const returns = [makeReturn()];
    const fields = { 1: makeFieldSet(1) };
    const summaries = [makeSummary({ refund: 1500, amount_owed: 0 })];

    const result = buildTaxContext(returns, fields, summaries);

    // Check the summary section shows refund
    expect(result).toContain("Refund: $1,500");
    // Summary should not show "Amount Owed:" line when amount is 0
    // (detailed fields section may still show the field)
    const summarySection = result.split("## Detailed Breakdown")[0];
    expect(summarySection).not.toContain("Amount Owed:");
  });

  it("shows amount owed when present", () => {
    const returns = [makeReturn()];
    const fields = { 1: makeFieldSet(1) };
    const summaries = [makeSummary({ refund: 0, amount_owed: 500 })];

    const result = buildTaxContext(returns, fields, summaries);

    expect(result).toContain("Amount Owed: $500");
    expect(result).not.toContain("Refund:");
  });

  describe("detailed field serialization", () => {
    it("includes detailed breakdown section when fields exist", () => {
      const returns = [makeReturn()];
      const fields = { 1: makeFieldSet(1) };
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      expect(result).toContain("## Detailed Breakdown by Year");
      expect(result).toContain("2023 Tax Return Details");
    });

    it("groups fields by category", () => {
      const returns = [makeReturn()];
      const fields = { 1: makeFieldSet(1) };
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      expect(result).toContain("**Income Breakdown:**");
      expect(result).toContain("**Adjustments to Income:**");
      expect(result).toContain("**Deductions:**");
      expect(result).toContain("**Tax Computation:**");
      expect(result).toContain("**Payments & Withholding:**");
      expect(result).toContain("**Refund or Amount Owed:**");
    });

    it("includes line numbers for fields", () => {
      const returns = [makeReturn()];
      const fields = { 1: makeFieldSet(1) };
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      expect(result).toContain("(Line 1a)");
      expect(result).toContain("(Line 9)");
      expect(result).toContain("(Line 11)");
    });

    it("includes field labels and values", () => {
      const returns = [makeReturn()];
      const fields = { 1: makeFieldSet(1, { wages: 85000 }) };
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      expect(result).toContain("Wages, salaries, tips");
      expect(result).toContain("85000");
    });

    it("flags low confidence items", () => {
      const returns = [makeReturn()];
      const fields = {
        1: [
          makeField({ confidence: 0.92, field_label: "Uncertain income" }),
          makeField({ id: 2, confidence: 1.0, field_label: "Certain income" }),
        ],
      };
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      expect(result).toContain("⚠️ Low confidence items (may need review):");
      expect(result).toContain("Uncertain income: 92% confidence");
    });

    it("shows 'None' when all items have high confidence", () => {
      const returns = [makeReturn()];
      const fields = { 1: makeFieldSet(1) }; // All fields have confidence: 1.0
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      expect(result).toContain("⚠️ Low confidence items: None");
    });

    it("handles empty fields gracefully", () => {
      const returns = [makeReturn()];
      const fields = { 1: [] };
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      // Should not throw and should still have summaries
      expect(result).toContain("Tax Year 2023");
      // Detailed breakdown should not appear when no fields
      expect(result).not.toContain("Detailed Breakdown by Year");
    });

    it("handles missing fields for a return", () => {
      const returns = [makeReturn()];
      const fields = {}; // No fields at all
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      expect(result).toContain("Tax Year 2023");
      expect(result).not.toContain("Detailed Breakdown by Year");
    });

    it("serializes fields for multiple years", () => {
      const { returns, fields, summaries } = makeMultiYearData();

      const result = buildTaxContext(returns, fields, summaries);

      expect(result).toContain("2023 Tax Return Details");
      expect(result).toContain("2022 Tax Return Details");
      expect(result).toContain("2021 Tax Return Details");
    });
  });

  describe("schedule serialization", () => {
    it("serializes Schedule A (itemized deductions) fields", () => {
      const returns = [makeReturn()];
      const fields = {
        1: [...makeFieldSet(1), ...makeScheduleAFields(1)],
      };
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      expect(result).toContain("**Schedule A (Itemized Deductions):**");
      expect(result).toContain("Medical and dental expenses");
      expect(result).toContain("State and local taxes (SALT)");
      expect(result).toContain("Home mortgage interest");
      expect(result).toContain("Gifts to charity");
      expect(result).toContain("Total itemized deductions");
      expect(result).toContain("(Line 5d)"); // SALT line number
    });

    it("serializes Schedule C (self-employment) fields", () => {
      const returns = [makeReturn()];
      const fields = {
        1: [...makeFieldSet(1), ...makeScheduleCFields(1)],
      };
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      expect(result).toContain("**Schedule C (Self-Employment):**");
      expect(result).toContain("Gross receipts or sales");
      expect(result).toContain("Cost of goods sold");
      expect(result).toContain("Gross profit");
      expect(result).toContain("Total expenses");
      expect(result).toContain("Net profit (or loss)");
      expect(result).toContain("(Line 31)"); // Net profit line number
    });

    it("serializes Schedule D (capital gains) fields", () => {
      const returns = [makeReturn()];
      const fields = {
        1: [...makeFieldSet(1), ...makeScheduleDFields(1)],
      };
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      expect(result).toContain("**Schedule D (Capital Gains/Losses):**");
      expect(result).toContain("Short-term capital gain/loss");
      expect(result).toContain("Long-term capital gain/loss");
      expect(result).toContain("Net capital gain (or loss)");
      expect(result).toContain("Capital loss carryover");
      expect(result).toContain("(Line 16)"); // Net gain line number
    });

    it("serializes multiple schedules together", () => {
      const returns = [makeReturn()];
      const fields = {
        1: [
          ...makeFieldSet(1),
          ...makeScheduleAFields(1),
          ...makeScheduleCFields(1),
          ...makeScheduleDFields(1),
        ],
      };
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      // All three schedules should be present
      expect(result).toContain("**Schedule A (Itemized Deductions):**");
      expect(result).toContain("**Schedule C (Self-Employment):**");
      expect(result).toContain("**Schedule D (Capital Gains/Losses):**");

      // Schedules should appear after Form 1040 categories
      const scheduleAIndex = result.indexOf("Schedule A");
      const incomeIndex = result.indexOf("Income Breakdown");
      expect(scheduleAIndex).toBeGreaterThan(incomeIndex);
    });

    it("displays schedules in correct order", () => {
      const returns = [makeReturn()];
      const fields = {
        1: [
          ...makeFieldSet(1),
          ...makeScheduleDFields(1), // Add D first
          ...makeScheduleAFields(1), // Add A second
          ...makeScheduleCFields(1), // Add C third
        ],
      };
      const summaries = [makeSummary()];

      const result = buildTaxContext(returns, fields, summaries);

      // Should display in order: A, C, D regardless of input order
      const indexA = result.indexOf("Schedule A");
      const indexC = result.indexOf("Schedule C");
      const indexD = result.indexOf("Schedule D");

      expect(indexA).toBeLessThan(indexC);
      expect(indexC).toBeLessThan(indexD);
    });
  });
});
