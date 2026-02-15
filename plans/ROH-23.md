# Plan: Add integration tests for sidecar communication

**Issue:** [ROH-23](https://linear.app/rohanr/issue/ROH-23/add-integration-tests-for-sidecar-communication)
**Priority:** Low
**Status:** Already Implemented

---

## Context

ROH-23 requested TypeScript integration tests for the PDF extraction sidecar. Upon investigation, **these tests already exist and are passing**.

## Existing Tests

**File:** `app/src/services/__tests__/pdfExtractor.test.ts` (183 lines)

### Test Coverage

| Function | Test Cases | Status |
|----------|-----------|--------|
| `extractPdf()` | Success, error handling, JSON parse errors | ✅ 3 tests |
| `getSupportedYears()` | Success, error handling | ✅ 2 tests |
| `checkSidecarAvailable()` | Available, not available | ✅ 2 tests |

**Total: 7 integration tests**

### Mock Pattern Used

```typescript
vi.mock("@tauri-apps/plugin-shell", () => ({
  Command: {
    sidecar: vi.fn(),
  },
}));

// In tests:
const mockExecute = vi.fn().mockResolvedValue({
  code: 0,
  stdout: JSON.stringify(mockResult),
  stderr: "",
});

(Command.sidecar as ReturnType<typeof vi.fn>).mockReturnValue({
  execute: mockExecute,
});
```

## Verification

```bash
cd app && npm test
# Result: 151 tests passing across 13 files
```

All acceptance criteria from the issue are met:
- ✅ Test `extractPdf()` function
- ✅ Test `checkSidecarAvailable()` function
- ✅ Mock `Command.sidecar()` from `@tauri-apps/plugin-shell`
- ✅ Test error handling when sidecar fails
- ✅ Test JSON parsing of sidecar output

## Action Required

Update Linear status to Done.

---

*This plan documents existing work. No implementation needed.*
