# Work Log

## 2026-02-16

### Work Done
- ROH-26: Recalibrated PDF extractor mappings for years 2018-2021
  - 2018: Complete recalibration to page 0, tight y-ranges around character midpoints
  - 2019: Complete rewrite with measured positions from generated PDFs
  - 2020: Fixed total_tax truncation (x0 was missing leading digit)
  - 2021: Complete rewrite with wider x-range for 6-digit numbers
- All Alex Chen returns (2018-2024) now extract correctly
- All Maria Garcia returns (2019-2024) now extract correctly
- 151 tests passing

### Debugging Approach
- Used pdfplumber to inspect exact character positions (x0, mid_y)
- Tightened bbox y-ranges to ±3-5pt around measured midpoints to avoid template text overlap
- Widened bbox x-ranges (x0=515-525) to capture longer numbers

### Issues Encountered
- Template text at close y-positions caused mixed extractions — fixed with tighter y-ranges
- 6-digit numbers (105000) started at x=519.5, bbox x0=520 missed first digit — widened to x0=515
- Maria Garcia 2018 has coversheet on page 0, values on page 1 (generator inconsistency, not extractor issue)

### Next Steps
- Fix generator coversheet handling for consistent page structure
- ROH-11: Move upload button to sidebar below returns list
- ROH-15: Encryption at rest with SQLCipher

---

## 2026-02-15

### Work Done
- Completed ROH-25: Test data generator with multi-year personas
  - Rewrote `generate_sample_returns.py` to overlay values onto IRS blank templates
  - Created two 7-year personas (2018-2024): Alex Chen (software engineer) and Maria Garcia (nurse to admin)
  - Built TaxCalculator with correct bracket math for all years (2018-2024)
  - Handled year-specific form layouts (2018 postcard format, 2019+ split pages, coversheet pages)
  - Generated 14 PDFs + 14 JSON sidecars with expected values
  - Reorganized test-data/ folder into blank-templates/, generated/, samples/
  - Fixed coordinate alignment issues through multiple calibration iterations
- Completed ROH-24: Comprehensive PDF extraction testing framework
  - Added accuracy tests comparing extracted values against expected JSON sidecars

### Decisions Made
- Template overlay approach: generate test PDFs by overlaying text onto actual IRS blank templates (vs creating custom layouts)
- Year-specific field position overrides needed because IRS templates vary in structure
- Two contrasting personas for comprehensive testing: single→married progression (Alex) vs married→head of household (Maria)

