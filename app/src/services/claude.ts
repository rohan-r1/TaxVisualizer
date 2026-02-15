import type { Message } from "../components/Chatbot/ChatbotPanel";
import type { ChartConfig } from "../types/chart";
import { isValidMetric, isValidChartType } from "../types/chart";

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
- Never make up data - only use what's provided above

## Chart Creation

When the user asks to create, show, visualize, or chart something:

1. Choose the appropriate chart type:
   - Single metric over multiple years → "bar"
   - Composition/share of a single value → "pie" (NEVER for time comparisons)
   - Multiple metrics over time → "line"
   - Stackable components over time → "stacked_bar"

2. Available metrics (use exact keys):
   - Income: wages, taxable_interest, ordinary_dividends, qualified_dividends, ira_distributions, pensions, social_security, capital_gains, other_income, total_income, adjustments, agi, taxable_income
   - Deductions: deduction, deductions, standard_deduction, qbi_deduction, total_deductions
   - Tax: tax_amount, schedule_2_tax, tax_before_credits, tax_after_credits, other_taxes, total_tax
   - Credits: child_tax_credit, schedule_3_credits, total_credits
   - Payments: federal_withholding, estimated_payments, other_payments, total_payments
   - Refund/Owed: overpaid, refund, amount_owed
   - Computed: effective_tax_rate
   - Schedule A: sched_a_medical, sched_a_salt, sched_a_mortgage_interest, sched_a_charity, sched_a_total
   - Schedule C: sched_c_gross_receipts, sched_c_cogs, sched_c_gross_profit, sched_c_expenses, sched_c_net_profit
   - Schedule D: sched_d_short_term, sched_d_long_term, sched_d_net, sched_d_carryover

3. If the metric IS in the list above, create the chart. Include this JSON block:

\`\`\`chart-config
{"type": "bar", "title": "Total Tax Over Time", "metrics": ["total_tax"]}
\`\`\`

4. For pie charts showing a specific year's breakdown, include the "year" field:

\`\`\`chart-config
{"type": "pie", "title": "Income Breakdown 2021", "metrics": ["wages", "taxable_interest", "ordinary_dividends", "capital_gains"], "year": 2021}
\`\`\`

5. If the metric is NOT in the list above, say so directly: "I can't chart [X] because we don't extract that field." Do NOT include a chart-config block.

6. Never hedge or add disclaimers when creating a chart. Either create it confidently or decline clearly.

7. For pie charts, only use for composition comparisons (e.g., income breakdown), not time series. Always include the year field when discussing a specific year.`;

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

/**
 * Parse a chart configuration from Claude's response.
 * Returns null if no valid chart config is found.
 */
export function parseChartConfig(response: string): ChartConfig | null {
  const match = response.match(/```chart-config\n([\s\S]*?)\n```/);
  if (!match) return null;

  try {
    const parsed = JSON.parse(match[1]);

    // Validate required fields
    if (!parsed.type || !parsed.title || !Array.isArray(parsed.metrics)) {
      return null;
    }

    // Validate chart type
    if (!isValidChartType(parsed.type)) {
      return null;
    }

    // Validate all metrics
    if (!parsed.metrics.every(isValidMetric)) {
      return null;
    }

    // Ensure at least one metric
    if (parsed.metrics.length === 0) {
      return null;
    }

    // Build config with optional year field
    const config: ChartConfig = {
      id: crypto.randomUUID(),
      type: parsed.type,
      title: parsed.title,
      metrics: parsed.metrics,
      createdAt: new Date(),
    };

    // Add year if specified and valid
    if (typeof parsed.year === "number" && parsed.year >= 2000 && parsed.year <= 2100) {
      config.year = parsed.year;
    }

    return config;
  } catch {
    return null;
  }
}

/**
 * Remove the chart config block from response text for display.
 */
export function stripChartConfig(response: string): string {
  return response.replace(/```chart-config\n[\s\S]*?\n```\n?/, "").trim();
}
