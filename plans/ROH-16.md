# Plan: Real PDF extraction pipeline (replace mock extraction)

**Issue:** [ROH-16](https://linear.app/rohanr/issue/ROH-16/real-pdf-extraction-pipeline-replace-mock-extraction)
**Priority:** Low
**Status:** In Progress (Tier 2 working for 2018-2019)

> **Update (2026-02-14):** Python sidecar with pdfplumber is now working. Tier 2 extraction functional for 2018-2019 Form 1040s. Tauri shell permissions configured correctly. Mappings calibrated against sample PDFs and official IRS templates.
>
> **Remaining work:**
> - Calibrate mappings for 2020-2024 forms
> - Tier 3 (OCR) and Tier 4 (LLM validation) still deferred
> - See ROH-22 for field display review

---

## Context

The app currently uses mock extraction — it generates fake data based on the filename. This was perfect for building the UI and chatbot, but users need to see their actual tax data. This issue replaces the mock with a real tiered extraction pipeline.

**Why tiered:** Tax return PDFs come in two flavors:
1. **Digital PDFs** (most common) — Text is embedded, can be extracted directly
2. **Scanned PDFs** — Images of paper, require OCR

Direct extraction is fast, free, and highly accurate. OCR is slower, costs money, and less reliable. We use the cheap/fast method when possible, falling back to OCR only when necessary.

**Why now:** This is Phase 4 — the final piece. Phases 1-3 prepared the data layer; now we need real data to populate it.

## Summary

Build a 5-tier extraction pipeline: (1) detect PDF type, (2) extract text from digital PDFs using pdfplumber, (3) OCR scanned PDFs via Azure Document Intelligence, (4) validate all extractions with LLM, (5) flag low-confidence items for user review. The pipeline runs locally via a Python sidecar, with ephemeral cloud calls for OCR/LLM only.

## Technical Approach

### Why This Approach

A tiered approach optimizes for cost, speed, and accuracy:

| Tier | Method | Speed | Cost | Accuracy | When Used |
|------|--------|-------|------|----------|-----------|
| 1 | Type Detection | <1s | Free | N/A | Always |
| 2 | pdfplumber | <2s | Free | 99%+ | Digital PDFs (90% of returns) |
| 3 | Azure OCR | 5-10s | ~$0.01/page | 95%+ | Scanned PDFs only |
| 4 | LLM Validation | 2-3s | ~$0.01 | +1-3% | Always (catches errors) |
| 5 | User Review | N/A | Free | 100% | Low-confidence items |

Think of it like a hospital triage system — most patients get quick treatment; complex cases get specialists.

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| **OCR everything** | Simpler, one path | Expensive, slower, less accurate | 90% of PDFs don't need OCR |
| **No LLM validation** | Faster, cheaper | Miss validation errors, no cross-checks | Worth the small cost for accuracy |
| **Client-side OCR (Tesseract)** | No API costs | Poor accuracy on tax forms, slow | Tax forms need specialized OCR |
| **Build our own ML model** | No API dependency | Massive undertaking, need training data | Way out of scope |

The tiered approach balances speed, cost, and accuracy optimally.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Tauri App (Rust + React)                    │
│  ┌─────────────┐   ┌─────────────────────────────────────────────┐ │
│  │  Frontend   │   │  Python Sidecar                              │ │
│  │  (React)    │──▶│  ┌─────────────────────────────────────────┐│ │
│  │             │   │  │ Tier 1: PDF Type Detection              ││ │
│  │  Upload PDF │   │  │   └─▶ Digital? → Tier 2                 ││ │
│  │             │   │  │   └─▶ Scanned? → Tier 3                 ││ │
│  │             │   │  ├─────────────────────────────────────────┤│ │
│  │             │   │  │ Tier 2: pdfplumber (local, free)        ││ │
│  │             │   │  │   Extract text, parse Form 1040 layout  ││ │
│  │             │   │  ├─────────────────────────────────────────┤│ │
│  │             │   │  │ Tier 3: Azure OCR (cloud, ephemeral)    ││ │
│  │             │   │  │   Send image, get structured text       ││ │
│  │             │   │  ├─────────────────────────────────────────┤│ │
│  │  ◀──────────│◀──│  │ Tier 4: LLM Validation (cloud, ephemeral)│ │
│  │  Display    │   │  │   Check field relationships, flag errors││ │
│  │  Results    │   │  ├─────────────────────────────────────────┤│ │
│  │             │   │  │ Tier 5: Confidence scores per field     ││ │
│  │  Flag low   │   │  │   < 95% → needs_review = true           ││ │
│  │  confidence │   │  └─────────────────────────────────────────┘│ │
│  └─────────────┘   └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Task List

- 🟢 **Set up Python sidecar** — pdfplumber-based extraction
  - 🟢 Create extract.py with coordinate-based field extraction
  - 🟢 Create build.py for PyInstaller bundling
  - 🟢 Configure Tauri shell permissions (sidecar scope in capabilities)
  - 🟢 Create TypeScript service (`app/src/services/pdfExtractor.ts`)
- 🟢 **Tier 2: Digital PDF extraction** — pdfplumber
  - 🟢 Year-specific field mappings (2018-2025 templates created)
  - 🟢 Calibrate 2018 mapping against official IRS template
  - 🟢 Calibrate 2019 mapping (tested, working)
  - 🟡 Calibrate 2020-2024 mappings (templates exist, need verification)
  - 🟢 Extract values with confidence scores (0.9 for extracted, 0.5 for missing)
- 🟢 **Integrate with app** — Replace mock extraction
  - 🟢 Update App.tsx to use sidecar extraction
  - 🟢 Fallback to mock if sidecar unavailable
  - 🟢 Handle extraction errors gracefully
- ⏸️ **Tier 3: Scanned PDF OCR** — *Deferred*
  - ⏸️ Integrate Azure Document Intelligence
  - ⏸️ Handle ephemeral data (no storage on Azure side)
- ⏸️ **Tier 4: LLM validation** — *Deferred*
  - ⏸️ Build validation prompt (check math, relationships)
  - ⏸️ Adjust confidence scores based on validation
- ⏸️ **Tier 5: Confidence-based review** — *Deferred*
  - ⏸️ Apply 95% threshold for needs_review flag
  - ⏸️ Build review UI for user corrections

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete | ⏸️ Deferred

## Major Changes

### Python Sidecar Structure

```
app/
├── src-tauri/
│   └── python/
│       ├── requirements.txt      # pdfplumber, pymupdf, azure-ai-formrecognizer
│       ├── extract.py            # Main extraction entry point
│       ├── detect.py             # Tier 1: PDF type detection
│       ├── digital.py            # Tier 2: pdfplumber extraction
│       ├── ocr.py                # Tier 3: Azure OCR
│       ├── validate.py           # Tier 4: LLM validation
│       └── schema.py             # Field mappings and schemas
```

### Tier 1: PDF Type Detection

```python
# detect.py
import fitz  # PyMuPDF

def detect_pdf_type(pdf_path: str) -> str:
    """Detect if PDF is digital (embedded text) or scanned (image-based)."""
    doc = fitz.open(pdf_path)

    text_chars = 0
    total_pages = len(doc)

    for page in doc:
        text_chars += len(page.get_text())

    # Heuristic: Digital PDFs have significant text per page
    avg_chars_per_page = text_chars / total_pages
    if avg_chars_per_page > 500:
        return "digital"
    else:
        return "scanned"
```

### Tier 2: Digital PDF Extraction

```python
# digital.py
import pdfplumber

# Form 1040 field mappings (approximate bounding boxes)
FORM_1040_FIELDS = {
    "wages": {"page": 0, "bbox": (400, 150, 550, 170), "line": "1a"},
    "total_income": {"page": 0, "bbox": (400, 280, 550, 300), "line": "9"},
    # ... more fields
}

def extract_digital_pdf(pdf_path: str) -> dict:
    """Extract fields from digital PDF using pdfplumber."""
    fields = []

    with pdfplumber.open(pdf_path) as pdf:
        for field_key, config in FORM_1040_FIELDS.items():
            page = pdf.pages[config["page"]]
            cropped = page.crop(config["bbox"])
            text = cropped.extract_text() or ""

            fields.append({
                "key": field_key,
                "value": parse_currency(text),
                "confidence": 0.99,  # High confidence for direct extraction
                "line_number": config["line"],
            })

    return {"fields": fields, "method": "pdfplumber"}
```

### Tier 4: LLM Validation

```python
# validate.py
def validate_with_llm(fields: list) -> list:
    """Use LLM to validate extracted fields."""
    prompt = f"""
    Validate these tax return fields. Check:
    1. AGI = Total Income - Adjustments
    2. Taxable Income = AGI - Deductions
    3. Values are reasonable (no negative income, etc.)

    Fields:
    {json.dumps(fields)}

    Return JSON with:
    - any corrections needed
    - confidence adjustments
    - flags for suspicious values
    """

    response = claude_api.message(prompt)
    validation = json.loads(response)

    # Apply corrections and adjust confidence
    for field in fields:
        if field["key"] in validation.get("corrections", {}):
            field["value"] = validation["corrections"][field["key"]]
            field["confidence"] *= 0.8  # Lower confidence for corrected values

    return fields
```

### Data Flow

```
User uploads tax_return_2023.pdf
    ↓
Rust invokes Python sidecar: extract.py --file tax_return_2023.pdf
    ↓
Tier 1: detect.py → "digital"
    ↓
Tier 2: digital.py → extracts 15 fields with 99% confidence
    ↓
Tier 4: validate.py → LLM confirms math checks out, no corrections
    ↓
Tier 5: All fields > 95% confidence → needs_review = false
    ↓
Python returns JSON to Rust
    ↓
Rust inserts fields into SQLite
    ↓
React displays data in dashboard and chatbot
```

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Create | `app/src-tauri/python/` | Python sidecar directory |
| Create | `app/src-tauri/python/extract.py` | Main extraction entry point |
| Create | `app/src-tauri/python/detect.py` | PDF type detection |
| Create | `app/src-tauri/python/digital.py` | pdfplumber extraction |
| Create | `app/src-tauri/python/ocr.py` | Azure OCR integration |
| Create | `app/src-tauri/python/validate.py` | LLM validation |
| Create | `app/src-tauri/python/schema.py` | Field mappings |
| Modify | `app/src-tauri/tauri.conf.json` | Configure sidecar bundling |
| Modify | `app/src-tauri/src/lib.rs` | Add extraction command |
| Modify | `app/src/App.tsx` | Use real extraction instead of mock |
| Delete | `app/src/db/mockExtraction.ts` | Remove mock (or keep for tests) |

## Testing Strategy

### What to Test
- **Type detection** — Correctly identifies digital vs scanned PDFs
- **Digital extraction** — Extracts correct values from test Form 1040 PDFs
- **Field mapping** — Values map to correct field keys
- **LLM validation** — Catches intentional math errors in test data
- **Confidence scoring** — Low-confidence items flagged correctly

### How to Verify
1. Obtain sample Form 1040 PDFs (digital and scanned)
2. Run extraction on each
3. Compare extracted values to known correct values
4. Verify confidence scores are appropriate

```bash
# Run extraction manually
cd app/src-tauri/python
python extract.py --file ../../../test_returns/2023_1040.pdf
```

## Risks & Considerations

- **PDF layout variations:**
  - *Impact:* IRS may change Form 1040 layout year-to-year
  - *Mitigation:* Version-specific field mappings. Support 2020-2024 initially.

- **Azure API costs:**
  - *Impact:* ~$0.01/page for OCR, adds up with scanned PDFs
  - *Mitigation:* Only use for scanned PDFs. Tier 2 handles 90%+ of returns.

- **Python dependency:**
  - *Impact:* Must bundle Python with the app
  - *Mitigation:* Use PyInstaller or Nuitka to create standalone executable.

- **Privacy (API calls):**
  - *Impact:* Tax data sent to Azure/Claude APIs
  - *Mitigation:* Ephemeral only. Azure Document Intelligence doesn't store data. Claude API has data retention disabled.

## Performance Implications

| Tier | Time | Notes |
|------|------|-------|
| Detection | <1s | Local file check |
| pdfplumber | 1-3s | Local processing |
| Azure OCR | 5-15s | Network latency + processing |
| LLM Validation | 2-5s | API call |
| **Total (digital)** | **3-8s** | Most returns |
| **Total (scanned)** | **8-20s** | OCR adds time |

## Dependencies

- **pdfplumber** — Digital PDF text extraction
- **PyMuPDF (fitz)** — PDF type detection
- **azure-ai-formrecognizer** — OCR for scanned PDFs
- **anthropic** — LLM validation
- **Tauri sidecar** — Running Python from Rust

## Open Questions

1. **Python bundling:** Should we use PyInstaller (larger bundle) or require Python installed?
   - *Recommendation:* PyInstaller for seamless UX. Size is ~30MB.

2. **Which tax years to support initially?**
   - *Recommendation:* 2020-2024. Cover recent history.

3. **Review UI:** Should we build the low-confidence review UI as part of this issue?
   - *Recommendation:* Separate issue. This one is already large.

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
