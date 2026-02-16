/**
 * Tests for the PDF Extractor service
 *
 * Note: These tests mock the Tauri shell plugin since we can't run the
 * actual sidecar in a test environment.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { EventEmitter } from "events";

// Mock the Tauri shell plugin
vi.mock("@tauri-apps/plugin-shell", () => ({
  Command: {
    sidecar: vi.fn(),
  },
}));

import { Command } from "@tauri-apps/plugin-shell";
import {
  extractPdf,
  checkSidecarAvailable,
  type ExtractionResult,
} from "../pdfExtractor";

/**
 * Create a mock command that emits events for streaming output
 */
function createMockCommand(options: {
  stdout: string;
  stderr?: string;
  exitCode?: number;
}) {
  const command = new EventEmitter();
  const stdout = new EventEmitter();
  const stderr = new EventEmitter();

  // Attach stdout/stderr emitters
  (command as unknown as { stdout: EventEmitter }).stdout = stdout;
  (command as unknown as { stderr: EventEmitter }).stderr = stderr;

  // Mock spawn to trigger events
  (command as unknown as { spawn: () => void }).spawn = () => {
    // Emit stdout data
    if (options.stdout) {
      stdout.emit("data", options.stdout);
    }

    // Emit stderr data (progress messages)
    if (options.stderr) {
      stderr.emit("data", options.stderr);
    }

    // Emit close event
    setTimeout(() => {
      command.emit("close", { code: options.exitCode ?? 0 });
    }, 0);
  };

  return command;
}

describe("pdfExtractor", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("extractPdf", () => {
    it("should extract fields from a PDF successfully", async () => {
      const mockResult: ExtractionResult = {
        year: 2024,
        filing_status: "Married Filing Jointly",
        extraction_method: "paddleocr",
        fields: [
          {
            key: "total_income",
            label: "Total income",
            value: "135800",
            category: "income",
            line_number: "9",
            confidence: 0.98,
          },
          {
            key: "agi",
            label: "Adjusted gross income (AGI)",
            value: "120200",
            category: "adjustments",
            line_number: "11",
            confidence: 0.99,
          },
        ],
        page_count: 5,
      };

      const mockCommand = createMockCommand({
        stdout: JSON.stringify(mockResult),
        stderr: "PROGRESS:complete:150 text blocks\n",
      });

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue(
        mockCommand
      );

      const result = await extractPdf("/path/to/test.pdf");

      expect(Command.sidecar).toHaveBeenCalledWith("binaries/extract", [
        "/path/to/test.pdf",
      ]);
      expect(result.year).toBe(2024);
      expect(result.filing_status).toBe("Married Filing Jointly");
      expect(result.extraction_method).toBe("paddleocr");
      expect(result.fields).toHaveLength(2);
      expect(result.fields[0].key).toBe("total_income");
    });

    it("should call progress callback with progress updates", async () => {
      const mockResult: ExtractionResult = {
        year: 2024,
        filing_status: "Single",
        extraction_method: "paddleocr",
        fields: [],
        page_count: 2,
      };

      const mockCommand = createMockCommand({
        stdout: JSON.stringify(mockResult),
        stderr: "PROGRESS:ocr:1/2\nPROGRESS:ocr:2/2\nPROGRESS:complete:50 text blocks\n",
      });

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue(
        mockCommand
      );

      const progressUpdates: Array<{
        stage: string;
        current?: number;
        total?: number;
      }> = [];

      await extractPdf("/path/to/test.pdf", (progress) => {
        progressUpdates.push(progress);
      });

      expect(progressUpdates.length).toBeGreaterThan(0);
      // Check that we received OCR progress updates
      const ocrUpdates = progressUpdates.filter((p) => p.stage === "ocr");
      expect(ocrUpdates.length).toBe(2);
    });

    it("should handle extraction errors", async () => {
      const mockCommand = createMockCommand({
        stdout: "",
        stderr: "ERROR: File not found",
        exitCode: 1,
      });

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue(
        mockCommand
      );

      const result = await extractPdf("/nonexistent.pdf");

      expect(result.error).toContain("File not found");
      expect(result.year).toBe(0);
      expect(result.fields).toHaveLength(0);
    });

    it("should handle JSON parse errors", async () => {
      const mockCommand = createMockCommand({
        stdout: "not valid json",
        stderr: "",
      });

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue(
        mockCommand
      );

      const result = await extractPdf("/path/to/test.pdf");

      expect(result.error).toBeDefined();
      expect(result.error).toContain("Failed to parse result");
      expect(result.year).toBe(0);
    });

    it("should handle spawn errors", async () => {
      const command = new EventEmitter();
      const stdout = new EventEmitter();
      const stderr = new EventEmitter();

      (command as unknown as { stdout: EventEmitter }).stdout = stdout;
      (command as unknown as { stderr: EventEmitter }).stderr = stderr;
      (command as unknown as { spawn: () => void }).spawn = () => {
        setTimeout(() => {
          command.emit("error", new Error("Spawn failed"));
        }, 0);
      };

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue(command);

      const result = await extractPdf("/path/to/test.pdf");

      expect(result.error).toBeDefined();
      expect(result.year).toBe(0);
    });
  });

  describe("checkSidecarAvailable", () => {
    it("should return true when sidecar is available", async () => {
      const mockExecute = vi.fn().mockResolvedValue({
        code: 0,
        stdout: "Extract Form 1040 data from PDF files using PaddleOCR",
        stderr: "",
      });

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue({
        execute: mockExecute,
      });

      const available = await checkSidecarAvailable();

      expect(available).toBe(true);
    });

    it("should return true when sidecar exits with code 1 (no args)", async () => {
      const mockExecute = vi.fn().mockResolvedValue({
        code: 1,
        stdout: "",
        stderr: "",
      });

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue({
        execute: mockExecute,
      });

      const available = await checkSidecarAvailable();

      expect(available).toBe(true);
    });

    it("should return false when sidecar is not available", async () => {
      (Command.sidecar as ReturnType<typeof vi.fn>).mockImplementation(() => {
        throw new Error("Sidecar not found");
      });

      const available = await checkSidecarAvailable();

      expect(available).toBe(false);
    });
  });
});
