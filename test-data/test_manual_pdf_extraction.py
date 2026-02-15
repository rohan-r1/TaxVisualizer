#!/usr/bin/env python3
"""
Test extraction accuracy against manually-filled IRS PDFs.
"""

import os
import sys
import json
from pathlib import Path

# Add the python directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "app" / "src-tauri" / "python"))

from extract import extract_form_1040


def test_schedule_1_extraction():
    """Test Schedule 1 field extraction against manual PDFs."""
    manual_dir = Path(__file__).parent / "manual-returns" / "alex_chen"
    generated_dir = Path(__file__).parent / "generated" / "alex_chen"

    # Expected values from MANUAL_ENTRY_REFERENCE.md
    expected = {
        "2018": {
            "sched1_student_loan_interest": "2500",
            "sched1_total_adjustments": "2500",
        },
        "2019": {
            "sched1_student_loan_interest": "2500",
            "sched1_total_adjustments": "2500",  # User corrected this
        },
        "2020": {
            "sched1_hsa_deduction": "3550",
            "sched1_student_loan_interest": "2500",
            "sched1_total_adjustments": "6050",
        },
        "2021": {
            "sched1_hsa_deduction": "3600",
            "sched1_student_loan_interest": "2500",
            "sched1_total_adjustments": "6100",
        },
        "2022": {
            "sched1_educator_expenses": "300",
            "sched1_hsa_deduction": "7300",
            "sched1_student_loan_interest": "2500",
            "sched1_total_adjustments": "10100",
        },
        "2023": {
            "sched1_educator_expenses": "300",
            "sched1_hsa_deduction": "7750",
            "sched1_ira_deduction": "6500",
            "sched1_total_adjustments": "14550",
        },
        "2024": {
            "sched1_educator_expenses": "300",
            "sched1_hsa_deduction": "8300",
            "sched1_ira_deduction": "7000",
            "sched1_total_adjustments": "15600",
        },
    }

    results = {}

    for year in ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]:
        pdf_file = manual_dir / f"f1040s1--{year}.pdf"
        if not pdf_file.exists():
            print(f"  {year}: PDF not found")
            continue

        # Extract fields
        extraction = extract_form_1040(str(pdf_file))
        fields_list = extraction.get("fields", [])
        # Convert list to dict for easier lookup
        extracted_fields = {f["key"]: f["value"] for f in fields_list if "key" in f}

        year_results = {"expected": expected[year], "extracted": {}, "matches": {}}

        for field_name, expected_value in expected[year].items():
            extracted_value = extracted_fields.get(field_name)
            matches = str(extracted_value) == expected_value if extracted_value else False
            year_results["extracted"][field_name] = extracted_value
            year_results["matches"][field_name] = matches

        results[year] = year_results

        # Print results
        all_match = all(year_results["matches"].values())
        status = "PASS" if all_match else "FAIL"
        print(f"  {year}: {status}")
        for field_name, expected_value in expected[year].items():
            extracted_value = year_results["extracted"][field_name]
            match = year_results["matches"][field_name]
            symbol = "[OK]" if match else "[X]"
            print(f"    {symbol} {field_name}: expected={expected_value}, extracted={extracted_value}")

    return results


