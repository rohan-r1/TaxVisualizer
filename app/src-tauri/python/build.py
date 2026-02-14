#!/usr/bin/env python3
"""
Build script for creating the PDF extraction sidecar executable.

This script uses PyInstaller to bundle the extract.py script and its
dependencies into a standalone executable that Tauri can invoke.

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

    # Ensure binaries directory exists
    binaries_dir = os.path.join(script_dir, "..", "binaries")
    os.makedirs(binaries_dir, exist_ok=True)

    # Get absolute path for mappings
    mappings_path = os.path.join(script_dir, "mappings")

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
        # Hidden imports for pdfplumber dependencies
        "--hidden-import", "pdfplumber",
        "--hidden-import", "pdfminer",
        "--hidden-import", "pdfminer.pdfparser",
        "--hidden-import", "pdfminer.pdfdocument",
        "--hidden-import", "pdfminer.pdfpage",
        "--hidden-import", "pdfminer.pdfinterp",
        "--hidden-import", "pdfminer.converter",
        "--hidden-import", "pdfminer.layout",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        # Add mappings package (use absolute path)
        "--add-data", f"{mappings_path}{os.pathsep}mappings",
        # The main script
        os.path.join(script_dir, "extract.py"),
    ]

    print(f"\nRunning: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        # Determine output path
        ext = ".exe" if platform.system().lower() == "windows" else ""
        output_path = os.path.join(binaries_dir, f"{output_name}{ext}")
        abs_path = os.path.abspath(output_path)
        print(f"\n[OK] Build successful!")
        print(f"  Output: {abs_path}")
        return True
    else:
        print(f"\n[FAILED] Build failed with code {result.returncode}")
        return False


if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
