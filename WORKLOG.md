# Work Log

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
