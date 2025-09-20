#!/bin/bash
# Build script for Universal Mac (Intel + Apple Silicon)

echo "Building Realisierungsdatenvisualizer for Universal Mac..."

# Clean previous builds
rm -rf build dist

# Install macOS requirements
echo "Installing macOS requirements..."
pip install -r requirements.txt
pip install -r requirements-macos.txt

# Build with py2app for Universal
echo "Building with py2app for Universal architecture (Intel + Apple Silicon)..."
python setup_cross_platform.py macos-universal py2app

# Create DMG
if [ -d "dist/Realisierungsdatenvisualizer.app" ]; then
    echo "Creating DMG installer..."
    hdiutil create -volname "Realisierungsdatenvisualizer" \
        -srcfolder "dist/Realisierungsdatenvisualizer.app" \
        -ov -format UDZO "dist/Realisierungsdatenvisualizer-Universal.dmg"
    echo "DMG created: dist/Realisierungsdatenvisualizer-Universal.dmg"
else
    echo "Error: App not found in dist folder"
fi

echo "Build complete!"