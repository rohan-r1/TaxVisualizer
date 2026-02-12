import type { Message } from "../components/Chatbot/ChatbotPanel";

const API_KEY_STORAGE_KEY = "claude_api_key";
const ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages";

interface ClaudeMessage {
  role: "user" | "assistant";
  content: string;
}

/**
 * Send a message to Claude API with streaming response.
 * Tax context is injected as a system prompt.
 */
export async function sendChatMessage(
  userMessage: string,
  taxContext: string,
  previousMessages: Message[],
  onChunk: (chunk: string) => void
): Promise<void> {
  const apiKey = localStorage.getItem(API_KEY_STORAGE_KEY);

  if (!apiKey) {
    throw new Error("API key not configured. Please add your Claude API key in Settings.");
  }

  // Build conversation history
  const messages: ClaudeMessage[] = previousMessages.map((msg) => ({
    role: msg.role,
    content: msg.content,
  }));

  // Add the new user message
  messages.push({
    role: "user",
    content: userMessage,
  });

  const systemPrompt = `You are a helpful tax assistant for the TaxVisualizer application. You help users understand their tax returns and answer questions about their tax data.

Here is the user's tax data:

${taxContext}

Guidelines:
- Be concise but thorough in your answers
- When referencing specific numbers, cite the tax year
- If the user asks about something not in their data, let them know
- Use plain language to explain tax concepts
- Format currency values clearly
- If comparing years, show the actual values and changes
- Never make up data - only use what's provided above`;

  const response = await fetch(ANTHROPIC_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "anthropic-dangerous-direct-browser-access": "true",
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      system: systemPrompt,
      messages,
      stream: true,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    if (response.status === 401) {
      throw new Error("Invalid API key. Please check your API key in Settings.");
    }
    throw new Error(error.error?.message || `API error: ${response.status}`);
  }

  // Handle streaming response
  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Process complete events in the buffer
    const lines = buffer.split("\n");
    buffer = lines.pop() || ""; // Keep incomplete line in buffer

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") continue;

        try {
          const event = JSON.parse(data);
          if (event.type === "content_block_delta" && event.delta?.text) {
            onChunk(event.delta.text);
          }
        } catch {
          // Ignore parse errors for incomplete JSON
        }
      }
    }
  }
}
