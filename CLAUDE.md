# TaxVisualizer

## Project Overview
A cross-platform desktop application for individual tax filers to visualize and compare tax returns year-over-year. Users upload PDF tax returns, which are parsed via a tiered hybrid extraction pipeline, and the app displays dashboards showing tax liability trends, deduction patterns, and lifetime tax payments.

## Scope
- Individual filers only (Form 1040 and common schedules)
- **Tax years 2020 and later** (pre-2020 returns show user-friendly error)
- Business returns (1120, 1120-S, 1065) are out of scope

## Platform
- **Type:** Downloadable desktop application (not a web app)
- **Framework:** Tauri v2 (Rust backend + React frontend)
- **Platforms:** Mac and Windows
- **Distribution:** Packaged installers for both platforms with code signing

## Privacy Principles
Privacy is the top priority. Every architectural decision defaults to protecting user data.
- **Local-only storage:** All user data (tax returns, extracted data, SQLite DB) stays on the user's machine
- **Ephemeral API usage:** When external APIs are needed (OCR, LLM validation), data is sent transiently and any temporary copies outside the local machine are deleted immediately after processing
- **No telemetry:** No user financial data is transmitted for analytics or telemetry
- **Encryption at rest:** Local SQLite database encrypted on disk

## Design Principles
- **Stable input, flexible output:** The core input is always tax returns (Form 1040 + schedules). This will not change. The output layer (data presentation, visualizations, comparisons) must be flexible and extensible.
- **Extensible visualization layer:** New comparisons, views, filters, and date selectors should be addable without refactoring existing code. Design the output layer so that adding a new metric or chart is a localized change, not a structural one.
- **Clean data/view separation:** The normalized tax data schema and computation engine are the stable foundation. Views and visualizations consume computed data through a well-defined interface, so either side can evolve independently.

## Architecture

### Data Flow
PDF Upload (local) -> PaddleOCR Extraction -> Math Validation -> Normalized Schema (SQLite) -> Computed Metrics -> Visualizations (Recharts)

### Tech Stack
- **Desktop framework:** Tauri v2 (Rust backend, React frontend)
- **Frontend:** React + TypeScript + Recharts
- **Testing:** Vitest + React Testing Library + jsdom (151 tests across 11 files)
- **Fonts:** Inter (UI), JetBrains Mono (numbers/data)
- **Database:** SQLite (local, single-file, via tauri-plugin-sql)
- **PDF extraction:** Python sidecar with PaddleOCR (works for both digital and scanned PDFs)
- **PDF viewing:** PDF.js in the React frontend
- **Validation:** Local math validation (checks field relationships like AGI = income - adjustments)
- **Future:** IRS transcript integration, tax software API import, manual entry

### Data Model
- **User** -> **TaxReturns** (one per year)
  - Filing metadata (year, filing status, state)
  - Income components: wages, self-employment, investment, retirement, other
  - Deductions: above-the-line adjustments, standard/itemized, QBI
  - Credits: non-refundable and refundable
  - Tax calculation: AGI, taxable income, total tax, effective rate, marginal bracket
  - Payments & withholding
  - Final amounts (refund/owed)
  - Raw source backup (PDF stored locally, parsed JSON)

## User Journey
1. **Upload** — User uploads one or more tax return PDFs (can always add more or delete existing ones)
2. **Clarify** — System flags low-confidence extractions (especially from scanned/OCR PDFs) for user review and correction
3. **View & Interact** — User sees key numbers and visualizations from their returns
4. **Chat** — User can ask questions about their data via an integrated chatbot

## MVP Scope
- Display key numbers from each uploaded tax return
- Year-by-year chart when multiple returns are uploaded
- Add/delete returns at any time
- Chatbot for asking questions about the data
- Architecture supports adding new widgets/charts as localized additions (no refactoring needed)

## Future Views (post-MVP)
1. **Executive Summary Dashboard** - YoY comparisons of total tax, effective rate, refund/owed, income, deductions; lifetime totals as hero metrics
2. **Income Breakdown** - Income composition (W-2, self-employment, investment, retirement, other) with YoY changes
3. **Tax & Deductions Deep Dive** - Tax calculation waterfall, credits claimed, deduction comparison

## Key Technical Constraints
- Desktop app; all data stored locally on user's machine (no server-side storage)
- PaddleOCR runs locally — no cloud API calls for extraction
- Confidence scores per field from OCR; math validation catches extraction errors
- Support tax years 2020+ (5 years of history)
- Computed/derived fields (effective tax rate, etc.) should be recomputable from base data
- State returns vary significantly; consider starting federal-only

