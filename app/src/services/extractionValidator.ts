/**
 * Extraction Validator Service
 *
 * Validates extracted tax data by checking mathematical relationships
 * between fields. Runs after PDF extraction, before database storage.
 *
 * Phase 1: Local math validation (no API calls)
 * Phase 2 (future): LLM validation for ambiguous fields
 */

import type { ExtractionResult, ExtractedField } from "./pdfExtractor";

/**
 * A validation issue found during extraction validation
 */
export interface ValidationIssue {
  /** Severity of the issue */
  severity: "error" | "warning";
  /** The field key that has an issue */
  field: string;
  /** Human-readable description of the issue */
  message: string;
  /** Expected value (formatted for display) */
  expected?: string;
  /** Actual value found (formatted for display) */
  actual?: string;
}

/**
 * Result of validation
 */
export interface ValidationResult {
  /** True if no errors found (warnings are OK) */
  isValid: boolean;
  /** List of issues found */
  issues: ValidationIssue[];
  /** Map of field key -> updated confidence score */
  fieldUpdates: Map<string, number>;
}

/**
 * Format a number as currency for display
 */
function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Check if two values are approximately equal (within $1 tolerance)
 */
function approxEqual(a: number, b: number, tolerance: number = 1): boolean {
  return Math.abs(a - b) <= tolerance;
}

/**
 * Sum values for given field keys, skipping missing fields
 */
function sumFields(
  fields: Map<string, number>,
  keys: string[]
): number | undefined {
  let sum = 0;
  let hasAnyValue = false;

  for (const key of keys) {
    const value = fields.get(key);
    if (value !== undefined) {
      sum += value;
      hasAnyValue = true;
    }
  }

  return hasAnyValue ? sum : undefined;
}

/**
 * Check income components sum to total_income
 *
 * NOTE: This check is disabled because we don't extract all income components
 * (missing IRA distributions, pensions, social security, etc.), leading to
 * false positives. Re-enable when we extract all Form 1040 income lines.
 */
function checkIncomeSum(_fields: Map<string, number>): ValidationIssue[] {
  // Disabled - see note above
  return [];
}

/**
 * Check AGI calculation
 * Form 1040: line 9 - line 10 = line 11
 */
function checkAgiCalculation(fields: Map<string, number>): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  const totalIncome = fields.get("total_income");
  const adjustments = fields.get("adjustments") ?? 0;
  const agi = fields.get("agi");

  if (totalIncome === undefined || agi === undefined) return issues;

  const expectedAgi = totalIncome - adjustments;

  if (!approxEqual(expectedAgi, agi)) {
    issues.push({
      severity: "warning",
      field: "agi",
      message: "AGI doesn't match total income minus adjustments",
      expected: formatCurrency(expectedAgi),
      actual: formatCurrency(agi),
    });
  }

  return issues;
}

/**
 * Check taxable income calculation
 * Form 1040: line 11 - line 14 = line 15
 */
function checkTaxableIncome(fields: Map<string, number>): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  const agi = fields.get("agi");
  const totalDeductions = fields.get("total_deductions");
  const taxableIncome = fields.get("taxable_income");

  if (
    agi === undefined ||
    totalDeductions === undefined ||
    taxableIncome === undefined
  ) {
    return issues;
  }

  const expectedTaxable = Math.max(0, agi - totalDeductions);

  if (!approxEqual(expectedTaxable, taxableIncome)) {
    issues.push({
      severity: "warning",
      field: "taxable_income",
      message: "Taxable income doesn't match AGI minus deductions",
      expected: formatCurrency(expectedTaxable),
      actual: formatCurrency(taxableIncome),
    });
  }

  return issues;
}

/**
 * Check payments sum
 *
 * NOTE: This check is disabled because we don't extract all payment components
 * (missing additional child tax credit, education credits, etc.), leading to
 * false positives. Re-enable when we extract all Form 1040 payment lines.
 */
function checkPaymentsSum(_fields: Map<string, number>): ValidationIssue[] {
  // Disabled - see note above
  return [];
}

/**
 * Check refund/owed calculation
 * Form 1040: line 33 - line 24 = line 34 (refund) or line 24 - line 33 = line 37 (owed)
 */
function checkRefundOwed(fields: Map<string, number>): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  const totalPayments = fields.get("total_payments");
  const totalTax = fields.get("total_tax");
  const refund = fields.get("refund");
  const amountOwed = fields.get("amount_owed");

  if (totalPayments === undefined || totalTax === undefined) return issues;

  const difference = totalPayments - totalTax;

  if (difference >= 0 && refund !== undefined) {
    // Should be a refund
    if (!approxEqual(difference, refund)) {
      issues.push({
        severity: "warning",
        field: "refund",
        message: "Refund doesn't match payments minus tax",
        expected: formatCurrency(difference),
        actual: formatCurrency(refund),
      });
    }
  } else if (difference < 0 && amountOwed !== undefined) {
    // Should owe money
    const expectedOwed = Math.abs(difference);
    if (!approxEqual(expectedOwed, amountOwed)) {
      issues.push({
        severity: "warning",
        field: "amount_owed",
        message: "Amount owed doesn't match tax minus payments",
        expected: formatCurrency(expectedOwed),
        actual: formatCurrency(amountOwed),
      });
    }
  }

  return issues;
}

/**
 * Validate an extraction result by checking mathematical relationships
 *
 * @param result - The extraction result to validate
 * @returns Validation result with issues and confidence updates
 */
export function validateExtraction(result: ExtractionResult): ValidationResult {
  const issues: ValidationIssue[] = [];
  const fieldUpdates = new Map<string, number>();

  // Build field lookup (key -> numeric value)
  const fields = new Map<string, number>();
  for (const f of result.fields) {
    if (f.value !== null) {
      const parsed = parseInt(f.value, 10);
      if (!isNaN(parsed)) {
        fields.set(f.key, parsed);
      }
    }
  }

  // Run validation rules
  issues.push(...checkIncomeSum(fields));
  issues.push(...checkAgiCalculation(fields));
  issues.push(...checkTaxableIncome(fields));
  issues.push(...checkPaymentsSum(fields));
  issues.push(...checkRefundOwed(fields));

  // Reduce confidence for fields with issues
  // Use multiplicative reduction since OCR confidence varies
  for (const issue of issues) {
    const field = result.fields.find((f) => f.key === issue.field);
    const currentConf = field?.confidence ?? 0.9;
    const multiplier = issue.severity === "error" ? 0.6 : 0.8;
    fieldUpdates.set(issue.field, Math.max(0.3, currentConf * multiplier));
  }

  return {
    isValid: issues.filter((i) => i.severity === "error").length === 0,
    issues,
    fieldUpdates,
  };
}
