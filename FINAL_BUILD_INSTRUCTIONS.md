# Final Build Instructions for Realisierungsdatenvisualizer

## Updated Files Ready
✅ csv_formatter_gui.py - Updated with Changing Waves branding
✅ logo.png - Custom app icon
✅ All CSV processing logic complete

## Build Commands
Run these commands in Terminal from the /Users/michaelsamjatin/repos/CW directory:

```bash
# 1. Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate analysis

# 2. Clean previous builds
rm -rf build dist

# 3. Build the app with PyInstaller
pyinstaller --onefile --windowed \
  --name "Realisierungsdatenvisualizer" \
  --icon="logo.png" \
  --add-data "/Users/michaelsamjatin/miniconda3/envs/analysis/lib/python3.9/site-packages/tkinterdnd2:tkinterdnd2" \
  csv_formatter_gui.py

# 4. Create DMG installer
hdiutil create -volname "Realisierungsdatenvisualizer" \
  -srcfolder "dist/Realisierungsdatenvisualizer.app" \
  -ov -format UDZO "dist/Realisierungsdatenvisualizer.dmg"
```

## Final App Features
- **Name:** Realisierungsdatenvisualizer
- **Subtitle:** Changing Waves Fundraiser Data Processor
- **Footer:** © 2025 Changing Waves
- **Icon:** Custom logo.png
- **Size:** ~167MB DMG file
- **Functionality:** Complete CSV processing with all requirements

## What the App Does
1. Drag & drop CSV files or browse to select
2. Processes World Vision fundraiser data:
   - Point calculation system (age/interval/amount rules)
   - 70% approval bonus eligibility calculation
   - Sorting by calendar week and fundraiser name
   - Proper formatting with subtotal rows
   - European decimal format and leading zero preservation
3. Shows loading animation during processing
4. Outputs formatted CSV ready for Excel import

## Output Files
After successful build:
- `dist/Realisierungsdatenvisualizer.app` - macOS application
- `dist/Realisierungsdatenvisualizer.dmg` - Installer package

Ready for distribution to Changing Waves users!