### Issues Encountered
- IRS templates have different page structures across years (2018/2019 have coversheets, 2020+ don't)
- Field coordinates calibrated for extraction don't match template positions — created TEMPLATE_FIELD_OVERRIDES
- Multiple iterations needed to align values with form lines (12pt row height)
- 2019 capital_gains field was missing from overrides, causing overlap with total_income

### Next Steps
- Focus on user experience improvements
- ROH-11: Move upload button to sidebar below returns list
- ROH-15: Encryption at rest with SQLCipher

---

## 2026-02-14

### Work Done
- Implemented Python sidecar for real PDF extraction (ROH-16)
  - Created `extract.py` with pdfplumber-based coordinate extraction
  - Built year-specific field mappings for Form 1040 (2018-2025)
  - Configured Tauri v2 shell permissions with sidecar scope
  - Created TypeScript service (`pdfExtractor.ts`) to invoke sidecar
  - Added PyInstaller build script for bundling executable
- Fixed Tauri sidecar permissions issue
  - Root cause: `shell:allow-execute` needs object format with `allow` array, not just string
  - Added sidecar scope: `{ "identifier": "shell:allow-execute", "allow": [{ "name": "binaries/extract", "sidecar": true, "args": true }] }`
- Calibrated 2018 Form 1040 mapping against official IRS template
  - Fixed incorrect field labels (was calling wages "total_income", etc.)
  - Corrected bounding box coordinates for amount_owed (line 22)
  - Tested extraction on 2018 and 2019 sample PDFs — working correctly
- Created Linear issue ROH-22: Review extracted fields to display in summary
  - Currently parsing 14 fields but only displaying 9 in KeyNumbersWidget
- Created learning note explaining sidecar pattern (`learning-notes/2026-02-12-python-sidecar.md`)
- Pushed all changes to GitHub (commit `1bdb55e`)

### Decisions Made
- Use Python sidecar with pdfplumber instead of pdfjs-dist (better layout preservation)
- Coordinate-based extraction with year-specific mappings for Form 1040
- Fall back to mock extraction if sidecar is unavailable

### Issues Encountered
- pdfjs-dist text extraction doesn't preserve Form 1040 layout well enough for reliable extraction
- Official IRS template PDFs have different page structure than sample filled PDFs (coversheet adds page)
- Field value 1,663 was being captured as "applied_to_next_year" instead of "amount_owed" — fixed by adjusting y-coordinates

### Next Steps
- ROH-22: Review which extracted fields to display in summary
- Calibrate 2020-2024 Form 1040 mappings
- ROH-15: Encryption at rest with SQLCipher

---

## 2026-02-12

### Work Done
- Executed ROH-10: Always-visible chatbot input that expands on focus
  - Collapsed state shows input bar at bottom, expands to full panel on focus/submit
  - Click-outside-to-collapse behavior with smooth animations
  - Updated `app/src/components/Chatbot/ChatbotPanel.tsx` and `app/src/App.css`
- Fixed ROH-12: Chatbot response disappearing bug
  - Root cause: stale closure + React functional update timing issue
  - Fix: capture `streamingContentRef.current` to local variable before `setMessages`
  - Created learning note at `learning-notes/2026-02-12-stale-closures-and-useref-fix.md`
- Executed ROH-13: Give chatbot deeper access to parsed tax data
  - `buildTaxContext` now serializes detailed fields by category
  - Includes line numbers, confidence warnings
  - Updated `app/src/services/taxContext.ts`
- Executed ROH-14: Enhanced parsing for Schedules A, C, D
  - `mockExtraction.ts` generates schedule-specific fields
  - Smart schedule inclusion based on income level (probabilistic)
  - Added schedule category labels to taxContext
  - New test fixtures: `makeScheduleAFields()`, `makeScheduleCFields()`, `makeScheduleDFields()`
- Created plans for ROH-15 (encryption at rest) and ROH-16 (real PDF extraction)
- Enhanced `/plan` skill to auto-create Linear sub-issues for phased approaches
- Created `/learning-opportunity` global skill for PM education
- Pushed all changes to GitHub (commit `19933d9`)

### Decisions Made
- Phased approach for complex issues: original issue becomes master, all phases become sub-issues
- Learning notes stored in `learning-notes/` folder with date-prefixed filenames

### Issues Encountered
- ROH-12 bug resurfaced after ROH-14 due to subtle timing issue: React functional updates don't read `.current` until processing, but `finally` block clears ref first
- Fixed by capturing ref value to local variable before passing to `setMessages`

### Next Steps
- Execute ROH-11: Move upload button to sidebar below returns list
- Execute ROH-15: Encryption at rest with SQLCipher
- Execute ROH-16: Real PDF extraction pipeline

---

## 2026-02-11 (Session 2)

### Work Done
- Executed ROH-9: Updated color scheme to Cron.com aesthetic
  - Warm brown-black backgrounds (`#0f0d0a`, `#161412`, `#1e1c18`)
  - Orange-red accent (`#ff4700`), amber warning (`#ffaa00`)
  - Updated `app/src/App.css` and `app/src/widgets/YearOverYearChart.tsx`
- Created plan for ROH-10 (chatbot always-visible input that expands on focus) at `plans/ROH-10.md`
- Updated `/plan` slash command to explicitly NOT auto-execute after planning
- Created Linear issue ROH-12: Bug where chatbot response appears briefly then disappears
- Updated ROH-11: Changed upload button position from top of sidebar to below returns list
- Initialized git repository and pushed to GitHub: https://github.com/rohan-r1/TaxVisualizer
- Created `SETUP.md` with setup instructions for new machines
- Added git commit guidelines to CLAUDE.md (no Co-Authored-By lines)

### Decisions Made
- Color scheme changed from pastel zinc to Cron.com-inspired warm browns with orange accents
- Commits should not include Co-Authored-By attribution lines

### Issues Encountered
- LINEAR_TEAM_ID environment variable was set to "ROH" but API requires UUID — used teams query to get correct UUID
- Accidentally started executing after `/plan` approved — fixed by updating skill instructions

### Next Steps
- Execute ROH-10: Chatbot always-visible input
- Investigate ROH-12: Chatbot response disappearing bug (urgent)
- Execute ROH-11: Move upload button to sidebar

---

## 2026-02-11

### Work Done
- Built and launched the Tauri v2 app for the first time — resolved MSVC linker issue (needed VS Build Tools with C++ workload)
- Fixed Tauri v2 SQL permissions — added `sql:allow-execute` and `sql:allow-select` to capabilities
- Wrote comprehensive test suite: 70 tests across 9 files (Vitest + React Testing Library)
  - `src/db/__tests__/buildSummary.test.ts` — 9 tests for summary computation
  - `src/db/__tests__/mockExtraction.test.ts` — 13 tests for mock data generation
  - `src/components/__tests__/ReturnsList.test.tsx` — 8 tests
  - `src/components/__tests__/Dashboard.test.tsx` — 5 tests
  - `src/components/__tests__/UploadButton.test.tsx` — 5 tests
  - `src/widgets/__tests__/KeyNumbersWidget.test.tsx` — 10 tests
  - `src/widgets/__tests__/YearOverYearChart.test.tsx` — 5 tests
  - `src/widgets/__tests__/registry.test.ts` — 5 tests
  - `src/App.test.tsx` — 10 integration tests
- Redesigned UI: dark mode, modern fonts (Inter + JetBrains Mono), CSS variables throughout
- Redesigned KeyNumbersWidget from card grid to tabular layout (metrics as rows, years as columns)
- Converted YearOverYearChart from BarChart to LineChart with styled tooltips
- Uploaded 3 sample tax returns and verified full flow works end-to-end
- Created `/wrapup` slash command skill at `.claude/skills/wrapup/SKILL.md` (not yet working — needs debugging)

### Decisions Made
- Dark mode is the default (not behind `prefers-color-scheme` media query)
- Color palette: deep navy backgrounds (`#0f1219`, `#161b26`, `#1e2433`), indigo accent (`#818cf8`), chart colors: indigo/red/green/amber
- Numbers use JetBrains Mono font; UI text uses Inter
- Key numbers displayed in a borderless table layout rather than individual metric cards

### Issues Encountered
- Rust linker failed because `link.exe` resolved to Git Bash's `link` instead of MSVC — fixed by installing VS Build Tools with C++ workload
- Port 1420 persisted between dev server restarts — needed to kill the process manually
- `ResizeObserver` mock for Recharts needed to be a proper class (not `vi.fn().mockImplementation`) to work as a constructor
- `/wrapup` slash command created but not recognized — needs investigation (may be a path or config issue)

### Next Steps
- Fix `/wrapup` slash command so it's recognized by Claude Code
- Continue UI refinement
- Integrate chatbot (chat panel + LLM API + tax data context)
- Replace mock extraction with real PDF extraction pipeline

---
