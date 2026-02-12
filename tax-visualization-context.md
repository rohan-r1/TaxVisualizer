# Tax Return Visualization Application - Project Context

## Project Overview
Building an application to help individual tax filers visualize and compare their tax returns year-over-year, with the goal of understanding tax liability trends, deduction patterns, and lifetime tax payments.

## Core User Questions to Answer
1. What did my tax return look like this year compared to last year?
2. Did I pay more or less tax?
3. How did my deductions compare?
4. What is the total tax I have paid over my lifetime (across all uploaded returns)?

## Scope
- **Focus:** Individual filers only (Form 1040 and common schedules)
- **Out of scope (for now):** Business returns (1120, 1120-S, 1065)

## Core User Journey
1. **Upload** — User uploads one or more tax return PDFs (minimum one, no maximum). Users can always add more returns or delete existing ones at any time.
2. **Clarify** — System flags low-confidence extractions (especially from scanned/OCR PDFs) for user review and correction.
3. **View & Interact** — User sees key numbers and visualizations from their returns, with filters and selectors.
4. **Chat** — User can ask questions about their data via an integrated chatbot.

## MVP Scope
- Display key numbers from each uploaded tax return
- Year-by-year comparison chart when multiple returns are uploaded
- Add/delete returns at any time
- Chatbot for asking questions about the data
- Widget-based architecture: new charts/comparisons can be added as localized changes without refactoring

## Product Vision - Future Feature Set

### Three Core Views (post-MVP)

#### 1. Executive Summary Dashboard
The "at-a-glance" view featuring:
- Total tax paid (federal + state) - YoY comparison
- Effective tax rate - YoY comparison
- Refund/owed - YoY comparison
- Total income - YoY comparison
- Deductions used (standard vs. itemized) - YoY comparison
- **Lifetime totals** in hero metrics at top

#### 2. Income Breakdown
Visualize income composition with YoY changes:
- W-2 wages
- Self-employment income
- Investment income (interest, dividends, capital gains)
- Retirement income
- Other income
- Show how composition changes year-over-year

#### 3. Tax & Deductions Deep Dive
- Tax calculation waterfall: Income → AGI → Taxable Income → Tax → Credits → Final
- Credits claimed
- Deduction comparison
  - If itemized: show categories
  - If standard: optionally show what was "left on the table"

## User Personas & Metric Prioritization

### Casual Filer (W-2 employee, standard deduction)
Priority metrics:
- Total tax paid
- Effective tax rate
- Refund/owed amount
- W-2 income
- Withholding accuracy
- Federal vs. state breakdown

### Financially Engaged (itemizes, has investments)
All casual filer metrics, plus:
- Itemized vs. standard deduction comparison
- Investment income trends
- Capital gains/losses
- Retirement contributions
- Charitable giving patterns
- SALT deduction tracking

### Self-Employed/Freelancer
- Business income trends
- Self-employment tax
- Quarterly estimated payment patterns
- Business expense categories
- Home office deduction
- Health insurance deduction
- Retirement contributions (SEP-IRA, Solo 401k)

### High Earner/Complex
- Marginal vs. effective tax rate
- AMT exposure
- Net Investment Income Tax (NIIT)
- Additional Medicare Tax
- Tax loss harvesting effectiveness
- QBI deduction optimization

## Comprehensive Tax Return Metrics

### Income Components
**Wages & Salary:**
- W-2 wages, federal withholding, Social Security wages/tax, Medicare wages/tax
- Tips, dependent care benefits, employer retirement contributions

**Self-Employment (Schedule C):**
- Gross receipts/sales, returns, COGS, gross profit
- Expenses: advertising, car, commissions, contract labor, depreciation, insurance, legal, office, rent, repairs, supplies, taxes, travel, meals, utilities, wages, home office
- Net profit/loss

**Investment Income (Schedule B & D):**
- Interest (taxable & tax-exempt)
- Ordinary & qualified dividends
- Short-term & long-term capital gains/losses
- Net capital gain/loss, capital loss carryover
- Cost basis, proceeds

**Retirement Income:**
- IRA distributions (total & taxable)
- Pensions/annuities (total & taxable)
- Social Security benefits (total & taxable)

**Other Income:**
- Unemployment, alimony, business, rental, farm income
- Other gains/losses, gambling, prizes, scholarships

### Deductions & Adjustments

