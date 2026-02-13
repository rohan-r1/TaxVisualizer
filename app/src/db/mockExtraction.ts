/**
 * Mock extraction - simulates extracting data from a tax return PDF.
 * This will be replaced by the real tiered extraction pipeline.
 *
 * For now, it parses the filename to guess the year and returns
 * placeholder data so we can test the full UI flow.
 */

interface MockField {
  key: string;
  label: string;
  value: string;
  category: string;
  lineNumber: string;
}

/**
 * Generate Schedule A (Itemized Deductions) fields.
 * Used when taxpayer itemizes instead of taking standard deduction.
 */
function generateScheduleA(totalIncome: number): MockField[] {
  // Generate realistic itemized deduction amounts
  const medical = Math.round(totalIncome * 0.02 + Math.random() * 2000);
  const salt = Math.min(10000, Math.round(totalIncome * 0.05 + Math.random() * 3000)); // SALT cap
  const mortgageInterest = Math.round(8000 + Math.random() * 12000);
  const charity = Math.round(totalIncome * 0.03 + Math.random() * 2000);
  const total = medical + salt + mortgageInterest + charity;

  return [
    { key: "sched_a_medical", label: "Medical and dental expenses", value: medical.toString(), category: "schedule_a", lineNumber: "1" },
    { key: "sched_a_salt", label: "State and local taxes (SALT)", value: salt.toString(), category: "schedule_a", lineNumber: "5d" },
    { key: "sched_a_mortgage_interest", label: "Home mortgage interest", value: mortgageInterest.toString(), category: "schedule_a", lineNumber: "8a" },
    { key: "sched_a_charity", label: "Gifts to charity", value: charity.toString(), category: "schedule_a", lineNumber: "11" },
    { key: "sched_a_total", label: "Total itemized deductions", value: total.toString(), category: "schedule_a", lineNumber: "17" },
  ];
}

/**
 * Generate Schedule C (Self-Employment) fields.
 * Used when taxpayer has self-employment income.
 */
function generateScheduleC(): MockField[] {
  const grossReceipts = Math.round(30000 + Math.random() * 50000);
  const cogs = Math.round(grossReceipts * 0.2);
  const grossProfit = grossReceipts - cogs;
  const expenses = Math.round(grossProfit * 0.3 + Math.random() * 5000);
  const netProfit = grossProfit - expenses;

  return [
    { key: "sched_c_gross_receipts", label: "Gross receipts or sales", value: grossReceipts.toString(), category: "schedule_c", lineNumber: "1" },
    { key: "sched_c_cogs", label: "Cost of goods sold", value: cogs.toString(), category: "schedule_c", lineNumber: "4" },
    { key: "sched_c_gross_profit", label: "Gross profit", value: grossProfit.toString(), category: "schedule_c", lineNumber: "5" },
    { key: "sched_c_expenses", label: "Total expenses", value: expenses.toString(), category: "schedule_c", lineNumber: "28" },
    { key: "sched_c_net_profit", label: "Net profit (or loss)", value: netProfit.toString(), category: "schedule_c", lineNumber: "31" },
  ];
}

/**
 * Generate Schedule D (Capital Gains/Losses) fields.
 * Used when taxpayer has investment transactions.
 */
function generateScheduleD(): MockField[] {
  // Generate mix of gains/losses
  const shortTermGain = Math.round((Math.random() - 0.3) * 5000);
  const longTermGain = Math.round((Math.random() - 0.2) * 15000);
  const netGain = shortTermGain + longTermGain;
  const carryover = netGain < 0 ? Math.min(3000, Math.abs(netGain)) : 0;

  return [
    { key: "sched_d_short_term", label: "Short-term capital gain/loss", value: shortTermGain.toString(), category: "schedule_d", lineNumber: "7" },
    { key: "sched_d_long_term", label: "Long-term capital gain/loss", value: longTermGain.toString(), category: "schedule_d", lineNumber: "15" },
    { key: "sched_d_net", label: "Net capital gain (or loss)", value: netGain.toString(), category: "schedule_d", lineNumber: "16" },
    { key: "sched_d_carryover", label: "Capital loss carryover", value: carryover.toString(), category: "schedule_d", lineNumber: "21" },
  ];
}

