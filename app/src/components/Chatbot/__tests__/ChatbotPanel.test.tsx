import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ChatbotPanel } from "../ChatbotPanel";
import { ChatbotMessage } from "../ChatbotMessage";
import { ChatbotInput } from "../ChatbotInput";
import { makeReturn, makeSummary, makeFieldSet } from "../../../test/fixtures";

describe("ChatbotPanel", () => {
  const defaultProps = {
    returns: [makeReturn()],
    fields: { 1: makeFieldSet(1) },
    summaries: [makeSummary()],
    onClose: vi.fn(),
    onOpenSettings: vi.fn(),
  };

  it("renders with header and title", () => {
    render(<ChatbotPanel {...defaultProps} />);

    expect(screen.getByText("Tax Assistant")).toBeInTheDocument();
  });

  it("shows welcome message when no messages", () => {
    render(<ChatbotPanel {...defaultProps} />);

    expect(
      screen.getByText("Ask me anything about your tax returns!")
    ).toBeInTheDocument();
  });

  it("has settings and close buttons in header", () => {
    render(<ChatbotPanel {...defaultProps} />);

    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThanOrEqual(2);
  });

  it("calls onClose when close button clicked", () => {
    const onClose = vi.fn();
    render(<ChatbotPanel {...defaultProps} onClose={onClose} />);

    const closeButton = screen.getByTitle("Minimize");
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalled();
  });

  it("calls onOpenSettings when settings button clicked", () => {
    const onOpenSettings = vi.fn();
    render(<ChatbotPanel {...defaultProps} onOpenSettings={onOpenSettings} />);

    const settingsButton = screen.getByTitle("Settings");
    fireEvent.click(settingsButton);

    expect(onOpenSettings).toHaveBeenCalled();
  });

  it("has input field for messages", () => {
    render(<ChatbotPanel {...defaultProps} />);

    const input = screen.getByPlaceholderText("Ask about your tax returns...");
    expect(input).toBeInTheDocument();
  });

  it("renders with correct CSS classes", () => {
    const { container } = render(<ChatbotPanel {...defaultProps} />);

    expect(container.querySelector(".chatbot-panel")).toBeInTheDocument();
    expect(container.querySelector(".chatbot-header")).toBeInTheDocument();
    expect(container.querySelector(".chatbot-messages")).toBeInTheDocument();
    expect(container.querySelector(".chatbot-input")).toBeInTheDocument();
  });
});

describe("ChatbotMessage", () => {
  it("renders user message with user styling", () => {
    const { container } = render(
      <ChatbotMessage
        message={{
          id: "1",
          role: "user",
          content: "What was my AGI?",
          timestamp: new Date(),
        }}
      />
    );

    expect(screen.getByText("What was my AGI?")).toBeInTheDocument();
    expect(container.querySelector(".chatbot-message.user")).toBeInTheDocument();
  });

  it("renders assistant message with assistant styling", () => {
    const { container } = render(
      <ChatbotMessage
        message={{
          id: "2",
          role: "assistant",
          content: "Your AGI was $72,000",
          timestamp: new Date(),
        }}
      />
    );

    expect(screen.getByText("Your AGI was $72,000")).toBeInTheDocument();
    expect(container.querySelector(".chatbot-message.assistant")).toBeInTheDocument();
  });
});

describe("ChatbotInput", () => {
  it("renders textarea and submit button", () => {
    render(<ChatbotInput onSend={vi.fn()} />);

    expect(
      screen.getByPlaceholderText("Ask about your tax returns...")
    ).toBeInTheDocument();
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("calls onSend when form submitted with text", () => {
    const onSend = vi.fn();
    render(<ChatbotInput onSend={onSend} />);

    const input = screen.getByPlaceholderText("Ask about your tax returns...");
    fireEvent.change(input, { target: { value: "What was my tax?" } });
    fireEvent.submit(input.closest("form")!);

    expect(onSend).toHaveBeenCalledWith("What was my tax?");
  });

  it("clears input after submission", () => {
    const onSend = vi.fn();
    render(<ChatbotInput onSend={onSend} />);

    const input = screen.getByPlaceholderText("Ask about your tax returns...") as HTMLTextAreaElement;
    fireEvent.change(input, { target: { value: "Test message" } });
    fireEvent.submit(input.closest("form")!);

    expect(input.value).toBe("");
  });

  it("does not call onSend with empty text", () => {
    const onSend = vi.fn();
    render(<ChatbotInput onSend={onSend} />);

    const input = screen.getByPlaceholderText("Ask about your tax returns...");
    fireEvent.submit(input.closest("form")!);

    expect(onSend).not.toHaveBeenCalled();
  });

  it("disables input when disabled prop is true", () => {
    render(<ChatbotInput onSend={vi.fn()} disabled />);

    const input = screen.getByPlaceholderText("Ask about your tax returns...");
    expect(input).toBeDisabled();
  });

  it("submit button is disabled when input is empty", () => {
    render(<ChatbotInput onSend={vi.fn()} />);

    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
  });
});
