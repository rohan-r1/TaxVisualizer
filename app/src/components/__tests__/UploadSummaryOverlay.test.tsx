import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { UploadSummaryOverlay } from "../UploadSummary/UploadSummaryOverlay";

describe("UploadSummaryOverlay", () => {
  const defaultProps = {
    year: 2023,
    filingStatus: "Married Filing Jointly",
    formFieldCounts: [{ form: "Form 1040", count: 35 }],
    onContinue: vi.fn(),
    onReUpload: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the upload summary header with year", () => {
    render(<UploadSummaryOverlay {...defaultProps} />);

    expect(screen.getByText("Upload Summary")).toBeInTheDocument();
    expect(screen.getByText("2023")).toBeInTheDocument();
  });

  it("renders all detected forms with field counts", () => {
    render(
      <UploadSummaryOverlay
        {...defaultProps}
        formFieldCounts={[
          { form: "Form 1040", count: 24 },
          { form: "Schedule A", count: 12 },
          { form: "Schedule C", count: 8 },
        ]}
      />
    );

    expect(screen.getByText("Form 1040")).toBeInTheDocument();
    expect(screen.getByText("24 fields")).toBeInTheDocument();
    expect(screen.getByText("Schedule A")).toBeInTheDocument();
    expect(screen.getByText("12 fields")).toBeInTheDocument();
    expect(screen.getByText("Schedule C")).toBeInTheDocument();
    expect(screen.getByText("8 fields")).toBeInTheDocument();
  });

  it("displays filing status", () => {
    render(<UploadSummaryOverlay {...defaultProps} />);

    expect(screen.getByText(/Married Filing Jointly/)).toBeInTheDocument();
  });

  it("calls onContinue when Continue button is clicked", async () => {
    const user = userEvent.setup();
    const onContinue = vi.fn();

    render(<UploadSummaryOverlay {...defaultProps} onContinue={onContinue} />);
    await user.click(screen.getByRole("button", { name: "Continue" }));

    expect(onContinue).toHaveBeenCalledOnce();
  });

  it("calls onReUpload when Re-upload button is clicked", async () => {
    const user = userEvent.setup();
    const onReUpload = vi.fn();

    render(<UploadSummaryOverlay {...defaultProps} onReUpload={onReUpload} />);
    await user.click(screen.getByRole("button", { name: "Re-upload" }));

    expect(onReUpload).toHaveBeenCalledOnce();
  });

  it("calls onReUpload when clicking overlay backdrop", async () => {
    const user = userEvent.setup();
    const onReUpload = vi.fn();

    render(<UploadSummaryOverlay {...defaultProps} onReUpload={onReUpload} />);

    // Click the overlay (backdrop), not the panel
    const overlay = document.querySelector(".upload-summary-overlay");
    await user.click(overlay!);

    expect(onReUpload).toHaveBeenCalledOnce();
  });

  it("does not call onReUpload when clicking inside the panel", async () => {
    const user = userEvent.setup();
    const onReUpload = vi.fn();

    render(<UploadSummaryOverlay {...defaultProps} onReUpload={onReUpload} />);

    // Click inside the panel (on the header)
    await user.click(screen.getByText("Upload Summary"));

    expect(onReUpload).not.toHaveBeenCalled();
  });
});
