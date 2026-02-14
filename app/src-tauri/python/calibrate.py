#!/usr/bin/env python3
"""
Form 1040 Calibration Tool

Helps identify the correct bounding box coordinates for Form 1040 fields.
Use this tool to create or adjust field mappings for new form years.

Usage:
    python calibrate.py <pdf_path> [--page N] [--output debug.png]

Features:
    - Visualize text positions on the form
    - Interactive mode to test bounding boxes
    - Export debug images with coordinate overlays
"""

import argparse
import json
import sys

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed. Run: pip install pdfplumber")
    sys.exit(1)


def show_page_info(pdf_path: str, page_num: int = 0):
    """Display information about a PDF page."""
    with pdfplumber.open(pdf_path) as pdf:
        if page_num >= len(pdf.pages):
            print(f"Error: Page {page_num} does not exist. PDF has {len(pdf.pages)} pages.")
            return

        page = pdf.pages[page_num]

        print(f"\n=== Page {page_num} Info ===")
        print(f"Width: {page.width} points")
        print(f"Height: {page.height} points")
        print(f"Rotation: {page.rotation} degrees")

        # Show all text with positions
        print(f"\n=== Text Elements (first 50) ===")
        chars = page.chars[:50]
        for i, char in enumerate(chars):
            print(f"  {i}: '{char['text']}' at ({char['x0']:.1f}, {char['top']:.1f})")


def extract_with_bbox(pdf_path: str, page_num: int, bbox: tuple):
    """Extract text from a specific bounding box."""
    with pdfplumber.open(pdf_path) as pdf:
        if page_num >= len(pdf.pages):
            print(f"Error: Page {page_num} does not exist.")
            return

        page = pdf.pages[page_num]
        cropped = page.crop(bbox)
        text = cropped.extract_text()

        print(f"\n=== Extracted from bbox {bbox} on page {page_num} ===")
        print(f"Text: '{text}'")


def save_debug_image(pdf_path: str, page_num: int, output_path: str, show_chars: bool = True):
    """Save a debug image showing text positions."""
    with pdfplumber.open(pdf_path) as pdf:
        if page_num >= len(pdf.pages):
            print(f"Error: Page {page_num} does not exist.")
            return

        page = pdf.pages[page_num]
        im = page.to_image(resolution=150)

        if show_chars:
            # Draw rectangles around each character
            im.draw_rects(page.chars, stroke="red", stroke_width=1)

        im.save(output_path)
        print(f"Saved debug image to: {output_path}")


def interactive_mode(pdf_path: str):
    """Interactive mode for testing bounding boxes."""
    print("\n=== Interactive Calibration Mode ===")
    print("Commands:")
    print("  page N        - Switch to page N")
    print("  bbox X0 Y0 X1 Y1 - Extract text from bounding box")
    print("  save FILE     - Save debug image")
    print("  info          - Show page info")
    print("  quit          - Exit")
    print("")

    current_page = 0

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Opened PDF with {len(pdf.pages)} pages")

        while True:
            try:
                cmd = input(f"[page {current_page}] > ").strip()
            except EOFError:
                break

            if not cmd:
                continue

            parts = cmd.split()
            action = parts[0].lower()

            if action == "quit" or action == "q":
                break

            elif action == "page":
                if len(parts) < 2:
                    print("Usage: page N")
                    continue
                try:
                    page_num = int(parts[1])
                    if 0 <= page_num < len(pdf.pages):
                        current_page = page_num
                        print(f"Switched to page {current_page}")
                    else:
                        print(f"Invalid page. PDF has {len(pdf.pages)} pages (0-{len(pdf.pages)-1})")
                except ValueError:
                    print("Invalid page number")

            elif action == "bbox":
                if len(parts) < 5:
                    print("Usage: bbox X0 Y0 X1 Y1")
                    continue
                try:
                    bbox = tuple(float(x) for x in parts[1:5])
                    page = pdf.pages[current_page]
                    cropped = page.crop(bbox)
                    text = cropped.extract_text()
                    print(f"Extracted: '{text}'")
                except Exception as e:
                    print(f"Error: {e}")

            elif action == "save":
                filename = parts[1] if len(parts) > 1 else f"debug_page{current_page}.png"
                page = pdf.pages[current_page]
                im = page.to_image(resolution=150)
                im.draw_rects(page.chars, stroke="red", stroke_width=1)
                im.save(filename)
                print(f"Saved: {filename}")

            elif action == "info":
                page = pdf.pages[current_page]
                print(f"Page {current_page}: {page.width} x {page.height} points")

            else:
                print(f"Unknown command: {action}")


def main():
    parser = argparse.ArgumentParser(
        description="Calibration tool for Form 1040 field coordinates"
    )

    parser.add_argument(
        "pdf_path",
        help="Path to the PDF file"
    )

    parser.add_argument(
        "--page", "-p",
        type=int,
        default=0,
        help="Page number to analyze (0-indexed)"
    )

    parser.add_argument(
        "--output", "-o",
        help="Save debug image to this path"
    )

    parser.add_argument(
        "--bbox", "-b",
        nargs=4,
        type=float,
        metavar=("X0", "Y0", "X1", "Y1"),
        help="Extract text from bounding box"
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Enter interactive calibration mode"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Show page information"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode(args.pdf_path)
    elif args.bbox:
        extract_with_bbox(args.pdf_path, args.page, tuple(args.bbox))
    elif args.output:
        save_debug_image(args.pdf_path, args.page, args.output)
    elif args.info:
        show_page_info(args.pdf_path, args.page)
    else:
        # Default: show info and save debug image
        show_page_info(args.pdf_path, args.page)
        output = f"debug_page{args.page}.png"
        save_debug_image(args.pdf_path, args.page, output)


if __name__ == "__main__":
    main()
