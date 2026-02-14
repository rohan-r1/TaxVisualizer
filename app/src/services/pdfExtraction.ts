/**
 * PDF Extraction Service
 *
 * Extracts text from PDF files and parses Form 1040 data.
 * Uses pdfjs-dist for text extraction.
 *
 * Tier 1: Detects if PDF is digital (has text) or scanned (no text)
 * Tier 2: Extracts and parses text from digital PDFs
 */

import * as pdfjsLib from "pdfjs-dist";

// Set up the worker for pdfjs-dist
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.mjs",
  import.meta.url
).toString();

export interface ExtractedField {
  key: string;
  label: string;
  value: string;
  category: string;
  lineNumber: string;
  confidence: number;
}

export interface ExtractionResult {
  year: number;
  filingStatus: string;
  extractionMethod: "pdfjs" | "mock" | "scanned_unsupported";
  fields: ExtractedField[];
  isScanned: boolean;
  rawText?: string;
}

/**
 * Minimum characters per page to consider a PDF as having extractable text.
 * Below this threshold, we consider it a scanned PDF.
 */
const MIN_CHARS_PER_PAGE = 100;

/**
 * Extract text from all pages of a PDF.
 */
async function extractTextFromPdf(pdfData: ArrayBuffer): Promise<{ text: string; pageCount: number }> {
  const pdf = await pdfjsLib.getDocument({ data: pdfData }).promise;
  const pageCount = pdf.numPages;
  const textParts: string[] = [];

  for (let i = 1; i <= pageCount; i++) {
    const page = await pdf.getPage(i);
    const textContent = await page.getTextContent();
    const pageText = textContent.items
      .map((item) => ("str" in item ? item.str : ""))
      .join(" ");
    textParts.push(pageText);
  }

  return {
    text: textParts.join("\n\n--- PAGE BREAK ---\n\n"),
    pageCount,
  };
}

/**
 * Detect if a PDF is digital (has embedded text) or scanned (image-based).
 */
function detectPdfType(text: string, pageCount: number): boolean {
  const avgCharsPerPage = text.length / pageCount;
  return avgCharsPerPage < MIN_CHARS_PER_PAGE;
}

/**
 * Parse the tax year from the extracted text.
 * Looks for patterns like "Form 1040 2023" or "Tax Year 2023".
 */
function parseYear(text: string, filename: string): number {
  // Try to find year in form header (e.g., "Form 1040 2023" or "Form 1040-SR 2022")
  const form1040Match = text.match(/Form\s*1040[-A-Z]*\s*(20\d{2})/i);
  if (form1040Match) {
    return parseInt(form1040Match[1]);
  }

  // Try to find "Tax Year XXXX"
  const taxYearMatch = text.match(/Tax\s*Year\s*(20\d{2})/i);
  if (taxYearMatch) {
    return parseInt(taxYearMatch[1]);
  }

  // Fallback: look for any 20XX year in filename
  const filenameMatch = filename.match(/20\d{2}/);
  if (filenameMatch) {
    return parseInt(filenameMatch[0]);
  }

  // Default to current year
  return new Date().getFullYear();
}

/**
 * Parse filing status from the extracted text.
 */
function parseFilingStatus(text: string): string {
  const statusPatterns = [
    { pattern: /Single/i, status: "Single" },
    { pattern: /Married\s+filing\s+jointly/i, status: "Married Filing Jointly" },
    { pattern: /Married\s+filing\s+separately/i, status: "Married Filing Separately" },
    { pattern: /Head\s+of\s+household/i, status: "Head of Household" },
    { pattern: /Qualifying\s+(widow|surviving\s+spouse)/i, status: "Qualifying Surviving Spouse" },
  ];

  for (const { pattern, status } of statusPatterns) {
    if (pattern.test(text)) {
      return status;
    }
  }

  return "Single"; // Default
}

/**
 * Parse a currency value from text, handling various formats.
 */
function parseCurrency(text: string): number | null {
  if (!text) return null;

  // Remove common formatting
  const cleaned = text
    .replace(/[$,]/g, "")
    .replace(/\s+/g, "")
    .replace(/\(([0-9.]+)\)/, "-$1"); // Handle parentheses for negatives

  const parsed = parseFloat(cleaned);
  return isNaN(parsed) ? null : Math.round(parsed);
}

/**
 * Minimum value threshold - values below this are likely line numbers, not dollar amounts.
 * Most tax return values (income, deductions, etc.) are at least $100.
 */
const MIN_VALUE_THRESHOLD = 100;

