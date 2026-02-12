import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { UploadButton } from "../UploadButton";
import { open } from "@tauri-apps/plugin-dialog";

vi.mock("@tauri-apps/plugin-dialog", () => ({
  open: vi.fn(),
}));

const mockedOpen = vi.mocked(open);

describe("UploadButton", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the upload button", () => {
    render(<UploadButton onFileSelected={vi.fn()} />);

    expect(
      screen.getByRole("button", { name: /upload tax return/i })
    ).toBeInTheDocument();
  });

  it("opens file dialog on click", async () => {
    const user = userEvent.setup();
    mockedOpen.mockResolvedValue(null);
    render(<UploadButton onFileSelected={vi.fn()} />);

    await user.click(screen.getByRole("button"));

    expect(mockedOpen).toHaveBeenCalledOnce();
    expect(mockedOpen).toHaveBeenCalledWith({
      multiple: false,
      filters: [{ name: "PDF", extensions: ["pdf"] }],
    });
  });

  it("calls onFileSelected with path and filename when file is selected", async () => {
    const user = userEvent.setup();
    const onFileSelected = vi.fn();
    mockedOpen.mockResolvedValue("/Users/test/Documents/1040_2023.pdf" as any);

    render(<UploadButton onFileSelected={onFileSelected} />);
    await user.click(screen.getByRole("button"));

    expect(onFileSelected).toHaveBeenCalledWith(
      "/Users/test/Documents/1040_2023.pdf",
      "1040_2023.pdf"
    );
  });

  it("handles Windows-style backslash paths", async () => {
    const user = userEvent.setup();
    const onFileSelected = vi.fn();
    mockedOpen.mockResolvedValue("C:\\Users\\test\\Documents\\1040_2023.pdf" as any);

    render(<UploadButton onFileSelected={onFileSelected} />);
    await user.click(screen.getByRole("button"));

    expect(onFileSelected).toHaveBeenCalledWith(
      "C:\\Users\\test\\Documents\\1040_2023.pdf",
      "1040_2023.pdf"
    );
  });

  it("does not call onFileSelected when dialog is cancelled", async () => {
    const user = userEvent.setup();
    const onFileSelected = vi.fn();
    mockedOpen.mockResolvedValue(null);

    render(<UploadButton onFileSelected={onFileSelected} />);
    await user.click(screen.getByRole("button"));

    expect(onFileSelected).not.toHaveBeenCalled();
  });
});