**Above-the-Line (Adjustments to Income):**
- Educator expenses, HSA, self-employment tax (deductible portion)
- Self-employed health insurance, retirement plans
- IRA deduction, student loan interest

**Standard vs. Itemized:**
- Standard deduction amount OR
- Itemized total

**Itemized Deductions (Schedule A):**
- Medical/dental expenses
- SALT (state/local income or sales taxes, real estate, personal property - $10k cap)
- Mortgage interest, investment interest
- Charitable contributions (cash & non-cash)
- Casualty/theft losses

**QBI Deduction:**
- Qualified Business Income deduction (Form 8995/8995-A)

### Tax Calculation
- Total income
- AGI (Adjusted Gross Income)
- Taxable income
- Tax liability (from brackets)
- Alternative Minimum Tax (if applicable)
- Total tax before credits

### Credits
**Non-Refundable:**
- Child Tax Credit, Credit for other dependents
- Education credits (American Opportunity, Lifetime Learning)
- Retirement savings credit, residential energy credits
- Foreign tax credit, child/dependent care credit

**Refundable:**
- Earned Income Tax Credit (EITC)
- Additional Child Tax Credit
- American Opportunity Credit (refundable portion)

### Other Taxes
- Self-employment tax
- Additional Medicare Tax (0.9%)
- Net Investment Income Tax (3.8%)

### Payments & Withholding
- Federal income tax withheld
- Estimated tax payments (quarterly)
- Amount applied from prior year

### Final Calculation
- Total tax liability
- Total payments and credits
- **Amount owed OR Refund amount**

### Filing Information
- Filing status (Single, MFJ, MFS, HoH, QW)
- Number of dependents
- Age, blind status

### State-Level (varies by state)
- State AGI, state-specific additions/subtractions
- State tax liability, credits, withholding
- State refund/owed

## Platform & Architecture

### Application Type
- **Downloadable desktop application** (not a web app)
- **Framework:** Tauri v2 (Rust backend + React frontend)
- **Platforms:** Mac and Windows
- **Distribution:** Packaged installers with code signing for both platforms

### Local-First Architecture
- All user data stored locally on the user's machine (SQLite database + PDF files)
- No server-side storage of user data
- **Database:** SQLite (single-file, encrypted at rest, via tauri-plugin-sql)
- **Frontend:** React + TypeScript + Recharts

### Privacy Principles
Privacy is the top priority. Every architectural decision defaults to protecting user data.
- **Local-only storage:** Tax returns, extracted data, and all user information stay on the user's machine
- **Ephemeral API usage:** When external APIs are needed (OCR for scanned PDFs, LLM validation), data is sent transiently and any temporary copies outside the local machine are deleted immediately after processing
- **No telemetry:** No user financial data is transmitted for analytics or tracking
- **Encryption at rest:** Local SQLite database encrypted on disk

## Design Principles

### Stable Input, Flexible Output
- **Input is fixed:** The core input is always tax returns (Form 1040 and common schedules). This will not change.
- **Output is flexible:** What data we present, how we visualize it, what filters/selectors are available, and what comparisons we offer will evolve over time.
- The architecture must support adding new comparisons, views, filters, and date selectors without refactoring or restructuring existing code.

### Extensibility Requirements
- Adding a new metric or chart should be a **localized change** — not a structural one
- The normalized data schema and computation engine are the stable foundation
- Views and visualizations consume computed data through a well-defined interface
- Either side (data layer or view layer) can evolve independently
- Users may want to: filter by year range, focus on specific income types, compare specific deductions, toggle between chart types

## Technical Approach

### Data Ingestion Strategy - RECOMMENDED: Tiered Hybrid Extraction

Users upload PDF tax returns. The system routes each PDF through the optimal extraction path for maximum accuracy.

**Tier 1 - PDF Type Detection**
- Programmatically detect if PDF is digital (embedded text from TurboTax, H&R Block, etc.) or scanned (image-based paper copies)
- Use PyMuPDF heuristics: attempt text extraction, compare page count to image count

**Tier 2 - Digital PDF Extraction** (most common case)
- Direct text extraction via pdfplumber — no OCR needed
- Near-100% accuracy, zero API cost, fast processing
- Handles tables and structured layout from Form 1040 and schedules

**Tier 3 - Scanned PDF Extraction**
- Specialized OCR via Azure Document Intelligence (purpose-built US Tax model supporting 1040 and many schedules) or similar tax-specific API (Docsumo, Affinda)
- 95-99% accuracy with confidence scores per field

