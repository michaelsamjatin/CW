# Compatible Build Instructions for Realisierungsdatenvisualizer
## Fixing Intel Mac Compatibility Issues

The compatibility issue is likely due to:
1. Building on Apple Silicon (M1/M2) for Intel Mac
2. macOS version targeting mismatch
3. Python architecture differences

## Solution: Create Compatible Build

### Option 1: Universal Build (Recommended)
Run these commands to create a build that works on both Intel and Apple Silicon:

```bash
# 1. Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate analysis

# 2. Clean previous builds
rm -rf build dist

# 3. Build with universal compatibility settings
pyinstaller --onefile --windowed \
  --name "Realisierungsdatenvisualizer" \
  --icon="logo.png" \
  --target-arch=universal2 \
  --osx-bundle-identifier="com.changingwaves.realisierungsdatenvisualizer" \
  --add-data "/Users/michaelsamjatin/miniconda3/envs/analysis/lib/python3.9/site-packages/tkinterdnd2:tkinterdnd2" \
  csv_formatter_gui.py

# 4. Create DMG with better compatibility
hdiutil create -volname "Realisierungsdatenvisualizer" \
  -srcfolder "dist/Realisierungsdatenvisualizer.app" \
  -ov -format UDZO \
  -imagekey zlib-level=9 \
  "dist/Realisierungsdatenvisualizer_Universal.dmg"
```

### Option 2: Intel-Specific Build
If Option 1 doesn't work, try building specifically for Intel:

```bash
# 1. Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate analysis

# 2. Clean previous builds
rm -rf build dist

# 3. Build for Intel x86_64 architecture
pyinstaller --onefile --windowed \
  --name "Realisierungsdatenvisualizer" \
  --icon="logo.png" \
  --target-arch=x86_64 \
  --osx-bundle-identifier="com.changingwaves.realisierungsdatenvisualizer" \
  --add-data "/Users/michaelsamjatin/miniconda3/envs/analysis/lib/python3.9/site-packages/tkinterdnd2:tkinterdnd2" \
  csv_formatter_gui.py

# 4. Create DMG
hdiutil create -volname "Realisierungsdatenvisualizer_Intel" \
  -srcfolder "dist/Realisierungsdatenvisualizer.app" \
  -ov -format UDZO \
  "dist/Realisierungsdatenvisualizer_Intel.dmg"
```

### Option 3: Lowered macOS Requirement
If the issue is macOS version compatibility:

```bash
# Set deployment target for older macOS versions
export MACOSX_DEPLOYMENT_TARGET=10.14

# Then run the build command from Option 1 or 2
```

## Troubleshooting Steps

### 1. Check Current Architecture
```bash
# Check what architecture you're building on
uname -m
# arm64 = Apple Silicon (M1/M2)
# x86_64 = Intel
```

### 2. Verify PyInstaller Options
```bash
# Check available PyInstaller options
pyinstaller --help | grep -A 5 -B 5 "target-arch"
```

### 3. Alternative: Build on Intel Mac
If you have access to an Intel Mac, building there will ensure compatibility.

## Expected Results

**Universal Build:** Works on both Intel and Apple Silicon Macs
**Intel Build:** Works specifically on Intel Macs (2019 MBP included)
**File Size:** May be larger due to including multiple architectures

## Testing
Before distribution, test on:
- [x] Apple Silicon Mac (M1/M2) 
- [ ] Intel Mac (2019 MBP and similar)
- [ ] Different macOS versions (10.14+)

The Intel-specific or Universal build should resolve the compatibility issue with the 2019 MacBook Pro.