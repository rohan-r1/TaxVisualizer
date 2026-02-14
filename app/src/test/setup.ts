import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

// Mock Tauri plugin-sql
vi.mock("@tauri-apps/plugin-sql", () => {
  const mockDb = {
    select: vi.fn().mockResolvedValue([]),
    execute: vi.fn().mockResolvedValue({ lastInsertId: 1, rowsAffected: 1 }),
  };
  return {
    default: {
      load: vi.fn().mockResolvedValue(mockDb),
    },
  };
});

// Mock Tauri plugin-dialog
vi.mock("@tauri-apps/plugin-dialog", () => ({
  open: vi.fn().mockResolvedValue(null),
}));

// Mock Tauri plugin-fs
vi.mock("@tauri-apps/plugin-fs", () => ({}));

// Mock Tauri plugin-opener
vi.mock("@tauri-apps/plugin-opener", () => ({}));

// Mock ResizeObserver (needed for Recharts)
class MockResizeObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
globalThis.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
