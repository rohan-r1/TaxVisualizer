/**
 * PDF Extraction Service
 *
 * Invokes the Python sidecar to extract Form 1040 data from PDFs.
 * Uses PaddleOCR for text extraction with label-based field mapping.
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
  page?: number;
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
  form_1040_page?: number;
}

/**
 * Progress information during extraction
 */
export interface ExtractionProgress {
  stage: "opening" | "rendering" | "ocr" | "extracting" | "complete";
  current?: number;
  total?: number;
  message?: string;
}

/**
 * Parse a progress message from stderr.
 * Format: PROGRESS:stage:data
 *
 * Examples:
 *   PROGRESS:pages:10
 *   PROGRESS:rendering:3/10
 *   PROGRESS:ocr:5/10
 *   PROGRESS:extracting:Form 1040
 *   PROGRESS:complete:450 text blocks
 */
function parseProgressMessage(line: string): ExtractionProgress | null {
  if (!line.startsWith("PROGRESS:")) {
    return null;
  }

  const parts = line.substring(9).split(":");
  if (parts.length < 1) {
    return null;
  }

  const stage = parts[0];
  const data = parts.slice(1).join(":");

  switch (stage) {
    case "opening":
      return { stage: "opening", message: `Opening ${data}` };

    case "pages":
      return {
        stage: "rendering",
        current: 0,
        total: parseInt(data, 10),
        message: `Found ${data} pages`,
      };

    case "rendering": {
      const [current, total] = data.split("/").map((x) => parseInt(x, 10));
      return {
        stage: "rendering",
        current,
        total,
        message: `Rendering page ${current} of ${total}`,
      };
    }

    case "loading_ocr":
      return { stage: "ocr", message: "Loading OCR model..." };

    case "ocr": {
      const [current, total] = data.split("/").map((x) => parseInt(x, 10));
      return {
        stage: "ocr",
        current,
        total,
        message: `OCR processing page ${current} of ${total}`,
      };
    }

    case "detected_form_pages":
      return {
        stage: "extracting",
        message: `Detected form pages: ${data}`,
      };

    case "extracting":
      return {
        stage: "extracting",
        message: `Extracting fields from ${data}`,
      };

    case "complete":
      return {
        stage: "complete",
        message: `Extraction complete: ${data}`,
      };

    default:
      return null;
  }
}

/**
 * Extract Form 1040 data from a PDF file.
 *
 * @param pdfPath - Absolute path to the PDF file
 * @param onProgress - Optional callback for progress updates
 * @returns Extraction result with year, filing status, and fields
 */
export async function extractPdf(
  pdfPath: string,
  onProgress?: (progress: ExtractionProgress) => void
): Promise<ExtractionResult> {
  return new Promise((resolve) => {
    try {
      // Spawn the sidecar with the PDF path as argument
      const command = Command.sidecar("binaries/extract", [pdfPath]);

      let stdout = "";
      let stderr = "";

      // Handle stdout (JSON result)
      command.stdout.on("data", (data) => {
        stdout += data;
      });

      // Handle stderr (progress messages)
      command.stderr.on("data", (data) => {
        stderr += data;

        // Parse progress messages line by line
        const lines = data.split("\n");
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed && onProgress) {
            const progress = parseProgressMessage(trimmed);
            if (progress) {
              onProgress(progress);
            }
          }
        }
      });

      // Handle process exit
      command.on("close", (event) => {
        if (event.code !== 0) {
          console.error("PDF extraction error:", stderr);
          resolve({
            year: 0,
            filing_status: "Unknown",
            extraction_method: "paddleocr",
            fields: [],
            error: stderr || `Extraction failed with code ${event.code}`,
          });
          return;
        }

        try {
          // Parse the JSON output from stdout
          const result: ExtractionResult = JSON.parse(stdout);
          resolve(result);
        } catch (parseError) {
          console.error("Failed to parse extraction result:", parseError);
          console.error("Raw stdout:", stdout);
          resolve({
            year: 0,
            filing_status: "Unknown",
            extraction_method: "paddleocr",
            fields: [],
            error: `Failed to parse result: ${parseError}`,
          });
        }
      });

      command.on("error", (error) => {
        console.error("PDF extraction error:", error);
        resolve({
          year: 0,
          filing_status: "Unknown",
          extraction_method: "paddleocr",
          fields: [],
          error: String(error),
        });
      });

      // Spawn the process
      command.spawn();
    } catch (error) {
      console.error("PDF extraction error:", error);
      resolve({
        year: 0,
        filing_status: "Unknown",
        extraction_method: "paddleocr",
        fields: [],
        error: error instanceof Error ? error.message : String(error),
      });
    }
  });
}

/**
 * Check if the extraction sidecar is available and working.
 *
 * @returns true if the sidecar is available
 */
export async function checkSidecarAvailable(): Promise<boolean> {
  try {
    // Try a simple extraction with no file to see if sidecar responds
    const command = Command.sidecar("binaries/extract", ["--help"]);
    const output = await command.execute();
    // If it exits (even with error code), sidecar is available
    return output.code === 0 || output.code === 1;
  } catch {
    return false;
  }
}