## UI Design
- **Dark mode first** — Cron.com-inspired warm palette (`#0f0d0a` bg, `#1e1c18` surfaces, `#ff4700` orange accent)
- **Key numbers** — borderless tabular layout: metric labels as rows, tax years as columns
- **Charts** — Recharts LineChart with styled dark tooltips; colors: orange (income), coral (tax), green (refund), amber (owed)
- **Widget system** — `src/widgets/registry.ts` array; add new widget = add one entry + component file
- **CSS variables** throughout `App.css` for consistent theming
- **Chatbot** — Bottom-anchored panel aligned with content area, Claude API with streaming

## Key Files
- `app/src/App.tsx` — main component, state management, upload/delete handlers
- `app/src/App.css` — all styles, CSS variables for theming
- `app/src/db/database.ts` — SQLite access layer (getDb, getAllReturns, insertReturn, deleteReturn, buildSummary)
- `app/src/db/mockExtraction.ts` — mock extraction with Form 1040 + Schedules A/C/D fields (fallback when sidecar unavailable)
- `app/src/services/pdfExtractor.ts` — TypeScript service to invoke Python sidecar
- `app/src/services/extractionValidator.ts` — Math validation for extracted fields
- `app/src-tauri/python/extract.py` — Python sidecar for PDF extraction with PaddleOCR
- `app/src-tauri/python/build.py` — PyInstaller build script for sidecar executable
- `test-data/manual-returns/alex_chen/` — Hand-filled test PDFs for Alex Chen persona (2020-2024)
- `test-data/blank-templates/` — IRS official blank Form 1040 templates (2020-2024)
- `app/src/widgets/registry.ts` — widget registry pattern for extensibility
- `app/src/widgets/KeyNumbersWidget.tsx` — tabular key numbers display
- `app/src/widgets/YearOverYearChart.tsx` — YoY line chart
- `app/src/components/Chatbot/` — ChatbotPanel, ChatbotInput, ChatbotMessage components
- `app/src/components/Settings/` — SettingsPanel for API key configuration
- `app/src/services/claude.ts` — Claude API client with streaming
- `app/src/services/taxContext.ts` — Serializes tax data for LLM context
- `app/src/test/fixtures.ts` — shared test data factories (makeReturn, makeField, makeSummary, etc.)
- `app/src-tauri/src/lib.rs` — Rust backend with SQLite migrations and plugin registration
- `plans/` — Active execution plans for Linear issues (created by `/plan` command)
- `plans/archive/` — Completed plans (22 archived)
- `learning-notes/` — Technical explanations for PM education (created by `/learning-opportunity` command)

## Current Status
MVP fully functional with PaddleOCR-based PDF extraction. Python sidecar uses OCR label matching (no brittle coordinate mappings) to extract Form 1040 + Schedule 1, 2, A, C fields. Math validation (ROH-39 complete) catches extraction errors by checking field relationships. Supports tax years 2020+ only; pre-2020 returns show user-friendly error. Test data: Alex Chen persona with hand-filled PDFs (2020-2024). Upload summary overlay shows extraction results. Cron.com-inspired dark UI with collapsible sidebar and full-height chatbot panel. GitHub repo: https://github.com/rohan-r1/TaxVisualizer

### Active Issues
- **ROH-36:** Add schedule data to charts — plan ready, needs `/execute`
- **ROH-31:** Make fonts and font sizes uniform across the application (Medium priority)
- **ROH-15:** Encryption at rest — deferred (waiting for official SQLCipher support in tauri-plugin-sql)

## Next Steps
1. **ROH-36:** Execute plan to expose schedule data in charts (fix naming mismatch in `chart.ts` and `claude.ts`)
2. **ROH-31:** Standardize typography — audit and unify font usage (Inter for UI, JetBrains Mono for numbers/data)
3. **ROH-15:** Monitor for official SQLCipher support, then implement encryption

## Git Commits
- Do NOT include `Co-Authored-By` lines in commit messages
- Keep commit messages concise and descriptive

## Linear Workflow
Custom slash commands for issue tracking (require `LINEAR_API_KEY` and `LINEAR_TEAM_ID` env vars):
- `/create-issue <description>` — Create a new Linear issue
- `/plan ROH-XX` — Create execution plan (planning only, does NOT execute); auto-creates sub-issues for phased approaches
- `/execute` — Execute the most recent plan, updating task status as you go
- `/learning-opportunity` — Create educational note explaining selected code/concept (saved to `learning-notes/`)

**IMPORTANT:** Plans must ONLY be executed via the `/execute` command. Do NOT implement plans when they are pasted into chat, even if the user says "implement this plan" or similar. Always wait for an explicit `/execute` command.

## Roles
- PM makes all product/UX decisions
- CTO advises on technical approach and builds application
