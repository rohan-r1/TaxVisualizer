import type { TaxReturn, ExtractedField, ReturnSummary } from "../types/tax";

export function makeReturn(overrides: Partial<TaxReturn> = {}): TaxReturn {
  return {
    id: 1,
    tax_year: 2023,
    filing_status: "Single",
    pdf_path: "/path/to/1040_2023.pdf",
    pdf_filename: "1040_2023.pdf",
    extraction_method: "mock",
    created_at: "2024-01-01T00:00:00",
    updated_at: "2024-01-01T00:00:00",
    ...overrides,
  };
}

export function makeField(overrides: Partial<ExtractedField> = {}): ExtractedField {
  return {
    id: 1,
    return_id: 1,
    field_key: "total_income",
    field_label: "Total income",
    field_value: "75000",
    field_type: "number",
    category: "income",
    line_number: "9",
    confidence: 1.0,
    needs_review: 0,
    ...overrides,
  };
}

export function makeSummary(overrides: Partial<ReturnSummary> = {}): ReturnSummary {
  return {
    tax_year: 2023,
    filing_status: "Single",
    total_income: 75000,
    agi: 72000,
    taxable_income: 57400,
    total_tax: 8200,
    total_payments: 9500,
    refund: 1300,
    amount_owed: 0,
    effective_tax_rate: 10.93,
    ...overrides,
  };
}

/** Creates a full set of extracted fields for a return */
export function makeFieldSet(returnId: number, values: {
  wages?: number;
  totalIncome?: number;
  adjustments?: number;
  agi?: number;
  standardDeduction?: number;
  taxableIncome?: number;
  totalTax?: number;
  totalPayments?: number;
  refund?: number;
  amountOwed?: number;
} = {}): ExtractedField[] {
  const v = {
    wages: 75000,
    totalIncome: 75000,
    adjustments: 2250,
    agi: 72750,
    standardDeduction: 14600,
    taxableIncome: 58150,
    totalTax: 8500,
    totalPayments: 9800,
    refund: 1300,
    amountOwed: 0,
    ...values,
  };

  let fieldId = returnId * 100;
  const field = (key: string, label: string, value: number, category: string, lineNumber: string): ExtractedField => ({
    id: fieldId++,
    return_id: returnId,
    field_key: key,
    field_label: label,
    field_value: value.toString(),
    field_type: "number",
    category,
    line_number: lineNumber,
    confidence: 1.0,
    needs_review: 0,
  });

  return [
    field("wages", "Wages, salaries, tips", v.wages, "income", "1a"),
    field("total_income", "Total income", v.totalIncome, "income", "9"),
    field("adjustments", "Adjustments to income", v.adjustments, "adjustments", "10"),
    field("agi", "Adjusted gross income", v.agi, "adjustments", "11"),
    field("standard_deduction", "Standard deduction", v.standardDeduction, "deductions", "12"),
    field("taxable_income", "Taxable income", v.taxableIncome, "deductions", "15"),
    field("total_tax", "Total tax", v.totalTax, "tax_computation", "24"),
    field("total_payments", "Total payments", v.totalPayments, "payments", "33"),
    field("refund", "Refund", v.refund, "refund_owed", "34"),
    field("amount_owed", "Amount owed", v.amountOwed, "refund_owed", "37"),
  ];
}

/** Creates multiple years of test data */
export function makeMultiYearData() {
  const returns: TaxReturn[] = [
    makeReturn({ id: 1, tax_year: 2021 }),
    makeReturn({ id: 2, tax_year: 2022, filing_status: "Married Filing Jointly" }),
    makeReturn({ id: 3, tax_year: 2023 }),
  ];

  const fields: Record<number, ExtractedField[]> = {
    1: makeFieldSet(1, { totalIncome: 65000, totalTax: 7000, refund: 800, amountOwed: 0 }),
    2: makeFieldSet(2, { totalIncome: 120000, totalTax: 18000, refund: 2500, amountOwed: 0 }),
    3: makeFieldSet(3, { totalIncome: 75000, totalTax: 8500, refund: 1300, amountOwed: 0 }),
  };

  const summaries: ReturnSummary[] = [
    makeSummary({ tax_year: 2021, total_income: 65000, total_tax: 7000, refund: 800, amount_owed: 0, effective_tax_rate: 10.77 }),
    makeSummary({ tax_year: 2022, filing_status: "Married Filing Jointly", total_income: 120000, total_tax: 18000, refund: 2500, amount_owed: 0, effective_tax_rate: 15.0 }),
    makeSummary({ tax_year: 2023, total_income: 75000, total_tax: 8500, refund: 1300, amount_owed: 0, effective_tax_rate: 11.33 }),
  ];

  return { returns, fields, summaries };
}
