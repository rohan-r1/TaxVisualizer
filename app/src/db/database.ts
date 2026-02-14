import Database from "@tauri-apps/plugin-sql";
import type { TaxReturn, ExtractedField, ReturnSummary } from "../types/tax";

let db: Database | null = null;

export async function getDb(): Promise<Database> {
  if (!db) {
    db = await Database.load("sqlite:taxvisualizer.db");
  }
  return db;
}

// --- Tax Returns ---

export async function getAllReturns(): Promise<TaxReturn[]> {
  const d = await getDb();
  return d.select<TaxReturn[]>(
    "SELECT * FROM tax_returns ORDER BY tax_year DESC"
  );
}

export async function insertReturn(
  taxYear: number,
  pdfPath: string,
  pdfFilename: string,
  filingStatus?: string,
  extractionMethod?: string
): Promise<number> {
  const d = await getDb();
  const result = await d.execute(
    `INSERT INTO tax_returns (tax_year, pdf_path, pdf_filename, filing_status, extraction_method)
     VALUES ($1, $2, $3, $4, $5)`,
    [taxYear, pdfPath, pdfFilename, filingStatus ?? null, extractionMethod ?? null]
  );
  return result.lastInsertId ?? 0;
}

export async function deleteReturn(id: number): Promise<void> {
  const d = await getDb();
  await d.execute("DELETE FROM tax_returns WHERE id = $1", [id]);
}

// --- Extracted Fields ---

export async function getFieldsForReturn(
  returnId: number
): Promise<ExtractedField[]> {
  const d = await getDb();
  return d.select<ExtractedField[]>(
    "SELECT * FROM extracted_fields WHERE return_id = $1 ORDER BY category, field_key",
    [returnId]
  );
}

export async function getAllFields(): Promise<Record<number, ExtractedField[]>> {
  const d = await getDb();
  const rows = await d.select<ExtractedField[]>(
    "SELECT * FROM extracted_fields ORDER BY return_id, category, field_key"
  );
  const grouped: Record<number, ExtractedField[]> = {};
  for (const row of rows) {
    if (!grouped[row.return_id]) grouped[row.return_id] = [];
    grouped[row.return_id].push(row);
  }
  return grouped;
}

export async function insertField(
  returnId: number,
  fieldKey: string,
  fieldLabel: string,
  fieldValue: string | null,
  category: string,
  lineNumber?: string,
  fieldType: string = "number",
  confidence: number = 1.0
): Promise<void> {
  const d = await getDb();
  await d.execute(
    `INSERT OR REPLACE INTO extracted_fields
     (return_id, field_key, field_label, field_value, field_type, category, line_number, confidence, needs_review)
     VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
    [
      returnId,
      fieldKey,
      fieldLabel,
      fieldValue,
      fieldType,
      category,
      lineNumber ?? null,
      confidence,
      confidence < 0.95 ? 1 : 0,
    ]
  );
}

export async function insertFieldsBatch(
  returnId: number,
  fields: Array<{
    key: string;
    label: string;
    value: string | null;
    category: string;
    lineNumber?: string;
    fieldType?: string;
    confidence?: number;
  }>
): Promise<void> {
  for (const f of fields) {
    await insertField(
      returnId,
      f.key,
      f.label,
      f.value,
      f.category,
      f.lineNumber,
      f.fieldType ?? "number",
      f.confidence ?? 1.0
    );
  }
}

// --- Summaries ---

/** Build a ReturnSummary from extracted fields */
export function buildSummary(
  taxReturn: TaxReturn,
  fields: ExtractedField[]
): ReturnSummary {
  const get = (key: string): number | null => {
    const f = fields.find((f) => f.field_key === key);
    if (!f || f.field_value === null) return null;
    const n = parseFloat(f.field_value);
    return isNaN(n) ? null : n;
  };

  const totalIncome = get("total_income");
  const totalTax = get("total_tax");
  const effectiveRate =
    totalIncome && totalTax && totalIncome > 0
      ? (totalTax / totalIncome) * 100
      : null;

  return {
    tax_year: taxReturn.tax_year,
    filing_status: taxReturn.filing_status ?? "Unknown",
    total_income: totalIncome,
    agi: get("agi"),
    taxable_income: get("taxable_income"),
    total_tax: totalTax,
    total_payments: get("total_payments"),
    refund: get("refund"),
    amount_owed: get("amount_owed"),
    effective_tax_rate: effectiveRate
      ? Math.round(effectiveRate * 100) / 100
      : null,
  };
}
