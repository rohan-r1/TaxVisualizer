import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";
import * as database from "./db/database";
import { makeReturn, makeFieldSet } from "./test/fixtures";

// Mock the database module
vi.mock("./db/database", async () => {
  const actual = await vi.importActual<typeof import("./db/database")>("./db/database");
  return {
    ...actual,
    getAllReturns: vi.fn(),
    getAllFields: vi.fn(),
    insertReturn: vi.fn(),
    insertFieldsBatch: vi.fn(),
    deleteReturn: vi.fn(),
  };
});

// Mock the dialog
vi.mock("@tauri-apps/plugin-dialog", () => ({
  open: vi.fn(),
}));

// Mock pdfExtraction to avoid pdfjs-dist DOMMatrix error in Node
vi.mock("./services/pdfExtraction", () => ({
  extractFromPdf: vi.fn().mockRejectedValue(new Error("Mock: use sidecar")),
}));

// Mock pdfExtractor sidecar
vi.mock("./services/pdfExtractor", () => ({
  checkSidecarAvailable: vi.fn().mockResolvedValue(true),
  extractPdf: vi.fn().mockResolvedValue({
    year: 2023,
    filing_status: "Single",
    extraction_method: "pdfplumber",
    fields: [
      { key: "total_income", label: "Total income", value: "75000", category: "income", line_number: "9", confidence: 1.0 },
      { key: "agi", label: "Adjusted gross income", value: "72000", category: "income", line_number: "11", confidence: 1.0 },
      { key: "total_tax", label: "Total tax", value: "8500", category: "tax_computation", line_number: "24", confidence: 1.0 },
    ],
  }),
}));

const mockedDb = vi.mocked(database);

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading state initially", () => {
    // Never resolve to keep loading state
    mockedDb.getAllReturns.mockReturnValue(new Promise(() => {}));
    mockedDb.getAllFields.mockReturnValue(new Promise(() => {}));

    render(<App />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders header with app title after loading", async () => {
    mockedDb.getAllReturns.mockResolvedValue([]);
    mockedDb.getAllFields.mockResolvedValue({});

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("TaxVisualizer")).toBeInTheDocument();
    });
  });

  it("shows empty state when no returns exist", async () => {
    mockedDb.getAllReturns.mockResolvedValue([]);
    mockedDb.getAllFields.mockResolvedValue({});

    render(<App />);

    await waitFor(() => {
      expect(
        screen.getByText("No tax returns uploaded yet")
      ).toBeInTheDocument();
    });
  });

  it("renders upload button in header", async () => {
    mockedDb.getAllReturns.mockResolvedValue([]);
    mockedDb.getAllFields.mockResolvedValue({});

    render(<App />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /upload tax return/i })
      ).toBeInTheDocument();
    });
  });

  it("renders sidebar with returns list when data exists", async () => {
    const returns = [makeReturn({ id: 1, tax_year: 2023 })];
    mockedDb.getAllReturns.mockResolvedValue(returns);
    mockedDb.getAllFields.mockResolvedValue({
      1: makeFieldSet(1),
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getAllByText("2023").length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText("Uploaded Returns")).toBeInTheDocument();
    });
  });

  it("shows error banner when loading fails", async () => {
    mockedDb.getAllReturns.mockRejectedValue(new Error("Database error"));
    mockedDb.getAllFields.mockResolvedValue({});

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Database error")).toBeInTheDocument();
    });
  });

  it("dismisses error banner when dismiss button is clicked", async () => {
    const user = userEvent.setup();
    mockedDb.getAllReturns.mockRejectedValue(new Error("Database error"));
    mockedDb.getAllFields.mockResolvedValue({});

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Database error")).toBeInTheDocument();
    });

    await user.click(screen.getByText("dismiss"));

    expect(screen.queryByText("Database error")).not.toBeInTheDocument();
  });

  it("shows duplicate year error message for UNIQUE constraint violation", async () => {
    mockedDb.getAllReturns.mockResolvedValue([]);
    mockedDb.getAllFields.mockResolvedValue({});
    mockedDb.insertReturn.mockRejectedValue(
      new Error("UNIQUE constraint failed")
    );

    // Import and mock the dialog
    const { open } = await import("@tauri-apps/plugin-dialog");
    vi.mocked(open).mockResolvedValue("/path/to/1040_2023.pdf" as any);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /upload tax return/i })).toBeInTheDocument();
    });

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /upload tax return/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/already exists.*delete it first/i)
      ).toBeInTheDocument();
    });
  });

  it("calls deleteReturn and refreshes when delete is triggered", async () => {
    const returns = [makeReturn({ id: 1, tax_year: 2023 })];
    mockedDb.getAllReturns
      .mockResolvedValueOnce(returns) // initial load
      .mockResolvedValueOnce([]); // after delete
    mockedDb.getAllFields.mockResolvedValue({
      1: makeFieldSet(1),
    });
    mockedDb.deleteReturn.mockResolvedValue(undefined);

    render(<App />);

    await waitFor(() => {
      expect(screen.getAllByText("2023").length).toBeGreaterThanOrEqual(1);
    });

    const user = userEvent.setup();
    await user.click(screen.getByTitle("Delete this return"));

    expect(mockedDb.deleteReturn).toHaveBeenCalledWith(1);
  });

  it("renders the dashboard with key numbers when data is loaded", async () => {
    const returns = [makeReturn({ id: 1, tax_year: 2023 })];
    const fields = { 1: makeFieldSet(1) };
    mockedDb.getAllReturns.mockResolvedValue(returns);
    mockedDb.getAllFields.mockResolvedValue(fields);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Total Income")).toBeInTheDocument();
    });
  });
});
