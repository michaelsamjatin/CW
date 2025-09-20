#!/bin/bash

# Linux Build Script for Realisierungsdatenvisualizer
# Supports Ubuntu, Debian, CentOS, Fedora, and other major distributions

echo "Building Realisierungsdatenvisualizer for Linux..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "Error: Python 3.8 or higher is required"
    echo "Current version: $(python3 --version)"
    exit 1
fi

# Install system dependencies based on distribution
if command -v apt-get >/dev/null 2>&1; then
    # Debian/Ubuntu
    echo "Detected Debian/Ubuntu system"
    sudo apt-get update
    sudo apt-get install -y python3-tk python3-pip python3-dev build-essential
elif command -v yum >/dev/null 2>&1; then
    # CentOS/RHEL/Fedora (older)
    echo "Detected CentOS/RHEL system"
    sudo yum install -y tkinter python3-pip python3-devel gcc
elif command -v dnf >/dev/null 2>&1; then
    # Fedora (newer)
    echo "Detected Fedora system"
    sudo dnf install -y python3-tkinter python3-pip python3-devel gcc
elif command -v pacman >/dev/null 2>&1; then
    # Arch Linux
    echo "Detected Arch Linux system"
    sudo pacman -S --noconfirm tk python-pip base-devel
elif command -v zypper >/dev/null 2>&1; then
    # openSUSE
    echo "Detected openSUSE system"
    sudo zypper install -y python3-tk python3-pip python3-devel gcc
else
    echo "Warning: Could not detect package manager. Please install tkinter manually."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user -r requirements-linux.txt

# Check if all dependencies are available
echo "Checking dependencies..."
if ! python3 -c "import tkinter, pandas, numpy" 2>/dev/null; then
    echo "Error: Some dependencies are missing. Please install them manually."
    exit 1
fi

# Build executable with PyInstaller
echo "Building executable..."
python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name "Realisierungsdatenvisualizer" \
    --add-data "realisierungsdaten.html:." \
    --hidden-import=tkinterdnd2 \
    --hidden-import=pandas \
    --hidden-import=numpy \
    csv_formatter_gui.py

# Check if build was successful
if [ -f "dist/Realisierungsdatenvisualizer" ]; then
    echo ""
    echo "Build completed successfully!"
    echo "Executable location: dist/Realisierungsdatenvisualizer"
    echo ""
    echo "To run the application:"
    echo "  ./dist/Realisierungsdatenvisualizer"
    echo ""
    echo "To make it executable system-wide:"
    echo "  sudo cp dist/Realisierungsdatenvisualizer /usr/local/bin/"
else
    echo "Build failed. Check the output above for errors."
    exit 1
fi