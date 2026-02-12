import { describe, it, expect } from "vitest";
import { widgetRegistry } from "../registry";

describe("widgetRegistry", () => {
  it("contains the expected widgets", () => {
    const ids = widgetRegistry.map((w) => w.id);
    expect(ids).toContain("key-numbers");
    expect(ids).toContain("year-over-year");
  });

  it("has unique widget IDs", () => {
    const ids = widgetRegistry.map((w) => w.id);
    const unique = new Set(ids);
    expect(unique.size).toBe(ids.length);
  });

  it("each widget has required properties", () => {
    for (const widget of widgetRegistry) {
      expect(widget.id).toBeTruthy();
      expect(widget.title).toBeTruthy();
      expect(typeof widget.component).toBe("function");
    }
  });

  it("key-numbers widget requires minimum 1 return", () => {
    const keyNumbers = widgetRegistry.find((w) => w.id === "key-numbers");
    expect(keyNumbers?.minReturns).toBe(1);
  });

  it("year-over-year widget requires minimum 2 returns", () => {
    const yoy = widgetRegistry.find((w) => w.id === "year-over-year");
    expect(yoy?.minReturns).toBe(2);
  });
});
