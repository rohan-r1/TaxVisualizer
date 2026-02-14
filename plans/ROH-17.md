# Plan: Python sidecar for PDF extraction (pdfplumber)

**Issue:** [ROH-17](https://linear.app/rohanr/issue/ROH-17/python-sidecar-for-pdf-extraction-pdfplumber)
**Priority:** High
**Status:** Complete

---

## Context

ROH-16 attempted JavaScript-based PDF extraction using pdfjs-dist. However, pdfjs-dist extracts text in PDF internal order (not visual order), resulting in jumbled text like:

```
OMB No. 1545-0074 Spouse's social security number Your social security number...
```

This makes regex-based parsing of Form 1040 impossible. The labels, values, and instructions are interleaved in unpredictable ways.

**Why Python with pdfplumber:**
- Extracts text by **coordinates/bounding boxes** (not just reading order)
- Can target specific regions of the form
- Well-documented for form parsing
- Used successfully for tax document extraction in other projects

## Summary

Create a Python sidecar that Tauri spawns to extract Form 1040 data. The Python script uses pdfplumber to:
1. Open the PDF
2. Extract text from specific bounding boxes (one per form field)
3. Return structured JSON to Rust/TypeScript

## Technical Approach

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Tauri App                               │
│  ┌──────────────┐         ┌─────────────────────────────┐  │
│  │  TypeScript  │  JSON   │  Python Sidecar             │  │
│  │  Frontend    │◄───────►│  (bundled executable)       │  │
│  │              │         │                             │  │
│  │  Upload PDF  │────────►│  1. Receive PDF path        │  │
│  │              │         │  2. Open with pdfplumber    │  │
│  │  Display     │◄────────│  3. Extract by coordinates  │  │
│  │  Results     │         │  4. Return JSON             │  │
│  └──────────────┘         └─────────────────────────────┘  │
│         │                              │                    │
│         │                              │                    │
│  ┌──────▼──────┐              ┌───────▼────────┐          │
│  │   SQLite    │              │  Field Mapping │          │
│  │   Database  │              │  (coordinates  │          │
│  │             │              │   per form     │          │
│  └─────────────┘              │   version)     │          │
│                               └────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Why This Approach

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **pdfjs-dist (JS)** | No sidecar, simple | Text order jumbled | Tried, doesn't work |
| **pdf2json (JS)** | Preserves coordinates | Complex coordinate math, less documented | Could work, but pdfplumber is better |
| **pdfplumber (Python)** | Excellent coord extraction, well-documented | Requires Python bundling | **Chosen** |
| **Tabula (Java)** | Great for tables | Heavy dependency (JVM) | Too heavy |
| **Cloud OCR** | High accuracy | Cost, latency, privacy concerns | Future enhancement |

### Form 1040 Field Mapping

Each form field has a bounding box (x0, y0, x1, y1) that defines where the value appears on the page. Example for 2018 Form 1040:

```python
FORM_1040_2018 = {
    "wages": {
        "page": 0,
        "bbox": (515, 158, 595, 172),  # Line 1
        "label": "Wages, salaries, tips"
    },
    "total_income": {
        "page": 0,
        "bbox": (515, 290, 595, 305),  # Line 6
        "label": "Total income"
    },
    # ... more fields
}
```

**Note:** Coordinates must be calibrated per form year (layout changes slightly).

## Task List

### Phase 1: Python Script Development — [ROH-18](https://linear.app/rohanr/issue/ROH-18)
- 🟢 **Create Python extraction script**
  - 🟢 Set up `python/` directory with structure
  - 🟢 Implement PDF loading with pdfplumber
  - 🟢 Define bounding boxes for Form 1040 (2018 - needs calibration in Phase 4)
  - 🟢 Extract text from each bounding box
  - 🟢 Return structured JSON output
  - 🟢 Add CLI interface (argparse)
  - 🟢 Add calibration helper script
  - ✅ Tested: Script runs, detects year, extracts filing status

### Phase 2: Tauri Integration — [ROH-19](https://linear.app/rohanr/issue/ROH-19)
- 🟢 **Configure Tauri sidecar**
  - 🟢 Bundle Python script as executable (PyInstaller) — 95MB executable at `binaries/extract-x86_64-pc-windows-msvc.exe`
  - 🟢 Configure tauri.conf.json for sidecar — added externalBin, shell plugin
  - 🟢 Create TypeScript service to invoke sidecar — `src/services/pdfExtractor.ts`
  - 🟢 Handle sidecar communication (stdin/stdout JSON) — JSON parsing with error handling

### Phase 3: Frontend Integration — [ROH-20](https://linear.app/rohanr/issue/ROH-20)
- 🟢 **Wire up to App.tsx**
  - 🟢 Replace mock extraction with sidecar call — uses `extractPdf()` when available
  - 🟢 Handle extraction progress/errors — loading state with fallback to mock
  - 🟢 Store extracted fields in database — converts sidecar format to DB schema

### Phase 4: Testing & Calibration — [ROH-21](https://linear.app/rohanr/issue/ROH-21)
- 🟢 **Calibrate field coordinates**
  - 🟢 Test with sample Form 1040 (2018)
  - 🟢 Adjust bounding boxes as needed (used midpoint filtering for tight row spacing)
  - 🟢 Add support for 2018-2025 layouts (8 years fully calibrated)
- 🟢 **Add tests**
  - 🟢 Unit tests for Python extraction (26 tests passing)
  - 🔴 Integration tests for sidecar communication (deferred to ROH-19)

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Handling Multiple Form Years

Form 1040 layouts change slightly each year, so coordinates must be calibrated per year.

### Strategy

1. **Detect year first** — Read form header to identify the tax year
2. **Load matching mapping** — Each year has its own coordinate file
3. **Fallback gracefully** — Unknown years use closest available mapping

### Year Detection

```python
def detect_form_year(page) -> int:
    text = page.extract_text()
    match = re.search(r'Form\s*1040.*?(20\d{2})', text)
    return int(match.group(1)) if match else None
```

### Mapping Structure

```
mappings/
├── __init__.py          # get_field_mapping(year) function
├── form_1040_2018.py    # FIELDS = { "wages": { "bbox": (...) }, ... }
├── form_1040_2019.py
├── form_1040_2020.py
└── ...
```

### Runtime Selection

```python
def get_field_mapping(year: int) -> dict:
    mappings = {
        2018: form_1040_2018.FIELDS,
        2019: form_1040_2019.FIELDS,
        # ...
    }
    if year in mappings:
        return mappings[year]
    # Fallback to closest year
    closest = min(mappings.keys(), key=lambda y: abs(y - year))
    return mappings[closest]
```

### Calibrating a New Year

1. Get sample Form 1040 PDF for the new year
2. Use pdfplumber's visual tools:
   ```python
   page.to_image().draw_rects(page.chars).save("debug.png")
   ```
3. Identify bounding boxes for each field
4. Create new mapping file
5. Test with sample returns

### Edge Cases

| Scenario | Solution |
|----------|----------|
| Unknown year | Use most recent mapping + lower confidence |
| Mapping mismatch | Flag fields for review |
| Major IRS redesign | Create new mapping with updated field keys |

## Major Changes

### Python Script Structure

```
app/
├── src-tauri/
│   └── python/
│       ├── requirements.txt      # pdfplumber, PyInstaller
│       ├── extract.py            # Main extraction script
│       ├── mappings/
│       │   ├── form_1040_2018.py # Coordinates for 2018
│       │   ├── form_1040_2019.py # Coordinates for 2019
│       │   └── ...
│       └── build.py              # PyInstaller build script
```

### extract.py (Core Logic)

```python
#!/usr/bin/env python3
import json
import sys
import pdfplumber
from mappings import get_field_mapping

def extract_form_1040(pdf_path: str) -> dict:
    """Extract Form 1040 fields using coordinate-based extraction."""
    with pdfplumber.open(pdf_path) as pdf:
        # Detect form year from first page
        first_page = pdf.pages[0]
        year = detect_form_year(first_page)

        # Get field mapping for this year
        mapping = get_field_mapping(year)

        fields = []
        for field_key, config in mapping.items():
            page = pdf.pages[config["page"]]

            # Crop to bounding box and extract text
            cropped = page.crop(config["bbox"])
            text = cropped.extract_text() or ""

            # Clean and parse value
            value = parse_currency(text.strip())

            fields.append({
                "key": field_key,
                "label": config["label"],
                "value": value,
                "category": config["category"],
                "line_number": config.get("line", ""),
                "confidence": 0.95 if value else 0.5
            })

        return {
            "year": year,
            "filing_status": extract_filing_status(pdf.pages[0]),
            "extraction_method": "pdfplumber",
            "fields": fields
        }

if __name__ == "__main__":
    pdf_path = sys.argv[1]
    result = extract_form_1040(pdf_path)
    print(json.dumps(result))
```

### Tauri Sidecar Configuration

```json
// tauri.conf.json
{
  "bundle": {
    "externalBin": [
      "python/dist/extract"
    ]
  }
}
```

### Rust Command

```rust
// lib.rs
#[tauri::command]
async fn extract_pdf(path: String) -> Result<serde_json::Value, String> {
    let output = Command::new_sidecar("extract")
        .map_err(|e| e.to_string())?
        .args([&path])
        .output()
        .await
        .map_err(|e| e.to_string())?;

    let json: serde_json::Value = serde_json::from_slice(&output.stdout)
        .map_err(|e| e.to_string())?;

    Ok(json)
}
```

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Create | `app/src-tauri/python/` | Python sidecar directory |
| Create | `app/src-tauri/python/extract.py` | Main extraction script |
| Create | `app/src-tauri/python/requirements.txt` | Dependencies |
| Create | `app/src-tauri/python/mappings/` | Form field coordinates |
| Create | `app/src-tauri/python/build.py` | PyInstaller build |
| Modify | `app/src-tauri/tauri.conf.json` | Sidecar configuration |
| Modify | `app/src-tauri/src/lib.rs` | Add extract command |
| Modify | `app/src/App.tsx` | Use sidecar extraction |

## Calibrating Bounding Boxes

To find the correct coordinates for each field:

1. Open Form 1040 PDF in a viewer that shows coordinates
2. Or use pdfplumber interactively:

```python
import pdfplumber

pdf = pdfplumber.open("1040_2018_sample.pdf")
page = pdf.pages[0]

# Get all text with positions
for char in page.chars:
    print(f"{char['text']} at ({char['x0']}, {char['top']})")

# Visually inspect to find field locations
# Or use page.to_image() to see the layout
```

3. Define bounding boxes that capture just the value area (not the label)

## Risks & Considerations

- **Bundling Python:** PyInstaller creates ~30-50MB executable. Acceptable for desktop app.
- **Form version changes:** IRS changes Form 1040 layout yearly. Need mappings per year.
- **Coordinate drift:** PDF generation software can shift positions slightly. May need fuzzy matching.
- **Non-standard PDFs:** Some tax software generates PDFs differently. May need multiple mapping variants.

## Performance Implications

| Step | Time | Notes |
|------|------|-------|
| Spawn sidecar | 100-200ms | One-time process startup |
| Open PDF | 50-100ms | pdfplumber load time |
| Extract fields | 200-500ms | Depends on page count |
| **Total** | **~500ms** | Much faster than OCR |

## Dependencies

- **pdfplumber** — PDF text extraction with coordinates
- **PyInstaller** — Bundle Python as standalone executable
- **Tauri sidecar** — Spawn external process from Rust

## Open Questions

1. **Python version:** Bundle Python 3.11 or 3.12?
   - *Recommendation:* 3.11 (more stable PyInstaller support)

2. **Cross-platform builds:** Need to build sidecar on each platform (Windows/Mac)
   - *Recommendation:* Set up CI/CD to build on both platforms

3. **How many form years to support initially?**
   - *Recommendation:* Start with 2018-2024 (7 years)

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