**Tier 4 - LLM Validation Layer**
- All extractions (digital and scanned) pass through LLM validation
- Validates field relationships (e.g., AGI = Total Income - Adjustments)
- Flags anomalies and corrects OCR errors using context
- Adds 1-3% accuracy improvement

**Tier 5 - Confidence-Based User Review**
- Items below 95% confidence flagged for manual user review
- Critical fields (income amounts, SSN) get extra scrutiny

**Future Options:**
- IRS Transcript Integration — users authorize transcript access (Form 8821) for 100% accurate e-filed return data
- Direct import from tax software APIs
- Manual entry with smart defaults

**Key Principle:** Build normalized internal schema that supports multiple ingestion methods

### Data Model Structure

```
User
  └─ TaxReturns (one per year)
       ├─ Filing metadata (year, filing_status, state)
       ├─ Income components (normalized structure)
       │    ├─ wages
       │    ├─ self_employment
       │    ├─ investment
       │    ├─ retirement
       │    └─ other
       ├─ Deductions (normalized structure)
       │    ├─ above_the_line (adjustments)
       │    ├─ standard_or_itemized
       │    └─ qbi_deduction
       ├─ Credits (normalized structure)
       │    ├─ non_refundable
       │    └─ refundable
       ├─ Tax calculation (computed fields)
       │    ├─ agi
       │    ├─ taxable_income
       │    ├─ total_tax
       │    ├─ effective_rate
       │    └─ marginal_bracket
       ├─ Payments & withholding
       ├─ Final amounts (refund/owed)
       └─ Raw source (PDF, parsed JSON backup)
```

### Visualization Technology

**Selected: Recharts** (free, MIT license, React-native)
- Declarative, composable React components
- Handles bar charts, line charts, area charts, pie charts, and waterfall visualizations
- Well-suited for YoY comparison dashboards
- SVG-based rendering (fine for tax data volumes)

### Key Technical Considerations

1. **Security & Privacy**
   - Tax data is highly sensitive PII
   - All data stored locally only — no server-side storage
   - Encryption at rest for local SQLite database
   - API calls (OCR, LLM) are ephemeral — no user data retained externally
   - Secure local file storage for uploaded PDFs

2. **Extraction Accuracy**
   - Tiered approach: direct text extraction for digital PDFs, specialized OCR for scans
   - LLM validation layer on all extractions to catch errors
   - Confidence scores per field; items below 95% flagged for user review
   - Target 99%+ overall accuracy

3. **Historical Data**
   - Support reasonable historical depth (suggest 7-10 years to start)
   - IRS typically keeps 7 years

4. **Computed Fields**
   - Many metrics are derived (effective tax rate, etc.)
   - Build calculation engine that can recompute from base data
   - Version calculations in case tax code interpretation changes

5. **State Variations**
   - State returns vary significantly
   - May need state-specific parsers
   - Consider starting with federal only, add states incrementally

## Open Questions for Product Manager

1. **Data source preference:** PDF upload only, or eventually enable filing through platform?
2. **Historical depth:** How many years back for "lifetime" calculations?
3. **Extraction accuracy trade-off:** How much LLM validation cost is acceptable per return? What confidence threshold for user review?
4. **V1 scope:** Build all 3 core views initially, or start with one?
5. **State returns:** Include in V1 or federal-only first?
6. **User authentication:** What level of security/auth needed?

## Next Steps for Development

### MVP
1. Set up Tauri v2 project (Rust backend + React/TypeScript frontend)
2. Design database schema for normalized tax return data
3. Build PDF upload, storage, and delete mechanism
4. Implement tiered extraction pipeline (PDF type detection, digital text extraction, OCR for scans)
5. Build LLM validation layer and confidence-based user review/clarification workflow
6. Display key numbers from each uploaded return
7. Year-by-year comparison chart for multiple returns
8. Implement widget architecture for extensible chart/visualization additions
9. Integrate chatbot for user questions about their data

### Post-MVP
10. Build Executive Summary Dashboard view
11. Build Income Breakdown view
12. Build Tax & Deductions Deep Dive view
13. Add filters, date selectors, and focus areas
14. Add remaining views and widgets iteratively

## Notes
- PM makes all product/UX decisions
- CTO advises on technical approach and builds application
- Focus is individual filers (Form 1040) only for now
