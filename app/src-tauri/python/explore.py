#!/usr/bin/env python3
"""Quick script to explore PDF layout for calibration."""

import pdfplumber
import sys

pdf_path = sys.argv[1] if len(sys.argv) > 1 else "/c/Users/rohan/Documents/TaxVisualizer/test-data/sample-returns/1040_2018_sample.pdf"

pdf = pdfplumber.open(pdf_path)

# Mode: --bbox to test bounding boxes
if len(sys.argv) > 2 and sys.argv[2] == "--bbox":
    page_num = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    page = pdf.pages[page_num]

    # Test regions based on findings - using tight 13pt height boxes
    # Values are at x=549-593 on page 1
    test_regions = [
        ("30,262 area", (545, 128, 598, 141)),
        ("44,682 area", (400, 188, 455, 201)),
        ("74,944 area (first)", (545, 188, 598, 201)),
        ("74,944 area (second)", (545, 212, 598, 225)),
        ("20,398 area", (545, 224, 598, 237)),
        ("8,532 area", (545, 236, 598, 249)),
        ("46,014 area", (545, 248, 598, 261)),
        ("8,635 area", (545, 284, 598, 297)),
        ("2,000 area", (545, 296, 598, 309)),
        ("6,635 area (first)", (545, 308, 598, 321)),
        ("6,635 area (second)", (545, 332, 598, 345)),
        ("4,972 area (first)", (545, 344, 598, 357)),
        ("4,972 area (second)", (545, 392, 598, 405)),
    ]

    print(f"Testing bounding boxes on page {page_num}:")
    for name, bbox in test_regions:
        try:
            cropped = page.crop(bbox)
            text = cropped.extract_text() or ""
            print(f"  {name}: \"{text.strip()}\"")
        except Exception as e:
            print(f"  {name}: ERROR - {e}")
else:
    # Default: show money values
    for i, page in enumerate(pdf.pages):
        print(f"\n{'='*60}")
        print(f"PAGE {i}: {page.width} x {page.height}")
        print("="*60)

        words = page.extract_words()
        money_words = []
        for w in words:
            text = w["text"]
            if any(c.isdigit() for c in text) and len(text) >= 3:
                if "," in text or text.replace("-", "").replace(".", "").isdigit():
                    money_words.append(w)

        print(f"\nFound {len(money_words)} potential money values:")
        for w in money_words[:30]:
            print(f"  '{w['text']}' at x={w['x0']:.0f}-{w['x1']:.0f}, y={w['top']:.0f}-{w['bottom']:.0f}")

pdf.close()
