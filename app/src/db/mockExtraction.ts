/**
 * Mock extraction - simulates extracting data from a tax return PDF.
 * This will be replaced by the real tiered extraction pipeline.
 *
 * For now, it parses the filename to guess the year and returns
 * placeholder data so we can test the full UI flow.
 */
export function mockExtract(filename: string) {
  // Try to extract year from filename (e.g., "1040_2021_sample.pdf")
  const yearMatch = filename.match(/20\d{2}/);
  const year = yearMatch ? parseInt(yearMatch[0]) : new Date().getFullYear();

  // Generate plausible mock data that varies by year
  const base = 60000 + (year - 2018) * 5000;
  const taxRate = 0.12 + Math.random() * 0.05;
  const totalIncome = base + Math.round(Math.random() * 20000);
  const adjustments = Math.round(totalIncome * 0.03);
  const agi = totalIncome - adjustments;
  const deduction = 14600;
  const taxableIncome = agi - deduction;
  const totalTax = Math.round(taxableIncome * taxRate);
  const payments = totalTax + Math.round((Math.random() - 0.3) * 3000);
  const refund = payments > totalTax ? payments - totalTax : 0;
  const owed = totalTax > payments ? totalTax - payments : 0;

  return {
    year,
    filingStatus: "Single",
    extractionMethod: "mock",
    fields: [
      {
        key: "wages",
        label: "Wages, salaries, tips",
        value: totalIncome.toString(),
        category: "income",
        lineNumber: "1a",
      },
      {
        key: "total_income",
        label: "Total income",
        value: totalIncome.toString(),
        category: "income",
        lineNumber: "9",
      },
      {
        key: "adjustments",
        label: "Adjustments to income",
        value: adjustments.toString(),
        category: "adjustments",
        lineNumber: "10",
      },
      {
        key: "agi",
        label: "Adjusted gross income",
        value: agi.toString(),
        category: "adjustments",
        lineNumber: "11",
      },
      {
        key: "standard_deduction",
        label: "Standard deduction",
        value: deduction.toString(),
        category: "deductions",
        lineNumber: "12",
      },
      {
        key: "taxable_income",
        label: "Taxable income",
        value: taxableIncome.toString(),
        category: "deductions",
        lineNumber: "15",
      },
      {
        key: "total_tax",
        label: "Total tax",
        value: totalTax.toString(),
        category: "tax_computation",
        lineNumber: "24",
      },
      {
        key: "total_payments",
        label: "Total payments",
        value: payments.toString(),
        category: "payments",
        lineNumber: "33",
      },
      {
        key: "refund",
        label: "Refund",
        value: refund.toString(),
        category: "refund_owed",
        lineNumber: "34",
      },
      {
        key: "amount_owed",
        label: "Amount owed",
        value: owed.toString(),
        category: "refund_owed",
        lineNumber: "37",
      },
    ],
  };
}
