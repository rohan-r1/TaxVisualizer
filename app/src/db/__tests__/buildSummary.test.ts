import { describe, it, expect } from "vitest";
import { buildSummary } from "../database";
import { makeReturn, makeField, makeFieldSet } from "../../test/fixtures";

describe("buildSummary", () => {
  it("extracts key numbers from fields", () => {
    const ret = makeReturn({ id: 1, tax_year: 2023, filing_status: "Single" });
    const fields = makeFieldSet(1, {
      totalIncome: 75000,
      agi: 72750,
      taxableIncome: 58150,
      totalTax: 8500,
      totalPayments: 9800,
      refund: 1300,
      amountOwed: 0,
    });

    const summary = buildSummary(ret, fields);

    expect(summary.tax_year).toBe(2023);
    expect(summary.filing_status).toBe("Single");
    expect(summary.total_income).toBe(75000);
    expect(summary.agi).toBe(72750);
    expect(summary.taxable_income).toBe(58150);
    expect(summary.total_tax).toBe(8500);
    expect(summary.total_payments).toBe(9800);
    expect(summary.refund).toBe(1300);
    expect(summary.amount_owed).toBe(0);
  });

  it("computes effective tax rate correctly", () => {
    const ret = makeReturn();
    const fields = makeFieldSet(1, { totalIncome: 100000, totalTax: 15000 });

    const summary = buildSummary(ret, fields);

    expect(summary.effective_tax_rate).toBe(15.0);
  });

  it("returns null effective_tax_rate when income is zero", () => {
    const ret = makeReturn();
    const fields = makeFieldSet(1, { totalIncome: 0, totalTax: 0 });

    const summary = buildSummary(ret, fields);

    expect(summary.effective_tax_rate).toBeNull();
  });

  it("returns null for missing fields", () => {
    const ret = makeReturn();
    const summary = buildSummary(ret, []);

    expect(summary.total_income).toBeNull();
    expect(summary.agi).toBeNull();
    expect(summary.taxable_income).toBeNull();
    expect(summary.total_tax).toBeNull();
    expect(summary.total_payments).toBeNull();
    expect(summary.refund).toBeNull();
    expect(summary.amount_owed).toBeNull();
    expect(summary.effective_tax_rate).toBeNull();
  });

  it("returns null for fields with null values", () => {
    const ret = makeReturn();
    const fields = [
      makeField({ field_key: "total_income", field_value: null }),
      makeField({ field_key: "total_tax", field_value: null }),
    ];

    const summary = buildSummary(ret, fields);

    expect(summary.total_income).toBeNull();
    expect(summary.total_tax).toBeNull();
    expect(summary.effective_tax_rate).toBeNull();
  });

  it("returns null for non-numeric field values", () => {
    const ret = makeReturn();
    const fields = [
      makeField({ field_key: "total_income", field_value: "not-a-number" }),
    ];

    const summary = buildSummary(ret, fields);

    expect(summary.total_income).toBeNull();
  });

  it("uses 'Unknown' when filing_status is null", () => {
    const ret = makeReturn({ filing_status: null });
    const summary = buildSummary(ret, []);

    expect(summary.filing_status).toBe("Unknown");
  });

  it("rounds effective tax rate to 2 decimal places", () => {
    const ret = makeReturn();
    const fields = makeFieldSet(1, { totalIncome: 73000, totalTax: 8533 });

    const summary = buildSummary(ret, fields);

    // 8533 / 73000 * 100 = 11.688... should round to 11.69
    expect(summary.effective_tax_rate).toBe(11.69);
  });

  it("handles large income values", () => {
    const ret = makeReturn();
    const fields = makeFieldSet(1, {
      totalIncome: 5000000,
      totalTax: 1750000,
    });

    const summary = buildSummary(ret, fields);

    expect(summary.total_income).toBe(5000000);
    expect(summary.total_tax).toBe(1750000);
    expect(summary.effective_tax_rate).toBe(35.0);
  });
});
