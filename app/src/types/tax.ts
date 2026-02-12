/** A single uploaded tax return */
export interface TaxReturn {
  id: number;
  tax_year: number;
  filing_status: string | null;
  pdf_path: string;
  pdf_filename: string;
  extraction_method: string | null;
  created_at: string;
  updated_at: string;
}

/** A single extracted field from a tax return */
export interface ExtractedField {
  id: number;
  return_id: number;
  field_key: string;
  field_label: string;
  field_value: string | null;
  field_type: string;
  category: string;
  line_number: string | null;
  confidence: number;
  needs_review: number;
}

/** Categories for organizing extracted fields */
export type FieldCategory =
  | "income"
  | "adjustments"
  | "deductions"
  | "tax_computation"
  | "credits"
  | "payments"
  | "refund_owed"
  | "filing_info";

/** Key numbers displayed in the MVP summary */
export interface ReturnSummary {
  tax_year: number;
  filing_status: string;
  total_income: number | null;
  agi: number | null;
  taxable_income: number | null;
  total_tax: number | null;
  total_payments: number | null;
  refund: number | null;
  amount_owed: number | null;
  effective_tax_rate: number | null;
}

/** Widget definition for the extensible widget system */
export interface WidgetConfig {
  id: string;
  title: string;
  component: React.ComponentType<WidgetProps>;
  /** Minimum number of returns needed to show this widget */
  minReturns?: number;
}

/** Props passed to every widget */
export interface WidgetProps {
  returns: TaxReturn[];
  fields: Record<number, ExtractedField[]>;
  summaries: ReturnSummary[];
}
