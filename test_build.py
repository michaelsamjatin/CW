#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the application can be imported and basic functionality works.
This is used in CI/CD to test before building executables.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Windows-compatible output symbols
if sys.platform == 'win32':
    CHECK = "[OK]"
    CROSS = "[FAIL]"
    WARN = "[WARN]"
else:
    CHECK = "✓"
    CROSS = "✗"
    WARN = "⚠"

def test_imports():
    """Test that all required modules can be imported."""
    try:
        import pandas
        import numpy
        print(f"{CHECK} pandas {pandas.__version__}")
        print(f"{CHECK} numpy {numpy.__version__}")
    except ImportError as e:
        print(f"{CROSS} Failed to import basic dependencies: {e}")
        return False

    try:
        import tkinter
        print(f"{CHECK} tkinter available")
    except ImportError as e:
        print(f"{CROSS} tkinter not available: {e}")
        return False

    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
        print(f"{CHECK} tkinterdnd2 available")
    except ImportError:
        print(f"{WARN} tkinterdnd2 not available (drag & drop will be disabled)")

    return True

def test_csv_processing():
    """Test that CSV processing logic works."""
    try:
        # Import our modules
        from csv_formatter import calculate_points, calculate_bonus_eligibility
        from html_generator import generate_html_for_fundraiser

        # Test point calculation
        points = calculate_points(25, "Monthly", 360)
        assert points == 0.5, f"Expected 0.5 points, got {points}"

        points = calculate_points(35, "Monthly", 360)
        assert points == 3.0, f"Expected 3.0 points, got {points}"

        points = calculate_points(45, "Monthly", 360)
        assert points == 4.0, f"Expected 4.0 points, got {points}"

        print(f"{CHECK} Point calculation working")
        return True

    except ImportError as e:
        print(f"{CROSS} Failed to import processing modules: {e}")
        return False
    except AssertionError as e:
        print(f"{CROSS} Point calculation test failed: {e}")
        return False
    except Exception as e:
        print(f"{CROSS} Unexpected error in CSV processing test: {e}")
        return False

def test_file_exists():
    """Test that required files exist."""
    required_files = [
        'csv_formatter.py',
        'csv_formatter_gui.py',
        'html_generator.py',
        'realisierungsdaten.html'
    ]

    for file in required_files:
        if os.path.exists(file):
            print(f"{CHECK} {file} exists")
        else:
            print(f"{CROSS} {file} missing")
            return False

    return True

def main():
    """Run all tests."""
    print("Testing build requirements...")
    print("=" * 40)

    tests = [
        ("File existence", test_file_exists),
        ("Module imports", test_imports),
        ("CSV processing", test_csv_processing),
    ]

    all_passed = True
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if not test_func():
            all_passed = False

    print("\n" + "=" * 40)
    if all_passed:
        print(f"{CHECK} All tests passed! Ready to build.")
        sys.exit(0)
    else:
        print(f"{CROSS} Some tests failed. Build may fail.")
        sys.exit(1)

if __name__ == "__main__":
    main()