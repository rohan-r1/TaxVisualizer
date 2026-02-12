import type { Message } from "./ChatbotPanel";

export interface ChatbotMessageProps {
  message: Message;
}

export function ChatbotMessage({ message }: ChatbotMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`chatbot-message ${isUser ? "user" : "assistant"}`}>
      <div className="chatbot-message-content">{message.content}</div>
    </div>
  );
}