/**
 * Determine which schedules to include based on mock taxpayer profile.
 * Higher income = more likely to have itemized deductions.
 * Some randomness to simulate variety in tax situations.
 */
function determineTaxpayerProfile(totalIncome: number): {
  hasScheduleA: boolean;
  hasScheduleC: boolean;
  hasScheduleD: boolean;
} {
  // Higher income taxpayers more likely to itemize (Schedule A)
  const itemizeProbability = totalIncome > 100000 ? 0.6 : totalIncome > 75000 ? 0.4 : 0.2;
  const hasScheduleA = Math.random() < itemizeProbability;

  // Self-employment less common (~15% of taxpayers)
  const hasScheduleC = Math.random() < 0.15;

  // Investment income more common for higher earners
  const investProbability = totalIncome > 80000 ? 0.5 : 0.25;
  const hasScheduleD = Math.random() < investProbability;

  return { hasScheduleA, hasScheduleC, hasScheduleD };
}

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

  // Determine taxpayer profile and schedules
  const profile = determineTaxpayerProfile(totalIncome);

  // Use itemized or standard deduction
  const standardDeduction = 14600;
  let deduction = standardDeduction;
  let deductionLabel = "Standard deduction";

  // Build Form 1040 fields
  const form1040Fields: MockField[] = [
    { key: "wages", label: "Wages, salaries, tips", value: totalIncome.toString(), category: "income", lineNumber: "1a" },
    { key: "total_income", label: "Total income", value: totalIncome.toString(), category: "income", lineNumber: "9" },
    { key: "adjustments", label: "Adjustments to income", value: adjustments.toString(), category: "adjustments", lineNumber: "10" },
    { key: "agi", label: "Adjusted gross income", value: agi.toString(), category: "adjustments", lineNumber: "11" },
  ];

  // Add schedule fields
  const scheduleFields: MockField[] = [];

  if (profile.hasScheduleA) {
    const schedAFields = generateScheduleA(totalIncome);
    scheduleFields.push(...schedAFields);
    // Use itemized deduction if greater than standard
    const itemizedTotal = parseInt(schedAFields.find(f => f.key === "sched_a_total")?.value || "0");
    if (itemizedTotal > standardDeduction) {
      deduction = itemizedTotal;
      deductionLabel = "Itemized deductions (from Schedule A)";
    }
  }

  if (profile.hasScheduleC) {
    scheduleFields.push(...generateScheduleC());
  }

  if (profile.hasScheduleD) {
    scheduleFields.push(...generateScheduleD());
  }

  const taxableIncome = Math.max(0, agi - deduction);
  const totalTax = Math.round(taxableIncome * taxRate);
  const payments = totalTax + Math.round((Math.random() - 0.3) * 3000);
  const refund = payments > totalTax ? payments - totalTax : 0;
  const owed = totalTax > payments ? totalTax - payments : 0;

  // Add remaining Form 1040 fields
  form1040Fields.push(
    { key: "deduction", label: deductionLabel, value: deduction.toString(), category: "deductions", lineNumber: "12" },
    { key: "taxable_income", label: "Taxable income", value: taxableIncome.toString(), category: "deductions", lineNumber: "15" },
    { key: "total_tax", label: "Total tax", value: totalTax.toString(), category: "tax_computation", lineNumber: "24" },
    { key: "total_payments", label: "Total payments", value: payments.toString(), category: "payments", lineNumber: "33" },
    { key: "refund", label: "Refund", value: refund.toString(), category: "refund_owed", lineNumber: "34" },
    { key: "amount_owed", label: "Amount owed", value: owed.toString(), category: "refund_owed", lineNumber: "37" },
  );

  return {
    year,
    filingStatus: "Single",
    extractionMethod: "mock",
    fields: [...form1040Fields, ...scheduleFields],
  };
}
