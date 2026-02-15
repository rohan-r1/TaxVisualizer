# Plan: [Phase 1] Schedule extraction — Upload summary overlay + detection infrastructure

**Issue:** [ROH-33](https://linear.app/rohanr/issue/ROH-33/phase-1-schedule-extraction-upload-summary-overlay-detection)
**Parent:** [ROH-32](https://linear.app/rohanr/issue/ROH-32/add-schedule-1-a-and-c-extraction-with-upload-summary-overlay)
**Priority:** High
**Status:** Complete

---

## Context

Currently, when users upload a PDF, it's processed immediately and saved to the database with no confirmation step. Users can't see what was detected before committing. Additionally, the extraction pipeline only handles Form 1040 — it can't detect or process additional schedules like Schedule 1, A, or C that may be included in a multi-page PDF.

This phase establishes the infrastructure needed to:
1. Give users visibility into what's being uploaded (detected forms, field counts)
2. Enable detection of schedule pages in multi-page PDFs
3. Prepare the codebase for Phase 2's full schedule extraction

## Summary

Phase 1 adds an **upload summary overlay** that appears after PDF extraction, showing the user which forms were detected and giving them options to Continue or Re-upload. The backend is extended to detect schedule pages in multi-page PDFs and report them in the extraction result. This sets up the infrastructure that Phase 2 will build upon for actual schedule field extraction.

## Phased Approach

This is a master issue broken into phases. Each phase has its own sub-issue for tracking.

| Phase | Scope | Issue |
|-------|-------|-------|
| 1 | Upload summary overlay + schedule detection infrastructure | [ROH-33](https://linear.app/rohanr/issue/ROH-33) (this plan) |
| 2 | Schedule 1, A, C mappings and field extraction (21 mapping files) | [ROH-34](https://linear.app/rohanr/issue/ROH-34) |

**Master issue:** [ROH-32](https://linear.app/rohanr/issue/ROH-32) — tracks overall progress

---

## Technical Approach

### Why This Approach

We're splitting the feature into two phases because:
1. **Immediate user value**: The overlay provides useful feedback even with just Form 1040
2. **Testable checkpoints**: Phase 1 can be verified independently before tackling 21 mapping files
3. **Risk reduction**: Infrastructure changes are isolated from coordinate calibration work

The upload summary overlay follows the existing `SettingsPanel` pattern — a proven, styled modal component that's consistent with the app's design.

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| Inline status banner (no overlay) | Simpler, less intrusive | No re-upload option, less visible | Users might miss it; can't easily cancel |
| Combine all phases | Faster if everything works | Very long PR, harder to test, higher risk | 21 mapping files + UI + tests is too large |
| Skip detection, assume page order | Less code | Unreliable — schedules can appear in any order | Would break with real-world PDFs |

---

## Task List

- 🟢 **Backend: Schedule detection** — Add page detection for Schedule 1, A, C
  - 🟢 Add `detect_schedules()` function in `mappings/__init__.py`
  - 🟢 Update `extract.py` to call detection and include `detected_forms` in result
  - 🟢 Add unit tests for schedule detection

- 🟢 **Types: Update interfaces** — Extend TypeScript types for new data
  - 🟢 Add `schedule_1` to `FieldCategory` in `types/tax.ts`
  - 🟢 Add `detected_forms` to `ExtractionResult` in `pdfExtractor.ts`
  - 🟢 Add `schedule_1` label to `taxContext.ts`

- 🟢 **UI: Upload summary overlay** — Create confirmation modal
  - 🟢 Create `UploadSummaryOverlay.tsx` component
  - 🟢 Add CSS styles following SettingsPanel pattern
  - 🟢 Add component tests

- 🟢 **Integration: Connect overlay to upload flow** — Wire everything together
  - 🟢 Add pending upload state to `App.tsx`
  - 🟢 Show overlay after extraction, before database commit
  - 🟢 Handle Continue (save) and Re-upload (cancel) actions

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

---

## Major Changes

### 1. Schedule Detection (Python Backend)

**Current state:** The extractor only looks for Form 1040 metadata. It doesn't know about schedules.

**After this change:** A new `detect_schedules()` function scans each page for schedule identifiers (e.g., "Schedule 1", "Schedule A") and returns which schedules are present and on which pages.

```python
# In mappings/__init__.py
def detect_schedules(pdf) -> Dict[str, Optional[int]]:
    """
    Detect which schedules are present in a multi-page PDF.
    Returns: {'schedule_1': page_idx, 'schedule_a': page_idx, 'schedule_c': page_idx}
    Values are None if schedule not found.
    """
```

**Why:** Multi-page PDFs may have schedules in any order, or not at all. Text-based detection is more reliable than assuming fixed positions.

### 2. Extraction Result Enhancement

**Current state:**
```typescript
interface ExtractionResult {
  year: number;
  filing_status: string;
  extraction_method: string;
  fields: ExtractedField[];
  // ...
}
```

**After this change:**
```typescript
interface ExtractionResult {
  year: number;
  filing_status: string;
  extraction_method: string;
  fields: ExtractedField[];
  detected_forms?: string[];  // NEW: ["Form 1040", "Schedule A", "Schedule C"]
  // ...
}
```

**Why:** The frontend needs to know which forms were detected to display them in the overlay.

### 3. Upload Summary Overlay Component

**Current state:** No confirmation step — files go straight to database.

**After this change:** A modal appears showing:
- Tax year (e.g., "2023")
- Filing status (e.g., "Married Filing Jointly")
- Detected forms with checkmarks (e.g., "Form 1040", "Schedule A")
- Field count (e.g., "35 fields extracted")
- Low-confidence warning if applicable
- Two buttons: "Re-upload" and "Continue"

```
┌─────────────────────────────────────┐
│ Upload Summary              [2023]  │
├─────────────────────────────────────┤
│                                     │
│ Detected Forms                      │
│ ✓ Form 1040                         │
│ ✓ Schedule A                        │
│ ✓ Schedule C                        │
│                                     │
│ ┌─────────┐  ┌─────────┐            │
│ │   35    │  │    2    │            │
│ │ Fields  │  │ Review  │            │
│ └─────────┘  └─────────┘            │
│                                     │
│ Filing Status: Married Filing...    │
│                                     │
│ [Re-upload]           [Continue]    │
└─────────────────────────────────────┘
```

**Why:** Users should see what they're about to import and have a chance to re-upload if they selected the wrong file.

### 4. Upload Flow State Change

**Current state:**
```
User selects file → extractPdf() → insertReturn() → done
```

**After this change:**
```
User selects file → extractPdf() → show overlay → user clicks Continue → insertReturn() → done
                                               └→ user clicks Re-upload → reset state
```

**Why:** The overlay sits between extraction and database commit, giving users a checkpoint.

---

## Implementation Details

### Schedule Detection Logic

The detection function searches for identifying text on each page:

```python
# In mappings/__init__.py

SCHEDULE_PATTERNS = {
    'schedule_1': [r'Schedule\s*1', r'Additional\s+Income\s+and\s+Adjustments'],
    'schedule_a': [r'Schedule\s*A', r'Itemized\s+Deductions'],
    'schedule_c': [r'Schedule\s*C', r'Profit\s+or\s+Loss\s+From\s+Business'],
}

def detect_schedules(pdf) -> Dict[str, Optional[int]]:
    """Detect schedule pages by searching for identifying text."""
    result = {key: None for key in SCHEDULE_PATTERNS}

    for page_idx, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        for schedule_type, patterns in SCHEDULE_PATTERNS.items():
            if result[schedule_type] is None:  # Not yet found
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        result[schedule_type] = page_idx
                        break
    return result
```

### Extract.py Updates

```python
# In extract.py

def extract_form_1040(pdf_path: str) -> Dict[str, Any]:
    with pdfplumber.open(pdf_path) as pdf:
        year = detect_form_year(pdf.pages[0])
        schedules = detect_schedules(pdf)  # NEW

        # ... existing field extraction ...

        # Build detected_forms list
        detected_forms = ['Form 1040']
        for schedule_type, page_idx in schedules.items():
            if page_idx is not None:
                name = schedule_type.replace('_', ' ').title()
                detected_forms.append(name)

        return {
            "year": year,
            "filing_status": filing_status,
            "extraction_method": "pdfplumber",
            "fields": fields,
            "page_count": len(pdf.pages),
            "detected_forms": detected_forms,  # NEW
        }
```

### UploadSummaryOverlay Component

```typescript
// components/UploadSummary/UploadSummaryOverlay.tsx

export interface UploadSummaryProps {
  year: number;
  filingStatus: string;
  detectedForms: string[];
  fieldCount: number;
  lowConfidenceCount: number;
  onContinue: () => void;
  onReUpload: () => void;
}

export function UploadSummaryOverlay({ ... }: UploadSummaryProps) {
  return (
    <div className="upload-summary-overlay" onClick={onReUpload}>
      <div className="upload-summary-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header with year badge */}
        {/* Detected forms list with checkmarks */}
        {/* Stats: field count, review count */}
        {/* Filing status */}
        {/* Action buttons */}
      </div>
    </div>
  );
}
```

### App.tsx Integration

```typescript
// In App.tsx

// New state for pending upload
const [pendingUpload, setPendingUpload] = useState<{
  path: string;
  filename: string;
  result: ExtractionResult;
} | null>(null);

const handleFileSelected = async (path: string, filename: string) => {
  setExtracting(true);
  const result = await extractPdf(path);
  setExtracting(false);

  if (result.error) {
    setError(result.error);
    return;
  }

  // Show overlay instead of immediately saving
  setPendingUpload({ path, filename, result });
};

const handleConfirmUpload = async () => {
  if (!pendingUpload) return;
  // ... existing save logic moved here ...
  setPendingUpload(null);
};

const handleCancelUpload = () => {
  setPendingUpload(null);
};
```

---

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src-tauri/python/mappings/__init__.py` | Add `detect_schedules()` function |
| Modify | `app/src-tauri/python/extract.py` | Call detection, add `detected_forms` to result |
| Modify | `app/src/types/tax.ts` | Add `schedule_1` to FieldCategory |
| Modify | `app/src/services/pdfExtractor.ts` | Add `detected_forms` to ExtractionResult interface |
| Modify | `app/src/services/taxContext.ts` | Add `schedule_1` category label |
| Create | `app/src/components/UploadSummary/UploadSummaryOverlay.tsx` | New overlay component |
| Create | `app/src/components/UploadSummary/index.ts` | Export barrel file |
| Modify | `app/src/App.css` | Add `.upload-summary-*` styles |
| Modify | `app/src/App.tsx` | Add pending state, show overlay, handle actions |
| Create | `app/src/components/__tests__/UploadSummaryOverlay.test.tsx` | Component tests |
| Create | `app/src-tauri/python/tests/test_schedule_detection.py` | Python unit tests |

---

## Testing Strategy

### What to Test

**Python (unit tests):**
- `test_detect_schedules_form_1040_only()` — Returns no schedules for single-form PDF
- `test_detect_schedules_with_schedule_a()` — Correctly identifies Schedule A page
- `test_detect_schedules_multiple()` — Handles PDF with all three schedules
- `test_detect_schedules_order_independent()` — Works regardless of page order

**React (Vitest + RTL):**
- `UploadSummaryOverlay` renders all detected forms
- "Continue" button calls `onContinue` handler
- "Re-upload" button calls `onReUpload` handler
- Clicking overlay backdrop calls `onReUpload`
- Low-confidence count shows warning badge when > 0

**Integration (manual):**
- Upload Form 1040-only PDF → overlay shows only "Form 1040"
- Upload multi-page PDF with Schedule A → overlay shows both forms
- Click Re-upload → overlay closes, can select new file
- Click Continue → data saved, appears in dashboard

### How to Verify

```bash
# Run Python tests
cd app/src-tauri/python
python -m pytest tests/test_schedule_detection.py -v

# Run React tests
cd app
npm test

# Manual E2E
npm run tauri dev
# Upload a multi-page PDF and verify overlay shows correct forms
```

---

## Risks & Considerations

- **Risk: Schedule detection accuracy**
  - *Impact:* False positives/negatives in schedule detection
  - *Mitigation:* Use multiple regex patterns per schedule; test with real IRS PDFs

- **Risk: Page order assumptions**
  - *Impact:* Detection could fail if schedules appear before Form 1040
  - *Mitigation:* Scan all pages, don't assume order; Form 1040 detection already handles this

- **Risk: Overlay doesn't block interaction**
  - *Impact:* User could interact with background while overlay is open
  - *Mitigation:* Overlay uses fixed positioning with z-index, same pattern as SettingsPanel

---

## Dependencies

- No external dependencies
- Builds on existing SettingsPanel CSS patterns
- Phase 2 depends on this phase completing first

---

## Open Questions

None — all design decisions resolved. Ready for implementation.

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
