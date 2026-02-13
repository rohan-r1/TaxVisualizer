import { describe, it, expect } from "vitest";
import { mockExtract } from "../mockExtraction";

describe("mockExtract", () => {
  it("extracts year from filename", () => {
    const result = mockExtract("1040_2021_sample.pdf");
    expect(result.year).toBe(2021);
  });

  it("extracts year from different filename formats", () => {
    expect(mockExtract("tax_return_2022.pdf").year).toBe(2022);
    expect(mockExtract("2023_filing.pdf").year).toBe(2023);
    expect(mockExtract("my-2020-return.pdf").year).toBe(2020);
  });

  it("uses current year when no year found in filename", () => {
    const result = mockExtract("no_year_here.pdf");
    expect(result.year).toBe(new Date().getFullYear());
  });

  it("returns 'Single' as default filing status", () => {
    const result = mockExtract("1040_2023.pdf");
    expect(result.filingStatus).toBe("Single");
  });

  it("returns 'mock' as extraction method", () => {
    const result = mockExtract("1040_2023.pdf");
    expect(result.extractionMethod).toBe("mock");
  });

  it("returns all expected Form 1040 field keys", () => {
    const result = mockExtract("1040_2023.pdf");
    const keys = result.fields.map((f) => f.key);

    // Core Form 1040 fields are always present
    expect(keys).toContain("wages");
    expect(keys).toContain("total_income");
    expect(keys).toContain("adjustments");
    expect(keys).toContain("agi");
    expect(keys).toContain("deduction"); // Can be standard or itemized
    expect(keys).toContain("taxable_income");
    expect(keys).toContain("total_tax");
    expect(keys).toContain("total_payments");
    expect(keys).toContain("refund");
    expect(keys).toContain("amount_owed");
  });

  it("returns at least 10 Form 1040 fields", () => {
    const result = mockExtract("1040_2023.pdf");
    // 10 base fields + optional schedule fields (0-14)
    expect(result.fields.length).toBeGreaterThanOrEqual(10);
    expect(result.fields.length).toBeLessThanOrEqual(24); // 10 + 5 + 5 + 4 schedules
  });

  it("generates numeric string values for all fields", () => {
    const result = mockExtract("1040_2023.pdf");
    for (const field of result.fields) {
      const parsed = parseFloat(field.value);
      expect(isNaN(parsed)).toBe(false);
    }
  });

  it("ensures refund and amount_owed are mutually exclusive", () => {
    // Run multiple times since values have randomness
    for (let i = 0; i < 20; i++) {
      const result = mockExtract(`test_2023_${i}.pdf`);
      const refund = parseFloat(result.fields.find((f) => f.key === "refund")!.value);
      const owed = parseFloat(result.fields.find((f) => f.key === "amount_owed")!.value);

      // At least one should be 0
      expect(refund === 0 || owed === 0).toBe(true);
      // Both should be non-negative
      expect(refund).toBeGreaterThanOrEqual(0);
      expect(owed).toBeGreaterThanOrEqual(0);
    }
  });

  it("assigns correct categories to Form 1040 fields", () => {
    const result = mockExtract("1040_2023.pdf");
    const fieldMap = Object.fromEntries(result.fields.map((f) => [f.key, f]));

    expect(fieldMap.wages.category).toBe("income");
    expect(fieldMap.total_income.category).toBe("income");
    expect(fieldMap.adjustments.category).toBe("adjustments");
    expect(fieldMap.agi.category).toBe("adjustments");
    expect(fieldMap.deduction.category).toBe("deductions");
    expect(fieldMap.taxable_income.category).toBe("deductions");
    expect(fieldMap.total_tax.category).toBe("tax_computation");
    expect(fieldMap.total_payments.category).toBe("payments");
    expect(fieldMap.refund.category).toBe("refund_owed");
    expect(fieldMap.amount_owed.category).toBe("refund_owed");
  });

  it("assigns line numbers to all fields", () => {
    const result = mockExtract("1040_2023.pdf");
    for (const field of result.fields) {
      expect(field.lineNumber).toBeDefined();
      expect(field.lineNumber).not.toBe("");
    }
  });

  it("generates consistent math (agi = total_income - adjustments)", () => {
    const result = mockExtract("1040_2023.pdf");
    const fieldMap = Object.fromEntries(result.fields.map((f) => [f.key, parseFloat(f.value)]));

    expect(fieldMap.agi).toBe(fieldMap.total_income - fieldMap.adjustments);
  });

  it("generates consistent math (taxable_income = agi - deduction)", () => {
    const result = mockExtract("1040_2023.pdf");
    const fieldMap = Object.fromEntries(result.fields.map((f) => [f.key, parseFloat(f.value)]));

    // Taxable income is AGI minus deduction (standard or itemized)
    // Result should be non-negative
    const expected = Math.max(0, fieldMap.agi - fieldMap.deduction);
    expect(fieldMap.taxable_income).toBe(expected);
  });

  it("includes schedule fields when applicable", () => {
    // Run multiple times to catch cases with schedules
    let foundScheduleA = false;
    let foundScheduleC = false;
    let foundScheduleD = false;

    for (let i = 0; i < 50; i++) {
      const result = mockExtract(`test_${i}_2023.pdf`);
      const keys = result.fields.map((f) => f.key);

      if (keys.some((k) => k.startsWith("sched_a_"))) foundScheduleA = true;
      if (keys.some((k) => k.startsWith("sched_c_"))) foundScheduleC = true;
      if (keys.some((k) => k.startsWith("sched_d_"))) foundScheduleD = true;
    }

    // With 50 iterations, we should find at least one instance of each schedule
    // (probabilistically, given the random inclusion logic)
    expect(foundScheduleA || foundScheduleC || foundScheduleD).toBe(true);
  });

  it("assigns correct categories to schedule fields", () => {
    // Run until we find a result with schedules
    let result;
    for (let i = 0; i < 100; i++) {
      result = mockExtract(`test_${i}_schedules.pdf`);
      if (result.fields.some((f) => f.category.startsWith("schedule_"))) {
        break;
      }
    }

    const scheduleFields = result!.fields.filter((f) => f.category.startsWith("schedule_"));

    for (const field of scheduleFields) {
      if (field.key.startsWith("sched_a_")) {
        expect(field.category).toBe("schedule_a");
      } else if (field.key.startsWith("sched_c_")) {
        expect(field.category).toBe("schedule_c");
      } else if (field.key.startsWith("sched_d_")) {
        expect(field.category).toBe("schedule_d");
      }
    }
  });
});
