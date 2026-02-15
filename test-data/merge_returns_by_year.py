#!/usr/bin/env python3
"""
Merge individual tax form PDFs by year.

Creates combined PDFs with Form 1040 first, then schedules in order (1, A, C).
Preserves form field annotations from IRS fillable PDFs.
"""

import re
from pathlib import Path
from collections import defaultdict

from pypdf import PdfReader, PdfWriter


def merge_pdfs_by_year(input_dir: Path, output_dir: Path):
    """Merge PDFs grouped by year, preserving form field data and appearance."""

    # Group files by year
    files_by_year = defaultdict(list)

    for pdf_file in input_dir.glob("*.pdf"):
        # Extract year from filename (e.g., f1040--2024.pdf -> 2024)
        match = re.search(r'(\d{4})\.pdf$', pdf_file.name)
        if match:
            year = match.group(1)
            files_by_year[year].append(pdf_file)

    # Sort order: 1040 first, then schedules in order (1, A, C)
    def sort_key(path):
        name = path.name.lower()
        if 'f1040--' in name or name.startswith('f1040-'):
            return (0, name)  # Main 1040 first
        elif 's1--' in name or 's1-' in name:
            return (1, name)  # Schedule 1
        elif 'sa--' in name or 'sa-' in name:
            return (2, name)  # Schedule A
        elif 'sc--' in name or 'sc-' in name:
            return (3, name)  # Schedule C
        else:
            return (9, name)  # Other

    output_dir.mkdir(parents=True, exist_ok=True)

    for year, files in sorted(files_by_year.items()):
        sorted_files = sorted(files, key=sort_key)

        print(f"\n{year}:")
        for f in sorted_files:
            print(f"  - {f.name}")

        # Simple merge with pypdf - append preserves form fields
        writer = PdfWriter()

        for pdf_file in sorted_files:
            reader = PdfReader(str(pdf_file))
            writer.append(reader)

        output_path = output_dir / f"alex_chen_{year}_combined.pdf"
        with open(output_path, "wb") as f:
            writer.write(f)

        print(f"  -> Created: {output_path.name} ({len(writer.pages)} pages)")


if __name__ == "__main__":
    input_dir = Path(__file__).parent / "manual-returns" / "alex_chen"
    output_dir = Path(__file__).parent / "manual-returns" / "alex_chen" / "combined"

    print("Merging PDFs by year...")
    merge_pdfs_by_year(input_dir, output_dir)
    print("\nDone!")
