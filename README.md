# TaxVisualizer

A desktop app that lets you upload your tax returns as PDFs and see your tax data visualized over time. Upload returns from different years to compare income, deductions, tax liability, and refunds at a glance.

Built for individual filers (Form 1040). All data stays on your machine.

## What It Does

- **Upload tax return PDFs** — supports both digital and scanned returns using OCR
- **Automatic extraction** — pulls key numbers from Form 1040 and common schedules (1, 2, A, C)
- **Year-over-year charts** — visualize trends in income, taxes paid, effective rate, and refunds
- **Key numbers dashboard** — see your most important tax metrics in a clean tabular layout
- **Built-in chatbot** — ask questions about your tax data using Claude
- **Math validation** — cross-checks extracted values (e.g., AGI = income - adjustments) to catch OCR errors

Supports tax years 2020 and later.

## Privacy

Your financial data never leaves your computer. Tax returns, extracted data, and the SQLite database all live locally. When the chatbot is used, only the relevant tax context is sent transiently to the Claude API — nothing is stored remotely. No telemetry, no analytics on your financial data.

## Tech Stack

- **Desktop framework:** [Tauri v2](https://v2.tauri.app/) (Rust backend + React frontend)
- **Frontend:** React, TypeScript, Recharts
- **Database:** SQLite (local, single-file)
- **PDF extraction:** Python sidecar with [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- **Chatbot:** Claude API with streaming responses
- **Testing:** Vitest + React Testing Library (190 tests)

## Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- [Rust](https://www.rust-lang.org/tools/install)
- [Python 3.11+](https://www.python.org/downloads/)
- Python packages: `pip install -r app/src-tauri/python/requirements.txt`

## Setup

```bash
cd app
npm install
npm run build:sidecar   # builds the PDF extraction binary (one-time, takes a few minutes)
```

## Development

```bash
cd app
npm run tauri dev
```

This starts the Vite dev server and launches the native desktop window. The first Rust compilation takes a minute or two; subsequent starts are fast.

## Testing

```bash
cd app
npm test
```

## Project Structure

```
app/
├── src/                    # React frontend
│   ├── components/         # UI components (upload, sidebar, chatbot, settings)
│   ├── widgets/            # Dashboard widgets (key numbers, charts)
│   ├── services/           # PDF extraction, validation, Claude API, chart logic
│   └── db/                 # SQLite access layer
├── src-tauri/
│   ├── src/                # Rust backend
│   ├── python/             # Python sidecar (PaddleOCR extraction)
│   │   ├── extract.py      # Extraction script
│   │   ├── build.py        # PyInstaller build script
│   │   └── requirements.txt
│   └── binaries/           # Built sidecar executable (gitignored)
└── package.json
```

## How It Works

1. You upload a tax return PDF
2. The Python sidecar renders each page and runs PaddleOCR to extract text
3. A label-matching algorithm identifies form fields (no brittle coordinate mappings)
4. Math validation checks that extracted values are internally consistent
5. Validated data is stored in a local SQLite database
6. The dashboard displays your data with charts and key metrics

## License

Private repository.
