import { useState, useRef, useEffect } from "react";
import { ChatbotMessage } from "./ChatbotMessage";
import { ChatbotInput } from "./ChatbotInput";
import type { TaxReturn, ExtractedField, ReturnSummary } from "../../types/tax";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export interface ChatbotPanelProps {
  returns: TaxReturn[];
  fields: Record<number, ExtractedField[]>;
  summaries: ReturnSummary[];
  onOpenSettings: () => void;
}

export function ChatbotPanel({
  returns,
  fields,
  summaries,
  onOpenSettings,
}: ChatbotPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const streamingContentRef = useRef("");  // Tracks current value for use in closures
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const collapsedInputRef = useRef<HTMLInputElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === "function") {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  // Click outside to collapse
  useEffect(() => {
    if (!isExpanded) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setIsExpanded(false);
      }
    };

    // Use setTimeout to avoid immediately triggering on the click that expanded
    const timeoutId = setTimeout(() => {
      document.addEventListener("mousedown", handleClickOutside);
    }, 0);

    return () => {
      clearTimeout(timeoutId);
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isExpanded]);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    streamingContentRef.current = "";  // Reset ref
    setStreamingContent("");

    try {
      // Import dynamically to avoid issues if API key not set
      const { sendChatMessage } = await import("../../services/claude");
      const { buildTaxContext } = await import("../../services/taxContext");

      const taxContext = buildTaxContext(returns, fields, summaries);

      await sendChatMessage(
        content,
        taxContext,
        messages,
        (chunk) => {
          streamingContentRef.current += chunk;  // Update ref (always current)
          setStreamingContent(streamingContentRef.current);  // Update state (for rendering)
        }
      );

      // Capture the final content BEFORE any cleanup
      // (React's functional update reads the ref when it processes, not when called)
      const finalContent = streamingContentRef.current;

      // After streaming completes, add the full message
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: finalContent,  // Use captured value, not ref
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "An error occurred";
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `Error: ${errorMessage}. Please check your API key in settings.`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
      streamingContentRef.current = "";  // Reset ref
      setStreamingContent("");           // Reset state
    }
  };

  const handleCollapsedSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const input = collapsedInputRef.current;
    if (input && input.value.trim()) {
      handleSendMessage(input.value.trim());
      input.value = "";
      setIsExpanded(true);
    }
  };

  // Collapsed view: just the input bar
  if (!isExpanded) {
    return (
      <div className="chatbot-panel chatbot-collapsed">
        <form className="chatbot-input-bar" onSubmit={handleCollapsedSubmit}>
          <input
            ref={collapsedInputRef}
            type="text"
            placeholder="Ask me anything about your tax returns!"
            onFocus={() => setIsExpanded(true)}
          />
          <button
            type="button"
            className="chatbot-bar-btn"
            onClick={onOpenSettings}
            title="Settings"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3" />
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
            </svg>
          </button>
        </form>
      </div>
    );
  }

  // Expanded view: full panel with header, messages, and input
  return (
    <div ref={panelRef} className="chatbot-panel chatbot-expanded">
      <div className="chatbot-header">
        <h3>Tax Assistant</h3>
        <div className="chatbot-header-actions">
          <button
            className="chatbot-header-btn"
            onClick={onOpenSettings}
            title="Settings"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3" />
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
            </svg>
          </button>
          <button
            className="chatbot-header-btn"
            onClick={() => setIsExpanded(false)}
            title="Minimize"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 9l6 6 6-6" />
            </svg>
          </button>
        </div>
      </div>

      <div className="chatbot-messages">
        {messages.length === 0 && !isLoading && (
          <div className="chatbot-welcome">
            <p>Ask me anything about your tax returns!</p>
            <p className="chatbot-welcome-hint">
              Try: "What was my effective tax rate in 2023?" or "Compare my income across years"
            </p>
          </div>
        )}
        {messages.map((message) => (
          <ChatbotMessage key={message.id} message={message} />
        ))}
        {isLoading && streamingContent && (
          <ChatbotMessage
            message={{
              id: "streaming",
              role: "assistant",
              content: streamingContent,
              timestamp: new Date(),
            }}
          />
        )}
        {isLoading && !streamingContent && (
          <div className="chatbot-typing">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <ChatbotInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
