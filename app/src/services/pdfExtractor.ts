/**
 * PDF Extraction Service
 *
 * Invokes the Python sidecar to extract Form 1040 data from PDFs.
 * Uses pdfplumber for coordinate-based extraction with year-specific mappings.
 */

import { Command } from "@tauri-apps/plugin-shell";

/**
 * Extracted field from a Form 1040
 */
export interface ExtractedField {
  key: string;
  label: string;
  value: string | null;
  category: string;
  line_number: string;
  confidence: number;
  page: number;
}

/**
 * Result from PDF extraction
 */
export interface ExtractionResult {
  year: number;
  filing_status: string;
  extraction_method: string;
  fields: ExtractedField[];
  page_count?: number;
  detected_forms?: string[];
  error?: string;
  supported_years?: number[];
}

/**
 * Extract Form 1040 data from a PDF file.
 *
 * @param pdfPath - Absolute path to the PDF file
 * @returns Extraction result with year, filing status, and fields
 */
export async function extractPdf(pdfPath: string): Promise<ExtractionResult> {
  try {
    // Spawn the sidecar with the PDF path as argument
    const command = Command.sidecar("binaries/extract", [pdfPath]);

    const output = await command.execute();

    // Check for errors
    if (output.code !== 0) {
      const errorMsg = output.stderr || `Extraction failed with code ${output.code}`;
      console.error("PDF extraction error:", errorMsg);
      return {
        year: 0,
        filing_status: "Unknown",
        extraction_method: "pdfplumber",
        fields: [],
        error: errorMsg,
      };
    }

    // Parse the JSON output from stdout
    // Note: stderr may contain warnings (like font warnings) that we can ignore
    const result: ExtractionResult = JSON.parse(output.stdout);

    return result;
  } catch (error) {
    console.error("PDF extraction error:", error);
    return {
      year: 0,
      filing_status: "Unknown",
      extraction_method: "pdfplumber",
      fields: [],
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

/**
 * Get the list of supported form years.
 *
 * @returns Array of supported years (e.g., [2018, 2019, 2020, ...])
 */
export async function getSupportedYears(): Promise<number[]> {
  try {
    const command = Command.sidecar("binaries/extract", ["--years"]);
    const output = await command.execute();

    if (output.code !== 0) {
      console.error("Failed to get supported years:", output.stderr);
      return [];
    }

    const result = JSON.parse(output.stdout);
    return result.supported_years || [];
  } catch (error) {
    console.error("Failed to get supported years:", error);
    return [];
  }
}

/**
 * Check if the extraction sidecar is available and working.
 *
 * @returns true if the sidecar is available
 */
export async function checkSidecarAvailable(): Promise<boolean> {
  try {
    const years = await getSupportedYears();
    return years.length > 0;
  } catch {
    return false;
  }
}
