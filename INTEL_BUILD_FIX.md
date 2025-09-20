# Intel Build Fix for Compatibility Error

## Problem
The universal build (`--target-arch=universal2`) failed because your conda environment contains architecture-specific binaries that aren't "fat binaries" (universal binaries).

## Solution: Intel-Specific Build
Use the Intel-specific build which will be compatible with 2019 MacBook Pro:

```bash
# 1. Clean everything first
rm -rf build dist *.spec

# 2. Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate analysis

# 3. Build specifically for Intel x86_64 (no universal2 flag)
pyinstaller --onefile --windowed \
  --name "Realisierungsdatenvisualizer" \
  --icon="logo.png" \
  --target-arch=x86_64 \
  --osx-bundle-identifier="com.changingwaves.realisierungsdatenvisualizer" \
  --add-data "/Users/michaelsamjatin/miniconda3/envs/analysis/lib/python3.9/site-packages/tkinterdnd2:tkinterdnd2" \
  csv_formatter_gui.py

# 4. If step 3 still fails, try without target-arch flag
pyinstaller --onefile --windowed \
  --name "Realisierungsdatenvisualizer" \
  --icon="logo.png" \
  --osx-bundle-identifier="com.changingwaves.realisierungsdatenvisualizer" \
  --add-data "/Users/michaelsamjatin/miniconda3/envs/analysis/lib/python3.9/site-packages/tkinterdnd2:tkinterdnd2" \
  csv_formatter_gui.py

# 5. Create DMG
hdiutil create -volname "Realisierungsdatenvisualizer_Intel" \
  -srcfolder "dist/Realisierungsdatenvisualizer.app" \
  -ov -format UDZO \
  "dist/Realisierungsdatenvisualizer_Intel.dmg"
```

## Alternative: Simplest Build
If the above still causes issues, try the most basic build:

```bash
# Clean first
rm -rf build dist *.spec

# Basic build without architecture specifications
pyinstaller --onefile --windowed \
  --name "Realisierungsdatenvisualizer" \
  --icon="logo.png" \
  csv_formatter_gui.py

# Then create DMG
hdiutil create -volname "Realisierungsdatenvisualizer" \
  -srcfolder "dist/Realisierungsdatenvisualizer.app" \
  -ov -format UDZO \
  "dist/Realisierungsdatenvisualizer.dmg"
```

## Why This Happens
- Your conda environment was installed on Apple Silicon
- Contains ARM64-specific Python extensions
- PyInstaller can't convert these to universal binaries
- Intel-specific build avoids this issue

## Expected Result
- App will work on Intel Macs (like 2019 MBP)
- May not work on Apple Silicon Macs
- If you need both, you'd need separate builds from Intel and ARM machines

Run the Intel-specific build commands above - this should resolve the compatibility error.