def test_schedule_a_extraction():
    """Test Schedule A field extraction against manual PDFs."""
    manual_dir = Path(__file__).parent / "manual-returns" / "alex_chen"

    # Expected values
    expected = {
        "2022": {
            "scheda_salt_deduction": "10000",
            "scheda_mortgage_interest_1098": "12000",
            "scheda_charity_cash": "3000",
            "scheda_total_itemized": "25000",
        },
        "2023": {
            "scheda_salt_deduction": "10000",
            "scheda_mortgage_interest_1098": "11500",
            "scheda_charity_cash": "4000",
            "scheda_charity_noncash": "500",
            "scheda_total_itemized": "26000",
        },
        "2024": {
            "scheda_salt_deduction": "10000",
            "scheda_mortgage_interest_1098": "14000",
            "scheda_charity_cash": "5000",
            "scheda_charity_noncash": "1000",
            "scheda_total_itemized": "30000",
        },
    }

    results = {}

    for year in ["2022", "2023", "2024"]:
        pdf_file = manual_dir / f"f1040sa--{year}.pdf"
        if not pdf_file.exists():
            print(f"  {year}: PDF not found")
            continue

        # Extract fields
        extraction = extract_form_1040(str(pdf_file))
        fields_list = extraction.get("fields", [])
        # Convert list to dict for easier lookup
        extracted_fields = {f["key"]: f["value"] for f in fields_list if "key" in f}

        year_results = {"expected": expected[year], "extracted": {}, "matches": {}}

        for field_name, expected_value in expected[year].items():
            extracted_value = extracted_fields.get(field_name)
            matches = str(extracted_value) == expected_value if extracted_value else False
            year_results["extracted"][field_name] = extracted_value
            year_results["matches"][field_name] = matches

        results[year] = year_results

        # Print results
        all_match = all(year_results["matches"].values())
        status = "PASS" if all_match else "FAIL"
        print(f"  {year}: {status}")
        for field_name, expected_value in expected[year].items():
            extracted_value = year_results["extracted"][field_name]
            match = year_results["matches"][field_name]
            symbol = "[OK]" if match else "[X]"
            print(f"    {symbol} {field_name}: expected={expected_value}, extracted={extracted_value}")

    return results


def test_schedule_c_extraction():
    """Test Schedule C field extraction against manual PDFs."""
    manual_dir = Path(__file__).parent / "manual-returns" / "alex_chen"

    # Expected values
    expected = {
        "2019": {
            "schedc_gross_receipts": "8000",
            "schedc_total_expenses": "3000",
            "schedc_net_profit": "5000",
        },
    }

    results = {}

    for year in ["2019"]:
        pdf_file = manual_dir / f"f1040sc--{year}.pdf"
        if not pdf_file.exists():
            print(f"  {year}: PDF not found")
            continue

        # Extract fields
        extraction = extract_form_1040(str(pdf_file))
        fields_list = extraction.get("fields", [])
        # Convert list to dict for easier lookup
        extracted_fields = {f["key"]: f["value"] for f in fields_list if "key" in f}

        year_results = {"expected": expected[year], "extracted": {}, "matches": {}}

        for field_name, expected_value in expected[year].items():
            extracted_value = extracted_fields.get(field_name)
            matches = str(extracted_value) == expected_value if extracted_value else False
            year_results["extracted"][field_name] = extracted_value
            year_results["matches"][field_name] = matches

        results[year] = year_results

        # Print results
        all_match = all(year_results["matches"].values())
        status = "PASS" if all_match else "FAIL"
        print(f"  {year}: {status}")
        for field_name, expected_value in expected[year].items():
            extracted_value = year_results["extracted"][field_name]
            match = year_results["matches"][field_name]
            symbol = "[OK]" if match else "[X]"
            print(f"    {symbol} {field_name}: expected={expected_value}, extracted={extracted_value}")

    return results


if __name__ == "__main__":
    print("=" * 70)
    print("MANUAL PDF EXTRACTION TEST")
    print("=" * 70)

    print("\nSchedule 1 Extraction:")
    print("-" * 50)
    s1_results = test_schedule_1_extraction()

    print("\nSchedule A Extraction:")
    print("-" * 50)
    sa_results = test_schedule_a_extraction()

    print("\nSchedule C Extraction:")
    print("-" * 50)
    sc_results = test_schedule_c_extraction()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_fields = 0
    passing_fields = 0

    for results in [s1_results, sa_results, sc_results]:
        for year, data in results.items():
            for field, match in data.get("matches", {}).items():
                total_fields += 1
                if match:
                    passing_fields += 1

    print(f"Total fields tested: {total_fields}")
    print(f"Passing: {passing_fields}")
    print(f"Failing: {total_fields - passing_fields}")
    print(f"Accuracy: {passing_fields / total_fields * 100:.1f}%")