/**
 * Form 1040 field patterns - regex patterns to extract specific line items.
 *
 * Key insight: Form 1040 PDFs often have values at the END of lines, or after the
 * line number appears a second time. We look for larger numbers (4+ digits) to
 * avoid matching line numbers like "1a", "2b", etc.
 */
const FORM_1040_PATTERNS: Array<{
  key: string;
  label: string;
  category: string;
  lineNumber: string;
  patterns: RegExp[];
}> = [
  // Income - wages are on line 1 (varies by year: 1, 1a, 1z)
  {
    key: "wages",
    label: "Wages, salaries, tips",
    category: "income",
    lineNumber: "1",
    patterns: [
      // Look for "1" or "1a" followed by wages label, then a large number at end
      /Wages.*?salaries.*?tips[^\d]*(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
      // Look for W-2 reference followed by amount
      /W-2[^\d]*(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
      // Generic: find line 1 with a 4+ digit number nearby
      /\b1[az]?\b[^\d]{0,50}(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
    ],
  },
  {
    key: "interest_income",
    label: "Interest income",
    category: "income",
    lineNumber: "2b",
    patterns: [
      /Taxable\s+interest[^\d]*(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
      /\b2b\b[^\d]{0,30}(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
    ],
  },
  {
    key: "dividend_income",
    label: "Ordinary dividends",
    category: "income",
    lineNumber: "3b",
    patterns: [
      /Ordinary\s+dividends[^\d]*(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
      /\b3b\b[^\d]{0,30}(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
    ],
  },
  {
    key: "total_income",
    label: "Total income",
    category: "income",
    lineNumber: "9",
    patterns: [
      // "Total income" followed by a large number
      /Total\s+income[^\d]*(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
      // Line 9 (or 7b in older forms) with large number
      /\b(?:9|7b)\b[^\d]{0,20}(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
    ],
  },
  // Adjustments
  {
    key: "adjustments",
    label: "Adjustments to income",
    category: "adjustments",
    lineNumber: "10",
    patterns: [
      /[Aa]djustments?\s+to\s+income[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
      /\b10\b[^\d]{0,30}[Aa]djust[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
    ],
  },
  {
    key: "agi",
    label: "Adjusted gross income",
    category: "adjustments",
    lineNumber: "11",
    patterns: [
      // AGI label followed by large number
      /[Aa]djusted\s+[Gg]ross\s+[Ii]ncome[^\d]*(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
      // Just "AGI" followed by number
      /\bAGI\b[^\d]{0,20}(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
      // Line 11 (or 8b in older forms)
      /\b(?:11|8b)\b[^\d]{0,50}(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
    ],
  },
  // Deductions
  {
    key: "deduction",
    label: "Standard/Itemized deduction",
    category: "deductions",
    lineNumber: "12",
    patterns: [
      /[Ss]tandard\s+[Dd]eduction[^\d]*(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
      /[Ii]temized\s+[Dd]eductions[^\d]*(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
      /\b12\b[^\d]{0,30}[Dd]eduction[^\d]*(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
    ],
  },
  {
    key: "taxable_income",
    label: "Taxable income",
    category: "deductions",
    lineNumber: "15",
    patterns: [
      /[Tt]axable\s+[Ii]ncome[^\d]*(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
      /\b(?:15|11b)\b[^\d]{0,30}[Tt]axable[^\d]*(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?/i,
    ],
  },
  // Tax computation
  {
    key: "total_tax",
    label: "Total tax",
    category: "tax_computation",
    lineNumber: "24",
    patterns: [
      /[Tt]otal\s+[Tt]ax[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
      /\b(?:24|16)\b[^\d]{0,30}[Tt]ax[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
    ],
  },
  // Payments
  {
    key: "total_payments",
    label: "Total payments",
    category: "payments",
    lineNumber: "33",
    patterns: [
      /[Tt]otal\s+(?:[Oo]ther\s+)?[Pp]ayments[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
      /\b(?:33|19)\b[^\d]{0,30}[Pp]ayment[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
    ],
  },
  {
    key: "federal_withholding",
    label: "Federal income tax withheld",
    category: "payments",
    lineNumber: "25d",
    patterns: [
      /[Ff]ederal.*?[Tt]ax\s+[Ww]ithheld[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
      /\b25d?\b[^\d]{0,30}[Ww]ithheld[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
    ],
  },
  // Refund/Owed
  {
    key: "refund",
    label: "Refund",
    category: "refund_owed",
    lineNumber: "34",
    patterns: [
      /[Oo]verpaid[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
      /[Rr]efund[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
      /\b(?:34|20)\b[^\d]{0,30}(?:[Oo]verpaid|[Rr]efund)[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
    ],
  },
  {
    key: "amount_owed",
    label: "Amount owed",
    category: "refund_owed",
    lineNumber: "37",
    patterns: [
      /[Aa]mount\s+[Yy]ou\s+[Oo]we[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
      /\b(?:37|22)\b[^\d]{0,30}[Oo]we[^\d]*(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?/i,
    ],
  },
];

/**
 * Extract Form 1040 fields from the PDF text.
 */
function extractForm1040Fields(text: string): ExtractedField[] {
  const fields: ExtractedField[] = [];

  for (const fieldDef of FORM_1040_PATTERNS) {
    let value: string | null = null;
    let confidence = 0;
    let matchedPattern: string | null = null;

    // Try each pattern until we find a valid match
    for (const pattern of fieldDef.patterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        const parsed = parseCurrency(match[1]);
        // Only accept values >= threshold to avoid matching line numbers
        if (parsed !== null && parsed >= MIN_VALUE_THRESHOLD) {
          value = parsed.toString();
          // Higher confidence for more specific patterns (earlier in array)
          confidence = 0.95 - (fieldDef.patterns.indexOf(pattern) * 0.05);
          matchedPattern = pattern.toString();
          break;
        }
      }
    }

    if (value !== null) {
      console.log(`Matched ${fieldDef.key}: ${value} using pattern: ${matchedPattern}`);
      fields.push({
        key: fieldDef.key,
        label: fieldDef.label,
        value,
        category: fieldDef.category,
        lineNumber: fieldDef.lineNumber,
        confidence,
      });
    }
  }

  return fields;
}

/**
 * Read a local file as ArrayBuffer.
 * Uses Tauri's fs API to read the file.
 */
async function readLocalFile(path: string): Promise<ArrayBuffer> {
  // In Tauri, we need to use the fs plugin to read local files
  const { readFile } = await import("@tauri-apps/plugin-fs");
  const contents = await readFile(path);
  return contents.buffer as ArrayBuffer;
}

/**
 * Main extraction function.
 * Takes a local file path, reads the PDF, and extracts tax data.
 */
export async function extractFromPdf(
  path: string,
  filename: string
): Promise<ExtractionResult> {
  try {
    // Read the PDF file
    const pdfData = await readLocalFile(path);

    // Extract text from PDF
    const { text, pageCount } = await extractTextFromPdf(pdfData);

    // DEBUG: Log extracted text to help diagnose extraction issues
    console.log("=== PDF EXTRACTION DEBUG ===");
    console.log("Filename:", filename);
    console.log("Page count:", pageCount);
    console.log("Text length:", text.length);
    console.log("First 2000 chars of extracted text:");
    console.log(text.substring(0, 2000));
    console.log("=== END DEBUG ===");

    // Detect if this is a scanned PDF
    const isScanned = detectPdfType(text, pageCount);

    if (isScanned) {
      // For MVP, we don't support scanned PDFs
      // Return a result indicating scanned PDF was detected
      const year = parseYear(text, filename);
      return {
        year,
        filingStatus: "Unknown",
        extractionMethod: "scanned_unsupported",
        fields: [],
        isScanned: true,
        rawText: text,
      };
    }

    // Parse year and filing status
    const year = parseYear(text, filename);
    const filingStatus = parseFilingStatus(text);

    // Extract Form 1040 fields
    const fields = extractForm1040Fields(text);

    // DEBUG: Log extracted fields
    console.log("=== EXTRACTED FIELDS ===");
    fields.forEach(f => console.log(`${f.key}: ${f.value} (confidence: ${f.confidence})`));
    console.log("=== END FIELDS ===");

    return {
      year,
      filingStatus,
      extractionMethod: "pdfjs",
      fields,
      isScanned: false,
      rawText: text,
    };
  } catch (error) {
    console.error("PDF extraction failed:", error);
    throw new Error(
      `Failed to extract data from PDF: ${error instanceof Error ? error.message : String(error)}`
    );
  }
}

/**
 * Check if a PDF is likely a tax form.
 * Useful for validating uploads before processing.
 */
export function isTaxForm(text: string): boolean {
  const taxFormIndicators = [
    /Form\s*1040/i,
    /U\.?S\.?\s+Individual\s+Income\s+Tax\s+Return/i,
    /Department\s+of\s+the\s+Treasury/i,
    /Internal\s+Revenue\s+Service/i,
    /IRS/i,
  ];

  return taxFormIndicators.some((pattern) => pattern.test(text));
}
