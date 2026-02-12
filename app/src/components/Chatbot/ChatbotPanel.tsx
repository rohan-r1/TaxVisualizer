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
  onClose: () => void;
  onOpenSettings: () => void;
}

export function ChatbotPanel({
  returns,
  fields,
  summaries,
  onClose,
  onOpenSettings,
}: ChatbotPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === "function") {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
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
          setStreamingContent((prev) => prev + chunk);
        }
      );

      // After streaming completes, add the full message
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: streamingContent,
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
      setStreamingContent("");
    }
  };

  // Fix: capture streaming content before clearing
  useEffect(() => {
    if (!isLoading && streamingContent) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: streamingContent,
          timestamp: new Date(),
        },
      ]);
      setStreamingContent("");
    }
  }, [isLoading, streamingContent]);

  return (
    <div className="chatbot-panel">
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
            onClick={onClose}
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
