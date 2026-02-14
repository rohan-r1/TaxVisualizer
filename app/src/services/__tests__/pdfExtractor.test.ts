/**
 * Tests for the PDF Extractor service
 *
 * Note: These tests mock the Tauri shell plugin since we can't run the
 * actual sidecar in a test environment.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock the Tauri shell plugin
vi.mock("@tauri-apps/plugin-shell", () => ({
  Command: {
    sidecar: vi.fn(),
  },
}));

import { Command } from "@tauri-apps/plugin-shell";
import {
  extractPdf,
  getSupportedYears,
  checkSidecarAvailable,
  type ExtractionResult,
} from "../pdfExtractor";

describe("pdfExtractor", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("extractPdf", () => {
    it("should extract fields from a PDF successfully", async () => {
      const mockResult: ExtractionResult = {
        year: 2018,
        filing_status: "Married Filing Jointly",
        extraction_method: "pdfplumber",
        fields: [
          {
            key: "total_income",
            label: "Total income",
            value: "30262",
            category: "income",
            line_number: "1",
            confidence: 0.9,
            page: 1,
          },
          {
            key: "total_tax",
            label: "Total tax",
            value: "46014",
            category: "tax_computation",
            line_number: "6",
            confidence: 0.9,
            page: 1,
          },
        ],
        page_count: 2,
      };

      const mockExecute = vi.fn().mockResolvedValue({
        code: 0,
        stdout: JSON.stringify(mockResult),
        stderr: "",
      });

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue({
        execute: mockExecute,
      });

      const result = await extractPdf("/path/to/test.pdf");

      expect(Command.sidecar).toHaveBeenCalledWith("binaries/extract", [
        "/path/to/test.pdf",
      ]);
      expect(result.year).toBe(2018);
      expect(result.filing_status).toBe("Married Filing Jointly");
      expect(result.fields).toHaveLength(2);
      expect(result.fields[0].key).toBe("total_income");
    });

    it("should handle extraction errors", async () => {
      const mockExecute = vi.fn().mockResolvedValue({
        code: 1,
        stdout: "",
        stderr: "File not found",
      });

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue({
        execute: mockExecute,
      });

      const result = await extractPdf("/nonexistent.pdf");

      expect(result.error).toBe("File not found");
      expect(result.year).toBe(0);
      expect(result.fields).toHaveLength(0);
    });

    it("should handle JSON parse errors", async () => {
      const mockExecute = vi.fn().mockResolvedValue({
        code: 0,
        stdout: "not valid json",
        stderr: "",
      });

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue({
        execute: mockExecute,
      });

      const result = await extractPdf("/path/to/test.pdf");

      expect(result.error).toBeDefined();
      expect(result.year).toBe(0);
    });
  });

  describe("getSupportedYears", () => {
    it("should return list of supported years", async () => {
      const mockExecute = vi.fn().mockResolvedValue({
        code: 0,
        stdout: JSON.stringify({
          supported_years: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
        }),
        stderr: "",
      });

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue({
        execute: mockExecute,
      });

      const years = await getSupportedYears();

      expect(Command.sidecar).toHaveBeenCalledWith("binaries/extract", [
        "--years",
      ]);
      expect(years).toEqual([2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]);
    });

    it("should return empty array on error", async () => {
      const mockExecute = vi.fn().mockResolvedValue({
        code: 1,
        stdout: "",
        stderr: "Error",
      });

      (Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue({
        execute: mockExecute,
      });

      const years = await getSupportedYears();

      expect(years).toEqual([]);
    });
  });

  describe("checkSidecarAvailable", () => {
    it("should return true when sidecar is available", async () => {
      const mockExecute = vi.fn().mockResolvedValue({
        code: 0,
        stdout: JSON.stringify({ supported_years: [2018] }),
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
