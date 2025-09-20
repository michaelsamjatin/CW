# Simple Build Fix - No Architecture Targeting

## Problem
Your conda environment has ARM64 binaries, making it impossible to target x86_64 architecture.

## Solution: Basic Build (No Architecture Flags)
Let's build without any architecture targeting and see what we get:

```bash
# 1. Clean everything completely
rm -rf build dist *.spec

# 2. Activate conda environment  
source ~/miniconda3/etc/profile.d/conda.sh
conda activate analysis

# 3. Most basic build possible - no architecture targeting
pyinstaller --onefile --windowed \
  --name "Realisierungsdatenvisualizer" \
  --icon="logo.png" \
  csv_formatter_gui.py

# 4. Create DMG
hdiutil create -volname "Realisierungsdatenvisualizer" \
  -srcfolder "dist/Realisierungsdatenvisualizer.app" \
  -ov -format UDZO \
  "dist/Realisierungsdatenvisualizer.dmg"
```

## Alternative: Build Without tkinterdnd2
If the above still fails, try excluding the problematic dependency:

```bash
# Clean first
rm -rf build dist *.spec

# Build without tkinterdnd2 data files
pyinstaller --onefile --windowed \
  --name "Realisierungsdatenvisualizer" \
  --icon="logo.png" \
  --hidden-import=tkinterdnd2 \
  csv_formatter_gui.py
```

## What This Will Create
- **ARM64 app** (for Apple Silicon)
- **Won't work on Intel Macs** natively
- **BUT** - newer Intel Macs might run it through Rosetta 2

## For Intel Mac Compatibility
If you need true Intel compatibility, you would need to:

1. **Use an Intel Mac** to build the app, OR
2. **Create a new conda environment** with x86_64 Python:

```bash
# Create x86_64 conda environment (if you want to try this)
CONDA_SUBDIR=osx-64 conda create -n analysis_intel python=3.9
conda activate analysis_intel
conda config --env --set subdir osx-64
pip install pandas numpy tkinterdnd2 pyinstaller
```

## Recommended Approach
Try the simple build first - it may work on the 2019 MBP through Rosetta 2, which translates ARM64 apps to run on Intel.