"""
Generate sample filled Form 1040 PDFs with fictitious data for testing.
Creates one PDF per user persona: casual filer, investor, self-employed.
Each PDF mimics the layout of a digitally-generated tax return (like TurboTax output).
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from pathlib import Path
import json

OUTPUT_DIR = Path(__file__).parent / "sample-returns" / "custom"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Also save the raw data as JSON for validation during testing
DATA_DIR = Path(__file__).parent / "sample-returns" / "custom"


def draw_1040_page1(c, data):
    """Draw page 1 of Form 1040 with filled data."""
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1.5 * inch, height - 0.5 * inch, "Form 1040")
    c.setFont("Helvetica", 8)
    c.drawString(1.5 * inch, height - 0.7 * inch, "Department of the Treasury — Internal Revenue Service")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(3.5 * inch, height - 0.5 * inch, f"U.S. Individual Income Tax Return  {data['tax_year']}")

    y = height - 1.0 * inch

    # Filing status
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.5 * inch, y, "Filing Status:")
    c.setFont("Helvetica", 9)
    c.drawString(1.5 * inch, y, data["filing_status"])
    y -= 0.25 * inch

    # Name and SSN
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.5 * inch, y, "Your first name and middle initial")
    c.drawString(4.0 * inch, y, "Last name")
    c.drawString(6.5 * inch, y, "Your SSN")
    y -= 0.2 * inch
    c.setFont("Helvetica", 10)
    c.drawString(0.5 * inch, y, data["first_name"])
    c.drawString(4.0 * inch, y, data["last_name"])
    c.drawString(6.5 * inch, y, data["ssn"])
    y -= 0.25 * inch

    if data.get("spouse_first_name"):
        c.setFont("Helvetica-Bold", 9)
        c.drawString(0.5 * inch, y, "Spouse's first name and middle initial")
        c.drawString(4.0 * inch, y, "Spouse's last name")
        c.drawString(6.5 * inch, y, "Spouse's SSN")
        y -= 0.2 * inch
        c.setFont("Helvetica", 10)
        c.drawString(0.5 * inch, y, data["spouse_first_name"])
        c.drawString(4.0 * inch, y, data["spouse_last_name"])
        c.drawString(6.5 * inch, y, data["spouse_ssn"])
        y -= 0.25 * inch

    # Address
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.5 * inch, y, "Home address")
    y -= 0.2 * inch
    c.setFont("Helvetica", 10)
    c.drawString(0.5 * inch, y, data["address"])
    y -= 0.2 * inch
    c.drawString(0.5 * inch, y, f"{data['city']}, {data['state']} {data['zip']}")
    y -= 0.4 * inch

    # Income section
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5 * inch, y, "Income")
    y -= 0.05 * inch
    c.line(0.5 * inch, y, 8.0 * inch, y)
    y -= 0.25 * inch

    income_lines = data["income_lines"]
    for line_num, label, amount in income_lines:
        c.setFont("Helvetica", 9)
        c.drawString(0.5 * inch, y, f"{line_num}")
        c.drawString(0.85 * inch, y, label)
        if amount is not None:
            c.drawRightString(7.8 * inch, y, f"{amount:,.0f}")
        y -= 0.2 * inch

    y -= 0.15 * inch

    # Adjustments / AGI
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5 * inch, y, "Adjusted Gross Income")
    y -= 0.05 * inch
    c.line(0.5 * inch, y, 8.0 * inch, y)
    y -= 0.25 * inch

    agi_lines = data["agi_lines"]
    for line_num, label, amount in agi_lines:
        c.setFont("Helvetica", 9)
        c.drawString(0.5 * inch, y, f"{line_num}")
        c.drawString(0.85 * inch, y, label)
        if amount is not None:
            c.drawRightString(7.8 * inch, y, f"{amount:,.0f}")
        y -= 0.2 * inch

    y -= 0.15 * inch

    # Deductions
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5 * inch, y, "Deductions")
    y -= 0.05 * inch
    c.line(0.5 * inch, y, 8.0 * inch, y)
    y -= 0.25 * inch

    deduction_lines = data["deduction_lines"]
    for line_num, label, amount in deduction_lines:
        c.setFont("Helvetica", 9)
        c.drawString(0.5 * inch, y, f"{line_num}")
        c.drawString(0.85 * inch, y, label)
        if amount is not None:
            c.drawRightString(7.8 * inch, y, f"{amount:,.0f}")
        y -= 0.2 * inch

    return y


def draw_1040_page2(c, data):
    """Draw page 2 of Form 1040 with tax computation, credits, payments."""
    width, height = letter
    y = height - 0.75 * inch

    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5 * inch, y, f"Form 1040 ({data['tax_year']}) — Page 2")
    c.setFont("Helvetica", 9)
    c.drawString(5.0 * inch, y, f"{data['last_name']}, {data['first_name']}")
    c.drawString(6.8 * inch, y, data["ssn"])
    y -= 0.35 * inch

    # Tax and Credits
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5 * inch, y, "Tax and Credits")
    y -= 0.05 * inch
    c.line(0.5 * inch, y, 8.0 * inch, y)
    y -= 0.25 * inch

    tax_lines = data["tax_lines"]
    for line_num, label, amount in tax_lines:
        c.setFont("Helvetica", 9)
        c.drawString(0.5 * inch, y, f"{line_num}")
        c.drawString(0.85 * inch, y, label)
        if amount is not None:
            c.drawRightString(7.8 * inch, y, f"{amount:,.0f}")
        y -= 0.2 * inch

    y -= 0.15 * inch

    # Payments
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5 * inch, y, "Payments")
    y -= 0.05 * inch
    c.line(0.5 * inch, y, 8.0 * inch, y)
    y -= 0.25 * inch

    payment_lines = data["payment_lines"]
    for line_num, label, amount in payment_lines:
        c.setFont("Helvetica", 9)
        c.drawString(0.5 * inch, y, f"{line_num}")
        c.drawString(0.85 * inch, y, label)
        if amount is not None:
            c.drawRightString(7.8 * inch, y, f"{amount:,.0f}")
        y -= 0.2 * inch

    y -= 0.15 * inch

    # Refund / Amount Owed
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5 * inch, y, "Refund or Amount You Owe")
    y -= 0.05 * inch
    c.line(0.5 * inch, y, 8.0 * inch, y)
    y -= 0.25 * inch

    refund_lines = data["refund_lines"]
    for line_num, label, amount in refund_lines:
        c.setFont("Helvetica", 9)
        c.drawString(0.5 * inch, y, f"{line_num}")
        c.drawString(0.85 * inch, y, label)
        if amount is not None:
            c.drawRightString(7.8 * inch, y, f"{amount:,.0f}")
        y -= 0.2 * inch


def generate_pdf(data, filename):
    """Generate a 2-page 1040 PDF."""
    filepath = OUTPUT_DIR / filename
    c = canvas.Canvas(str(filepath), pagesize=letter)

    draw_1040_page1(c, data)
    c.showPage()
    draw_1040_page2(c, data)
    c.showPage()
    c.save()

    # Save JSON sidecar with the expected values (for test validation)
    json_path = OUTPUT_DIR / filename.replace(".pdf", ".json")
    json_data = {
        "tax_year": data["tax_year"],
        "filing_status": data["filing_status"],
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "ssn": data["ssn"],
        "summary": data["summary"],
    }
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)

    print(f"  Generated: {filepath}")
    print(f"  Sidecar:   {json_path}")


# =============================================================================
# PERSONA 1: Casual Filer — W-2 employee, single, standard deduction
# =============================================================================
casual_filer = {
    "tax_year": "2024",
    "filing_status": "Single",
    "first_name": "John",
    "last_name": "Doe",
    "ssn": "000-00-0001",
    "spouse_first_name": None,
    "spouse_last_name": None,
    "spouse_ssn": None,
    "address": "123 Main Street, Apt 4B",
    "city": "Springfield",
    "state": "IL",
    "zip": "62701",
    "income_lines": [
        ("1a", "Wages, salaries, tips (W-2)", 72000),
        ("2b", "Taxable interest", 245),
        ("3b", "Ordinary dividends", 0),
        ("4a", "IRA distributions", None),
        ("4b", "Taxable IRA distributions", 0),
        ("7",  "Capital gain or (loss)", 0),
        ("8",  "Other income", 0),
        ("9",  "Total income", 72245),
    ],
    "agi_lines": [
        ("10", "Adjustments to income", 0),
        ("11", "Adjusted gross income", 72245),
    ],
    "deduction_lines": [
        ("12", "Standard deduction", 14600),
        ("13", "Qualified business income deduction", 0),
        ("14", "Total deductions", 14600),
        ("15", "Taxable income", 57645),
    ],
    "tax_lines": [
        ("16", "Tax", 8512),
        ("17", "Amount from Schedule 2, Part I, line 4", 0),
        ("18", "Add lines 16 and 17", 8512),
        ("19", "Child tax credit or credit for other dependents", 0),
        ("21", "Other credits from Schedule 3, line 8", 0),
        ("22", "Add lines 19 and 21", 0),
        ("24", "Total tax", 8512),
    ],
    "payment_lines": [
        ("25a", "Federal income tax withheld from W-2s", 9800),
        ("25d", "Total federal tax withheld", 9800),
        ("33", "Total payments", 9800),
    ],
    "refund_lines": [
        ("34", "Overpayment (refund)", 1288),
        ("35a", "Amount of line 34 you want refunded to you", 1288),
        ("37", "Amount you owe", 0),
    ],
    "summary": {
        "total_income": 72245,
        "agi": 72245,
        "taxable_income": 57645,
        "total_tax": 8512,
        "total_payments": 9800,
        "refund": 1288,
        "amount_owed": 0,
        "effective_tax_rate": 11.78,
        "deduction_type": "standard",
        "deduction_amount": 14600,
    }
}

# =============================================================================
# PERSONA 2: Investor — MFJ, itemized deductions, investment income
# =============================================================================
investor = {
    "tax_year": "2024",
    "filing_status": "Married Filing Jointly",
    "first_name": "Robert",
    "last_name": "Smith",
    "ssn": "000-00-0002",
    "spouse_first_name": "Sarah",
    "spouse_last_name": "Smith",
    "spouse_ssn": "000-00-0003",
    "address": "456 Oak Avenue",
    "city": "Naperville",
    "state": "IL",
    "zip": "60540",
    "income_lines": [
        ("1a", "Wages, salaries, tips (W-2)", 185000),
        ("2b", "Taxable interest", 3200),
        ("3a", "Qualified dividends", 8500),
        ("3b", "Ordinary dividends", 12400),
        ("4a", "IRA distributions", None),
        ("4b", "Taxable IRA distributions", 0),
        ("7",  "Capital gain or (loss). Attach Schedule D", 24500),
        ("8",  "Other income", 0),
        ("9",  "Total income", 225100),
    ],
    "agi_lines": [
        ("10", "Adjustments to income", 6000),
        ("11", "Adjusted gross income", 219100),
    ],
    "deduction_lines": [
        ("12", "Itemized deductions (Schedule A)", 38200),
        ("13", "Qualified business income deduction", 0),
        ("14", "Total deductions", 38200),
        ("15", "Taxable income", 180900),
    ],
    "tax_lines": [
        ("16", "Tax", 30856),
        ("17", "Amount from Schedule 2, Part I, line 4", 0),
        ("18", "Add lines 16 and 17", 30856),
        ("19", "Child tax credit or credit for other dependents", 4000),
        ("21", "Other credits from Schedule 3, line 8", 0),
        ("22", "Add lines 19 and 21", 4000),
        ("24", "Total tax", 26856),
    ],
    "payment_lines": [
        ("25a", "Federal income tax withheld from W-2s", 28000),
        ("26", "Estimated tax payments", 4000),
        ("25d", "Total federal tax withheld", 28000),
        ("33", "Total payments", 32000),
    ],
    "refund_lines": [
        ("34", "Overpayment (refund)", 5144),
        ("35a", "Amount of line 34 you want refunded to you", 5144),
        ("37", "Amount you owe", 0),
    ],
    "summary": {
        "total_income": 225100,
        "agi": 219100,
        "taxable_income": 180900,
        "total_tax": 26856,
        "total_payments": 32000,
        "refund": 5144,
        "amount_owed": 0,
        "effective_tax_rate": 12.26,
        "deduction_type": "itemized",
        "deduction_amount": 38200,
        "itemized_breakdown": {
            "state_local_taxes": 10000,
            "mortgage_interest": 14200,
            "charitable_contributions": 8500,
            "medical_dental": 5500,
        },
        "investment_income": {
            "taxable_interest": 3200,
            "qualified_dividends": 8500,
            "ordinary_dividends": 12400,
            "capital_gains": 24500,
        },
    }
}

# =============================================================================
# PERSONA 3: Self-Employed — Schedule C, business expenses
# =============================================================================
self_employed = {
    "tax_year": "2024",
    "filing_status": "Head of Household",
    "first_name": "Maria",
    "last_name": "Garcia",
    "ssn": "000-00-0004",
    "spouse_first_name": None,
    "spouse_last_name": None,
    "spouse_ssn": None,
    "address": "789 Pine Road",
    "city": "Austin",
    "state": "TX",
    "zip": "78701",
    "income_lines": [
        ("1a", "Wages, salaries, tips (W-2)", 0),
        ("2b", "Taxable interest", 890),
        ("3b", "Ordinary dividends", 0),
        ("7",  "Capital gain or (loss)", 0),
        ("8",  "Other income from Schedule 1 (business income)", 95400),
        ("9",  "Total income", 96290),
    ],
    "agi_lines": [
        ("10a", "Adjustments: 1/2 self-employment tax", 6736),
        ("10b", "Adjustments: self-employed health insurance", 8400),
        ("10c", "Adjustments: SEP-IRA contribution", 12000),
        ("10", "Total adjustments to income", 27136),
        ("11", "Adjusted gross income", 69154),
    ],
    "deduction_lines": [
        ("12", "Standard deduction", 21900),
        ("13", "Qualified business income deduction", 13544),
        ("14", "Total deductions", 35444),
        ("15", "Taxable income", 33710),
    ],
    "tax_lines": [
        ("16", "Tax", 3876),
        ("17", "Self-employment tax (Schedule SE)", 13472),
        ("18", "Add lines 16 and 17", 17348),
        ("19", "Child tax credit", 2000),
        ("21", "Earned income credit", 0),
        ("22", "Total credits", 2000),
        ("24", "Total tax", 15348),
    ],
    "payment_lines": [
        ("26", "Estimated tax payments (quarterly)", 14000),
        ("25d", "Total federal tax withheld", 0),
        ("33", "Total payments", 14000),
    ],
    "refund_lines": [
        ("34", "Overpayment (refund)", 0),
        ("37", "Amount you owe", 1348),
    ],
    "summary": {
        "total_income": 96290,
        "agi": 69154,
        "taxable_income": 33710,
        "total_tax": 15348,
        "total_payments": 14000,
        "refund": 0,
        "amount_owed": 1348,
        "effective_tax_rate": 22.19,
        "deduction_type": "standard",
        "deduction_amount": 21900,
        "qbi_deduction": 13544,
        "self_employment": {
            "gross_income": 142000,
            "business_expenses": 46600,
            "net_profit": 95400,
            "se_tax": 13472,
            "expense_breakdown": {
                "advertising": 3200,
                "car_expenses": 6800,
                "insurance": 4200,
                "office_expenses": 2400,
                "rent": 18000,
                "supplies": 3500,
                "utilities": 2800,
                "other": 5700,
            },
        },
    }
}


def main():
    print("Generating sample Form 1040 PDFs...\n")

    personas = [
        (casual_filer, "casual_filer_1040_2024.pdf"),
        (investor, "investor_1040_2024.pdf"),
        (self_employed, "self_employed_1040_2024.pdf"),
    ]

    for data, filename in personas:
        print(f"Persona: {data['first_name']} {data['last_name']} ({data['filing_status']})")
        generate_pdf(data, filename)
        print()

    print("Done! All sample returns generated.")


if __name__ == "__main__":
    main()
