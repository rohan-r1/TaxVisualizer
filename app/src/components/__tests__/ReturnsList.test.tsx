import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReturnsList } from "../ReturnsList";
import { makeReturn } from "../../test/fixtures";

describe("ReturnsList", () => {
  it("renders nothing when returns list is empty", () => {
    const { container } = render(
      <ReturnsList returns={[]} onDelete={vi.fn()} />
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders the header", () => {
    const returns = [makeReturn()];
    render(<ReturnsList returns={returns} onDelete={vi.fn()} />);

    expect(screen.getByText("Uploaded Returns")).toBeInTheDocument();
  });

  it("renders each return's tax year", () => {
    const returns = [
      makeReturn({ id: 1, tax_year: 2021 }),
      makeReturn({ id: 2, tax_year: 2022 }),
      makeReturn({ id: 3, tax_year: 2023 }),
    ];
    render(<ReturnsList returns={returns} onDelete={vi.fn()} />);

    expect(screen.getByText("2021")).toBeInTheDocument();
    expect(screen.getByText("2022")).toBeInTheDocument();
    expect(screen.getByText("2023")).toBeInTheDocument();
  });

  it("renders each return's filename", () => {
    const returns = [
      makeReturn({ id: 1, pdf_filename: "my_2023_return.pdf" }),
    ];
    render(<ReturnsList returns={returns} onDelete={vi.fn()} />);

    expect(screen.getByText("my_2023_return.pdf")).toBeInTheDocument();
  });

  it("renders filing status", () => {
    const returns = [makeReturn({ filing_status: "Married Filing Jointly" })];
    render(<ReturnsList returns={returns} onDelete={vi.fn()} />);

    expect(screen.getByText("Married Filing Jointly")).toBeInTheDocument();
  });

  it("shows 'Processing...' when filing_status is null", () => {
    const returns = [makeReturn({ filing_status: null })];
    render(<ReturnsList returns={returns} onDelete={vi.fn()} />);

    expect(screen.getByText("Processing...")).toBeInTheDocument();
  });

  it("calls onDelete with the correct id when delete button is clicked", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    const returns = [
      makeReturn({ id: 42, tax_year: 2023 }),
    ];
    render(<ReturnsList returns={returns} onDelete={onDelete} />);

    const deleteBtn = screen.getByTitle("Delete this return");
    await user.click(deleteBtn);

    expect(onDelete).toHaveBeenCalledOnce();
    expect(onDelete).toHaveBeenCalledWith(42);
  });

  it("renders a delete button for each return", () => {
    const returns = [
      makeReturn({ id: 1, tax_year: 2021 }),
      makeReturn({ id: 2, tax_year: 2022 }),
    ];
    render(<ReturnsList returns={returns} onDelete={vi.fn()} />);

    const deleteButtons = screen.getAllByTitle("Delete this return");
    expect(deleteButtons).toHaveLength(2);
  });
});
