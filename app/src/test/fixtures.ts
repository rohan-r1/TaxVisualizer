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

/** Creates Schedule A (Itemized Deductions) fields */
export function makeScheduleAFields(returnId: number, values: {
  medical?: number;
  salt?: number;
  mortgageInterest?: number;
  charity?: number;
  total?: number;
} = {}): ExtractedField[] {
  const v = {
    medical: 3500,
    salt: 10000,
    mortgageInterest: 12000,
    charity: 5000,
    total: 30500,
    ...values,
  };

  let fieldId = returnId * 100 + 50;
  return [
    { id: fieldId++, return_id: returnId, field_key: "sched_a_medical", field_label: "Medical and dental expenses", field_value: v.medical.toString(), field_type: "number", category: "schedule_a", line_number: "1", confidence: 1.0, needs_review: 0 },
    { id: fieldId++, return_id: returnId, field_key: "sched_a_salt", field_label: "State and local taxes (SALT)", field_value: v.salt.toString(), field_type: "number", category: "schedule_a", line_number: "5d", confidence: 1.0, needs_review: 0 },
    { id: fieldId++, return_id: returnId, field_key: "sched_a_mortgage_interest", field_label: "Home mortgage interest", field_value: v.mortgageInterest.toString(), field_type: "number", category: "schedule_a", line_number: "8a", confidence: 1.0, needs_review: 0 },
    { id: fieldId++, return_id: returnId, field_key: "sched_a_charity", field_label: "Gifts to charity", field_value: v.charity.toString(), field_type: "number", category: "schedule_a", line_number: "11", confidence: 1.0, needs_review: 0 },
    { id: fieldId++, return_id: returnId, field_key: "sched_a_total", field_label: "Total itemized deductions", field_value: v.total.toString(), field_type: "number", category: "schedule_a", line_number: "17", confidence: 1.0, needs_review: 0 },
  ];
}

/** Creates Schedule C (Self-Employment) fields */
export function makeScheduleCFields(returnId: number, values: {
  grossReceipts?: number;
  cogs?: number;
  grossProfit?: number;
  expenses?: number;
  netProfit?: number;
} = {}): ExtractedField[] {
  const v = {
    grossReceipts: 50000,
    cogs: 10000,
    grossProfit: 40000,
    expenses: 15000,
    netProfit: 25000,
    ...values,
  };

  let fieldId = returnId * 100 + 60;
  return [
    { id: fieldId++, return_id: returnId, field_key: "sched_c_gross_receipts", field_label: "Gross receipts or sales", field_value: v.grossReceipts.toString(), field_type: "number", category: "schedule_c", line_number: "1", confidence: 1.0, needs_review: 0 },
    { id: fieldId++, return_id: returnId, field_key: "sched_c_cogs", field_label: "Cost of goods sold", field_value: v.cogs.toString(), field_type: "number", category: "schedule_c", line_number: "4", confidence: 1.0, needs_review: 0 },
    { id: fieldId++, return_id: returnId, field_key: "sched_c_gross_profit", field_label: "Gross profit", field_value: v.grossProfit.toString(), field_type: "number", category: "schedule_c", line_number: "5", confidence: 1.0, needs_review: 0 },
    { id: fieldId++, return_id: returnId, field_key: "sched_c_expenses", field_label: "Total expenses", field_value: v.expenses.toString(), field_type: "number", category: "schedule_c", line_number: "28", confidence: 1.0, needs_review: 0 },
    { id: fieldId++, return_id: returnId, field_key: "sched_c_net_profit", field_label: "Net profit (or loss)", field_value: v.netProfit.toString(), field_type: "number", category: "schedule_c", line_number: "31", confidence: 1.0, needs_review: 0 },
  ];
}

/** Creates Schedule D (Capital Gains/Losses) fields */
export function makeScheduleDFields(returnId: number, values: {
  shortTermGain?: number;
  longTermGain?: number;
  netGain?: number;
  carryover?: number;
} = {}): ExtractedField[] {
  const v = {
    shortTermGain: 2000,
    longTermGain: 8000,
    netGain: 10000,
    carryover: 0,
    ...values,
  };

  let fieldId = returnId * 100 + 70;
  return [
    { id: fieldId++, return_id: returnId, field_key: "sched_d_short_term", field_label: "Short-term capital gain/loss", field_value: v.shortTermGain.toString(), field_type: "number", category: "schedule_d", line_number: "7", confidence: 1.0, needs_review: 0 },
    { id: fieldId++, return_id: returnId, field_key: "sched_d_long_term", field_label: "Long-term capital gain/loss", field_value: v.longTermGain.toString(), field_type: "number", category: "schedule_d", line_number: "15", confidence: 1.0, needs_review: 0 },
    { id: fieldId++, return_id: returnId, field_key: "sched_d_net", field_label: "Net capital gain (or loss)", field_value: v.netGain.toString(), field_type: "number", category: "schedule_d", line_number: "16", confidence: 1.0, needs_review: 0 },
    { id: fieldId++, return_id: returnId, field_key: "sched_d_carryover", field_label: "Capital loss carryover", field_value: v.carryover.toString(), field_type: "number", category: "schedule_d", line_number: "21", confidence: 1.0, needs_review: 0 },
  ];
}
