import { describe, it, expect } from "vitest";
import { validateExtraction, type ValidationResult } from "../extractionValidator";
import type { ExtractionResult, ExtractedField } from "../pdfExtractor";

/** Helper to create an extraction result with specified fields */
function makeExtractionResult(
  fieldValues: Record<string, number | null>
): ExtractionResult {
  const fields: ExtractedField[] = Object.entries(fieldValues).map(
    ([key, value]) => ({
      key,
      label: key.replace(/_/g, " "),
      value: value !== null ? String(value) : null,
      category: "income",
      line_number: "",
      confidence: 0.95,
    })
  );

  return {
    year: 2024,
    filing_status: "Single",
    extraction_method: "paddleocr",
    fields,
    page_count: 1,
    detected_forms: ["Form 1040"],
  };
}

describe("validateExtraction", () => {
  describe("income sum validation (disabled)", () => {
    // NOTE: Income sum validation is disabled because we don't extract all
    // income components (IRA distributions, pensions, social security, etc.)
    it("is disabled to avoid false positives", () => {
      const result = makeExtractionResult({
        wages: 75000,
        taxable_interest: 500,
        total_income: 100000, // Mismatch - but should not flag
      });

      const validation = validateExtraction(result);

      expect(validation.issues.filter((i) => i.field === "total_income")).toHaveLength(0);
    });
  });

  describe("AGI calculation validation", () => {
    it("passes when AGI equals total income minus adjustments", () => {
      const result = makeExtractionResult({
        total_income: 80000,
        adjustments: 5000,
        agi: 75000,
      });

      const validation = validateExtraction(result);

      expect(validation.issues.filter((i) => i.field === "agi")).toHaveLength(0);
    });

    it("passes when adjustments is zero (missing)", () => {
      const result = makeExtractionResult({
        total_income: 80000,
        agi: 80000,
      });

      const validation = validateExtraction(result);

      expect(validation.issues.filter((i) => i.field === "agi")).toHaveLength(0);
    });

    it("warns when AGI calculation is wrong", () => {
      const result = makeExtractionResult({
        total_income: 80000,
        adjustments: 5000,
        agi: 70000, // Wrong - should be 75000
      });

      const validation = validateExtraction(result);

      const agiIssue = validation.issues.find((i) => i.field === "agi");
      expect(agiIssue).toBeDefined();
      expect(agiIssue?.severity).toBe("warning");
      expect(agiIssue?.expected).toBe("$75,000");
      expect(agiIssue?.actual).toBe("$70,000");
    });
  });

  describe("taxable income validation", () => {
    it("passes when taxable income equals AGI minus deductions", () => {
      const result = makeExtractionResult({
        agi: 75000,
        total_deductions: 14600,
        taxable_income: 60400,
      });

      const validation = validateExtraction(result);

      expect(validation.issues.filter((i) => i.field === "taxable_income")).toHaveLength(0);
    });

    it("handles zero taxable income when deductions exceed AGI", () => {
      const result = makeExtractionResult({
        agi: 10000,
        total_deductions: 14600,
        taxable_income: 0, // Can't be negative
      });

      const validation = validateExtraction(result);

      expect(validation.issues.filter((i) => i.field === "taxable_income")).toHaveLength(0);
    });

    it("warns when taxable income calculation is wrong", () => {
      const result = makeExtractionResult({
        agi: 75000,
        total_deductions: 14600,
        taxable_income: 50000, // Wrong - should be 60400
      });

      const validation = validateExtraction(result);

      const issue = validation.issues.find((i) => i.field === "taxable_income");
      expect(issue).toBeDefined();
      expect(issue?.severity).toBe("warning");
    });
  });

  describe("payments sum validation (disabled)", () => {
    // NOTE: Payments sum validation is disabled because we don't extract all
    // payment components (additional child tax credit, education credits, etc.)
    it("is disabled to avoid false positives", () => {
      const result = makeExtractionResult({
        federal_withholding: 8000,
        estimated_payments: 0,
        total_payments: 20000, // Mismatch - but should not flag
      });

      const validation = validateExtraction(result);

      expect(validation.issues.filter((i) => i.field === "total_payments")).toHaveLength(0);
    });
  });

  describe("refund/owed validation", () => {
    it("passes when refund matches payments minus tax", () => {
      const result = makeExtractionResult({
        total_payments: 10000,
        total_tax: 8000,
        refund: 2000,
      });

      const validation = validateExtraction(result);

      expect(validation.issues.filter((i) => i.field === "refund")).toHaveLength(0);
    });

    it("passes when amount owed matches tax minus payments", () => {
      const result = makeExtractionResult({
        total_payments: 8000,
        total_tax: 10000,
        amount_owed: 2000,
      });

      const validation = validateExtraction(result);

      expect(validation.issues.filter((i) => i.field === "amount_owed")).toHaveLength(0);
    });

    it("warns when refund doesn't match calculation", () => {
      const result = makeExtractionResult({
        total_payments: 10000,
        total_tax: 8000,
        refund: 3000, // Wrong - should be 2000
      });

      const validation = validateExtraction(result);

      const issue = validation.issues.find((i) => i.field === "refund");
      expect(issue).toBeDefined();
      expect(issue?.severity).toBe("warning");
      expect(issue?.expected).toBe("$2,000");
      expect(issue?.actual).toBe("$3,000");
    });

    it("warns when amount owed doesn't match calculation", () => {
      const result = makeExtractionResult({
        total_payments: 8000,
        total_tax: 10000,
        amount_owed: 500, // Wrong - should be 2000
      });

      const validation = validateExtraction(result);

      const issue = validation.issues.find((i) => i.field === "amount_owed");
      expect(issue).toBeDefined();
      expect(issue?.severity).toBe("warning");
    });
  });

  describe("confidence updates", () => {
    it("reduces confidence for fields with issues", () => {
      const result = makeExtractionResult({
        total_income: 100000,
        adjustments: 0,
        agi: 90000, // Wrong - should be 100000
      });

      const validation = validateExtraction(result);

      expect(validation.fieldUpdates.has("agi")).toBe(true);
      const newConfidence = validation.fieldUpdates.get("agi");
      expect(newConfidence).toBeLessThan(0.95);
    });

    it("uses multiplicative reduction", () => {
      const result = makeExtractionResult({
        total_income: 100000,
        adjustments: 0,
        agi: 90000, // Wrong
      });
      // Set a known confidence
      result.fields.find((f) => f.key === "agi")!.confidence = 0.9;

      const validation = validateExtraction(result);

      // Warning reduces by 0.8x, so 0.9 * 0.8 = 0.72
      expect(validation.fieldUpdates.get("agi")).toBeCloseTo(0.72);
    });

    it("enforces minimum confidence floor", () => {
      const result = makeExtractionResult({
        total_income: 100000,
        adjustments: 0,
        agi: 90000, // Wrong
      });
      // Set very low confidence
      result.fields.find((f) => f.key === "agi")!.confidence = 0.2;

      const validation = validateExtraction(result);

      // Should not go below 0.3
      expect(validation.fieldUpdates.get("agi")).toBeGreaterThanOrEqual(0.3);
    });
  });

  describe("edge cases", () => {
    it("handles empty extraction result", () => {
      const result = makeExtractionResult({});

      const validation = validateExtraction(result);

      expect(validation.isValid).toBe(true);
      expect(validation.issues).toHaveLength(0);
    });

    it("handles null field values", () => {
      const result = makeExtractionResult({
        wages: 75000,
        total_income: null,
      });

      const validation = validateExtraction(result);

      // Should not crash, should skip validation for missing fields
      expect(validation.isValid).toBe(true);
    });

    it("handles zero values correctly", () => {
      const result = makeExtractionResult({
        wages: 75000,
        taxable_interest: 0,
        ordinary_dividends: 0,
        capital_gains: 0,
        other_income: 0,
        total_income: 75000,
      });

      const validation = validateExtraction(result);

      expect(validation.issues.filter((i) => i.field === "total_income")).toHaveLength(0);
    });

    it("handles negative values (capital losses)", () => {
      const result = makeExtractionResult({
        wages: 75000,
        capital_gains: -3000, // Loss
        total_income: 72000,
      });

      const validation = validateExtraction(result);

      expect(validation.issues.filter((i) => i.field === "total_income")).toHaveLength(0);
    });
  });

  describe("isValid flag", () => {
    it("returns true when only warnings exist", () => {
      const result = makeExtractionResult({
        total_income: 100000,
        adjustments: 0,
        agi: 90000, // Wrong - warning
      });

      const validation = validateExtraction(result);

      expect(validation.issues.length).toBeGreaterThan(0);
      expect(validation.issues[0].severity).toBe("warning");
      expect(validation.isValid).toBe(true); // Warnings don't make it invalid
    });

    it("returns true when no issues", () => {
      const result = makeExtractionResult({
        total_income: 100000,
        adjustments: 5000,
        agi: 95000,
      });

      const validation = validateExtraction(result);

      expect(validation.isValid).toBe(true);
    });
  });
});
