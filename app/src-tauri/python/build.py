#!/usr/bin/env python3
"""
Build script for creating the PDF extraction sidecar executable.

This script uses PyInstaller to bundle the extract.py script and its
dependencies into a standalone executable that Tauri can invoke.

Uses PaddleOCR for text extraction, which adds ~300MB to the bundle size
but provides reliable OCR that works with both digital and scanned PDFs.

Usage:
    python build.py

Output:
    dist/extract-{target_triple}.exe (Windows)
    dist/extract-{target_triple} (macOS/Linux)
"""

import os
import platform
import shutil
import subprocess
import sys


def get_target_triple() -> str:
    """Get the Rust-style target triple for the current platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        if machine in ("amd64", "x86_64"):
            return "x86_64-pc-windows-msvc"
        elif machine in ("arm64", "aarch64"):
            return "aarch64-pc-windows-msvc"
    elif system == "darwin":
        if machine in ("x86_64",):
            return "x86_64-apple-darwin"
        elif machine in ("arm64", "aarch64"):
            return "aarch64-apple-darwin"
    elif system == "linux":
        if machine in ("x86_64",):
            return "x86_64-unknown-linux-gnu"
        elif machine in ("arm64", "aarch64"):
            return "aarch64-unknown-linux-gnu"

    raise RuntimeError(f"Unsupported platform: {system} {machine}")


def build():
    """Build the sidecar executable using PyInstaller."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    target_triple = get_target_triple()
    output_name = f"extract-{target_triple}"

    print(f"Building sidecar for: {target_triple}")
    print(f"Output name: {output_name}")
    print(f"\nNote: This build includes PaddleOCR which adds ~300MB to the bundle.")
    print(f"The build may take several minutes.\n")

    # Ensure binaries directory exists
    binaries_dir = os.path.join(script_dir, "..", "binaries")
    os.makedirs(binaries_dir, exist_ok=True)

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single executable
        "--clean",                      # Clean build
        "--noconfirm",                  # Don't ask for confirmation
        "--name", output_name,          # Output name with target triple
        "--distpath", binaries_dir,     # Output to src-tauri/binaries/
        "--workpath", os.path.join(script_dir, "build"),  # Build directory
        "--specpath", os.path.join(script_dir, "build"),  # Spec file location
        # PaddleOCR dependencies
        "--hidden-import", "paddleocr",
        "--hidden-import", "paddle",
        "--hidden-import", "paddle.fluid",
        "--hidden-import", "paddleocr.paddleocr",
        "--hidden-import", "paddleocr.tools",
        "--hidden-import", "paddleocr.tools.infer",
        # PyMuPDF for PDF rendering
        "--hidden-import", "fitz",
        "--hidden-import", "pymupdf",
        # Image processing
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "cv2",
        "--hidden-import", "numpy",
        # PaddleOCR dependencies
        "--hidden-import", "pyclipper",
        "--hidden-import", "shapely",
        "--hidden-import", "skimage",
        "--hidden-import", "imgaug",
        "--hidden-import", "lmdb",
        "--hidden-import", "rapidfuzz",
        "--hidden-import", "imghdr",
        "--hidden-import", "Polygon",
        "--hidden-import", "lanms",
        # Collect all PaddleOCR data files
        "--collect-all", "paddleocr",
        "--collect-all", "paddle",
        "--collect-all", "Cython",
        "--collect-all", "imageio",
        "--collect-all", "imgaug",
        "--copy-metadata", "imageio",
        "--copy-metadata", "imgaug",
        # The main script
        os.path.join(script_dir, "extract.py"),
    ]

    print(f"Running: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        # Determine output path
        ext = ".exe" if platform.system().lower() == "windows" else ""
        output_path = os.path.join(binaries_dir, f"{output_name}{ext}")
        abs_path = os.path.abspath(output_path)

        # Get file size
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"\n[OK] Build successful!")
            print(f"  Output: {abs_path}")
            print(f"  Size: {size_mb:.1f} MB")
        else:
            print(f"\n[OK] Build completed but output file not found at expected path")
            print(f"  Expected: {abs_path}")
        return True
    else:
        print(f"\n[FAILED] Build failed with code {result.returncode}")
        return False


if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
