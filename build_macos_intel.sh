#!/bin/bash
# Build script for Intel Mac

echo "Building Realisierungsdatenvisualizer for Intel Mac..."

# Clean previous builds
rm -rf build dist

# Install macOS requirements
echo "Installing macOS requirements..."
pip install -r requirements.txt
pip install -r requirements-macos.txt

# Build with py2app for Intel
echo "Building with py2app for Intel architecture..."
python setup_cross_platform.py macos-intel py2app

# Create DMG
if [ -d "dist/Realisierungsdatenvisualizer.app" ]; then
    echo "Creating DMG installer..."
    hdiutil create -volname "Realisierungsdatenvisualizer" \
        -srcfolder "dist/Realisierungsdatenvisualizer.app" \
        -ov -format UDZO "dist/Realisierungsdatenvisualizer-Intel.dmg"
    echo "DMG created: dist/Realisierungsdatenvisualizer-Intel.dmg"
else
    echo "Error: App not found in dist folder"
fi

echo "Build complete!"