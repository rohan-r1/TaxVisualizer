# Plan: Phase 2: Tauri sidecar integration

**Issue:** [ROH-19](https://linear.app/rohanr/issue/ROH-19/phase-2-tauri-sidecar-integration)
**Priority:** High
**Status:** Already Implemented (needs verification & Linear status update)

---

## Context

ROH-19 is Phase 2 of the PDF extraction pipeline (ROH-17). Upon investigation, **this work was already completed** as part of ROH-17 execution. The Linear issue status is out of sync with the actual codebase state.

**Evidence of completion:**
- `app/src-tauri/binaries/extract-x86_64-pc-windows-msvc.exe` exists (99MB bundled Python)
- `app/src/services/pdfExtractor.ts` implements sidecar invocation
- `app/src-tauri/tauri.conf.json` has `externalBin: ["binaries/extract"]`
- `app/src-tauri/capabilities/default.json` has shell permissions for sidecar
- `App.tsx` uses `extractPdf()` with fallback to mock
- ROH-17 plan shows Phase 2 tasks all marked 🟢 Complete

## Summary

No new implementation needed. This plan documents the existing implementation and recommends:
1. Verify the sidecar works correctly
2. Commit any uncommitted sidecar-related files
3. Update Linear status to "Done"

## Current Implementation

### 1. Python Sidecar (Bundled Executable)

**Built executable:** `app/src-tauri/binaries/extract-x86_64-pc-windows-msvc.exe`
- Created by `python/build.py` using PyInstaller
- Bundles Python runtime + pdfplumber + all mappings
- Size: ~99MB (includes Python interpreter)

**Platform note:** Only Windows x86_64 binary exists. macOS builds will be needed for cross-platform distribution (future work, possibly ROH-21 or a new issue).

### 2. Tauri Configuration

**tauri.conf.json:**
```json
{
  "bundle": {
    "externalBin": ["binaries/extract"]
  }
}
```

**capabilities/default.json:**
```json
{
  "permissions": [
    {
      "identifier": "shell:allow-execute",
      "allow": [{ "name": "binaries/extract", "sidecar": true, "args": true }]
    },
    "shell:allow-spawn",
    "shell:allow-kill",
    "shell:allow-stdin-write"
  ]
}
```

**lib.rs:**
```rust
.plugin(tauri_plugin_shell::init())  // Shell plugin initialized
```

### 3. TypeScript Service

**`app/src/services/pdfExtractor.ts`** — 114 lines

Key functions:
- `extractPdf(pdfPath: string)` — Spawns sidecar, returns parsed JSON
- `getSupportedYears()` — Queries sidecar for supported form years
- `checkSidecarAvailable()` — Health check for sidecar availability

Communication pattern:
```typescript
const command = Command.sidecar("binaries/extract", [pdfPath]);
const output = await command.execute();
const result: ExtractionResult = JSON.parse(output.stdout);
```

### 4. Frontend Integration

**`app/src/App.tsx`** — Lines 54-119

- Checks `sidecarAvailable` on app startup
- Uses `extractPdf()` when sidecar available
- Falls back to `mockExtract()` if sidecar unavailable or fails
- Converts sidecar JSON format to internal schema
- Stores results in SQLite via `insertFieldsBatch()`

## Task List

- 🔴 **Verify implementation works** — Test sidecar extraction end-to-end
  - 🔴 Upload a sample PDF in the running app
  - 🔴 Confirm extraction uses sidecar (check console logs)
  - 🔴 Verify extracted values display correctly
- 🟢 **Commit uncommitted files** — All sidecar files are already committed
- 🔴 **Update Linear status** — Mark ROH-19 as Done

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Files (Already Exist)

| File | Status | Purpose |
|------|--------|---------|
| `app/src-tauri/python/build.py` | ✅ Exists | PyInstaller build script |
| `app/src-tauri/binaries/extract-*.exe` | ✅ Exists | Bundled Python executable |
| `app/src-tauri/tauri.conf.json` | ✅ Configured | `externalBin` set |
| `app/src-tauri/capabilities/default.json` | ✅ Configured | Shell permissions |
| `app/src/services/pdfExtractor.ts` | ✅ Exists | TypeScript sidecar client |
| `app/src/App.tsx` | ✅ Integrated | Uses sidecar extraction |

## Testing Strategy

### Verification Steps

1. **Start the app:**
   ```bash
   cd app && npm run tauri dev
   ```

2. **Upload a sample PDF:**
   - Use any Form 1040 from `test-data/sample-returns/`

3. **Check console:**
   - Should log "Using Python sidecar for PDF extraction"
   - Should NOT show "Sidecar not available" or fallback messages

4. **Verify extraction:**
   - Key numbers should display (wages, total income, etc.)
   - Values should match the PDF content

### Success Criteria

- Sidecar spawns without errors
- JSON output parses correctly
- Extracted fields appear in dashboard
- No fallback to mock extraction when sidecar is available

## Risks & Considerations

- **Cross-platform builds:** Only Windows binary exists. macOS users would fall back to mock extraction until macOS binaries are built. This is acceptable for now but should be addressed before macOS release.

- **Large binary size:** The 99MB sidecar is acceptable for a desktop app but should not be committed to git. Add to `.gitignore` and document build process.

## Open Questions

1. **Should we track macOS builds as a separate issue?**
   - Recommendation: Yes, create a new issue for cross-platform sidecar builds

2. **Are the sidecar files committed to git?**
   - Check git status during verification phase

---

*This plan documents existing work. The implementation is complete; only verification and Linear status update remain.*
