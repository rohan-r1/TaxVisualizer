import { describe, it, expect } from "vitest";
import { parseChartConfig, stripChartConfig } from "../claude";

describe("parseChartConfig", () => {
  it("parses a valid bar chart config", () => {
    const response = `Here's your chart!

\`\`\`chart-config
{"type": "bar", "title": "Total Tax Over Time", "metrics": ["total_tax"]}
\`\`\`

This shows your tax liability across years.`;

    const config = parseChartConfig(response);

    expect(config).not.toBeNull();
    expect(config?.type).toBe("bar");
    expect(config?.title).toBe("Total Tax Over Time");
    expect(config?.metrics).toEqual(["total_tax"]);
    expect(config?.id).toBeDefined();
    expect(config?.createdAt).toBeInstanceOf(Date);
  });

  it("parses a valid line chart config with multiple metrics", () => {
    const response = `\`\`\`chart-config
{"type": "line", "title": "Income vs Tax", "metrics": ["total_income", "total_tax"]}
\`\`\``;

    const config = parseChartConfig(response);

    expect(config).not.toBeNull();
    expect(config?.type).toBe("line");
    expect(config?.metrics).toEqual(["total_income", "total_tax"]);
  });

  it("parses a valid pie chart config", () => {
    const response = `\`\`\`chart-config
{"type": "pie", "title": "Tax Breakdown", "metrics": ["total_tax", "refund"]}
\`\`\``;

    const config = parseChartConfig(response);

    expect(config).not.toBeNull();
    expect(config?.type).toBe("pie");
  });

  it("parses a pie chart config with year field", () => {
    const response = `\`\`\`chart-config
{"type": "pie", "title": "Income Breakdown 2021", "metrics": ["wages", "taxable_interest", "ordinary_dividends"], "year": 2021}
\`\`\``;

    const config = parseChartConfig(response);

    expect(config).not.toBeNull();
    expect(config?.type).toBe("pie");
    expect(config?.year).toBe(2021);
  });

  it("ignores invalid year values", () => {
    const response = `\`\`\`chart-config
{"type": "bar", "title": "Test", "metrics": ["total_tax"], "year": "invalid"}
\`\`\``;

    const config = parseChartConfig(response);

    expect(config).not.toBeNull();
    expect(config?.year).toBeUndefined();
  });

  it("ignores year values outside valid range", () => {
    const response = `\`\`\`chart-config
{"type": "bar", "title": "Test", "metrics": ["total_tax"], "year": 1900}
\`\`\``;

    const config = parseChartConfig(response);

    expect(config).not.toBeNull();
    expect(config?.year).toBeUndefined();
  });

  it("parses a valid stacked_bar chart config", () => {
    const response = `\`\`\`chart-config
{"type": "stacked_bar", "title": "Components", "metrics": ["total_income", "total_tax"]}
\`\`\``;

    const config = parseChartConfig(response);

    expect(config).not.toBeNull();
    expect(config?.type).toBe("stacked_bar");
  });

  it("returns null for response without chart config", () => {
    const response = "Here's information about your taxes. Your total tax was $8,500.";

    expect(parseChartConfig(response)).toBeNull();
  });

  it("returns null for invalid chart type", () => {
    const response = `\`\`\`chart-config
{"type": "scatter", "title": "Invalid", "metrics": ["total_tax"]}
\`\`\``;

    expect(parseChartConfig(response)).toBeNull();
  });

  it("returns null for invalid metric", () => {
    const response = `\`\`\`chart-config
{"type": "bar", "title": "Invalid", "metrics": ["invalid_metric"]}
\`\`\``;

    expect(parseChartConfig(response)).toBeNull();
  });

  it("returns null for empty metrics array", () => {
    const response = `\`\`\`chart-config
{"type": "bar", "title": "Empty", "metrics": []}
\`\`\``;

    expect(parseChartConfig(response)).toBeNull();
  });

  it("returns null for missing required fields", () => {
    const response = `\`\`\`chart-config
{"type": "bar", "title": "Missing Metrics"}
\`\`\``;

    expect(parseChartConfig(response)).toBeNull();
  });

  it("returns null for malformed JSON", () => {
    const response = `\`\`\`chart-config
{type: "bar", title: "Bad JSON", metrics: ["total_tax"]}
\`\`\``;

    expect(parseChartConfig(response)).toBeNull();
  });

  it("validates all available metrics", () => {
    const validMetrics = [
      // Form 1040
      "wages",
      "total_income",
      "adjustments",
      "agi",
      "deduction",
      "taxable_income",
      "total_tax",
      "total_payments",
      "refund",
      "amount_owed",
      "effective_tax_rate",
      // Schedule A
      "sched_a_medical",
      "sched_a_salt",
      "sched_a_mortgage_interest",
      "sched_a_charity",
      "sched_a_total",
      // Schedule C
      "sched_c_gross_receipts",
      "sched_c_cogs",
      "sched_c_gross_profit",
      "sched_c_expenses",
      "sched_c_net_profit",
      // Schedule D
      "sched_d_short_term",
      "sched_d_long_term",
      "sched_d_net",
      "sched_d_carryover",
    ];

    for (const metric of validMetrics) {
      const response = `\`\`\`chart-config
{"type": "bar", "title": "Test", "metrics": ["${metric}"]}
\`\`\``;

      const config = parseChartConfig(response);
      expect(config).not.toBeNull();
      expect(config?.metrics).toEqual([metric]);
    }
  });
});

describe("stripChartConfig", () => {
  it("removes chart config block from response", () => {
    const response = `Here's your chart!

\`\`\`chart-config
{"type": "bar", "title": "Total Tax", "metrics": ["total_tax"]}
\`\`\`

This shows your tax liability.`;

    const stripped = stripChartConfig(response);

    // The stripped version should not contain the chart config
    expect(stripped).not.toContain("chart-config");
    expect(stripped).not.toContain('"total_tax"');
    expect(stripped).toContain("Here's your chart!");
    expect(stripped).toContain("This shows your tax liability.");
  });

  it("returns original text if no config block present", () => {
    const response = "Here's information about your taxes.";

    expect(stripChartConfig(response)).toBe(response);
  });

  it("handles config block at start of response", () => {
    const response = `\`\`\`chart-config
{"type": "bar", "title": "Test", "metrics": ["total_tax"]}
\`\`\`
Here's the explanation.`;

    const stripped = stripChartConfig(response);

    expect(stripped).toBe("Here's the explanation.");
  });

  it("handles config block at end of response", () => {
    const response = `Here's your visualization.
\`\`\`chart-config
{"type": "bar", "title": "Test", "metrics": ["total_tax"]}
\`\`\``;

    const stripped = stripChartConfig(response);

    expect(stripped).toBe("Here's your visualization.");
  });

  it("only removes one config block", () => {
    const response = `\`\`\`chart-config
{"type": "bar", "title": "First", "metrics": ["total_tax"]}
\`\`\`
Middle text
\`\`\`chart-config
{"type": "line", "title": "Second", "metrics": ["agi"]}
\`\`\``;

    const stripped = stripChartConfig(response);

    // Should only remove the first block
    expect(stripped).toContain("chart-config");
    expect(stripped).toContain("Middle text");
  });
});
