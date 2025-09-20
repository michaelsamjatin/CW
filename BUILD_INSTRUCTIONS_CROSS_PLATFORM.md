# Cross-Platform Build Instructions for Realisierungsdatenvisualizer

This application now supports **Windows 10+**, **Intel Mac**, and **Apple Silicon Mac**.

## Prerequisites

### All Platforms
- Python 3.8 or higher
- pip package manager

### Windows 10+
- Visual Studio Build Tools (for building native extensions)
- Windows 10 or later

### macOS (Intel/Apple Silicon)
- Xcode Command Line Tools
- macOS 10.13+ (Intel) or macOS 10.15+ (Universal)

## Quick Start

### 1. Clone and Setup
```bash
git clone <repository>
cd CW
pip install -r requirements.txt
```

### 2. Platform-Specific Build

#### Windows 10+
```batch
# Install Windows-specific requirements
pip install -r requirements-windows.txt

# Build executable
build_windows.bat
```

#### Intel Mac
```bash
# Install macOS-specific requirements
pip install -r requirements-macos.txt

# Build Intel app
chmod +x build_macos_intel.sh
./build_macos_intel.sh
```

#### Universal Mac (Intel + Apple Silicon)
```bash
# Install macOS-specific requirements
pip install -r requirements-macos.txt

# Build Universal app
chmod +x build_macos_universal.sh
./build_macos_universal.sh
```

## Manual Build Options

### Using Cross-Platform Setup Script

The `setup_cross_platform.py` script automatically detects your platform:

```bash
# Automatic detection
python setup_cross_platform.py auto

# Manual platform selection
python setup_cross_platform.py windows
python setup_cross_platform.py macos-intel
python setup_cross_platform.py macos-universal
```

### Alternative Build Methods

#### Windows - PyInstaller
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Realisierungsdatenvisualizer" csv_formatter_gui.py
```

#### Windows - cx_Freeze
```bash
pip install cx-freeze
python setup_cross_platform.py windows build
```

#### macOS - PyInstaller
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Realisierungsdatenvisualizer" csv_formatter_gui.py
```

## Platform-Specific Features

### Windows 10+
- **Taskbar Integration**: Custom app ID for Windows taskbar
- **Font Scaling**: Automatic DPI scaling support
- **File Encoding**: Multiple encoding fallbacks (UTF-8, CP1252, ISO-8859-1)
- **Drag & Drop**: Graceful fallback if tkinterdnd2 unavailable

### Intel Mac
- **Architecture**: x86_64 only for maximum compatibility
- **System Requirements**: macOS 10.13+ (High Sierra)
- **DMG Creation**: Automatic installer creation
- **Window Centering**: Native macOS window positioning

### Universal Mac
- **Architecture**: Universal binary (x86_64 + arm64)
- **System Requirements**: macOS 10.15+ (Catalina)
- **Compatibility**: Runs natively on both Intel and Apple Silicon
- **Optimized Performance**: Native performance on both architectures

## Output Files

### Windows
- `dist/Realisierungsdatenvisualizer.exe` - Standalone executable
- Compatible with Windows 10, 11

### Intel Mac
- `dist/Realisierungsdatenvisualizer.app` - macOS application bundle
- `dist/Realisierungsdatenvisualizer-Intel.dmg` - Installer package

### Universal Mac
- `dist/Realisierungsdatenvisualizer.app` - Universal macOS application
- `dist/Realisierungsdatenvisualizer-Universal.dmg` - Universal installer

## Troubleshooting

### Windows Issues
- **Missing DLLs**: Install Visual Studio Build Tools
- **Encoding Errors**: Application automatically tries multiple encodings
- **Drag & Drop**: Falls back to browse-only if tkinterdnd2 fails

### macOS Issues
- **Permission Denied**: Run `chmod +x build_macos_*.sh`
- **Code Signing**: For distribution, sign with Apple Developer certificate
- **Gatekeeper**: Users may need to right-click → Open for unsigned apps

### General Issues
- **Import Errors**: Ensure all requirements are installed
- **Build Failures**: Check Python version (3.8+ required)
- **Memory Issues**: Close other applications during build

## Dependencies

### Core Dependencies (All Platforms)
- pandas >= 1.5.0
- numpy >= 1.21.0
- tkinterdnd2 >= 0.4.0 (optional for drag & drop)

### Windows-Specific
- cx-Freeze >= 6.14.0
- pywin32 >= 306

### macOS-Specific
- py2app >= 0.28.0

## File Structure
```
CW/
├── csv_formatter_gui.py         # Main application
├── csv_formatter.py             # Core processing logic
├── setup_cross_platform.py     # Cross-platform setup script
├── requirements.txt             # Base requirements
├── requirements-windows.txt     # Windows-specific requirements
├── requirements-macos.txt       # macOS-specific requirements
├── build_windows.bat            # Windows build script
├── build_macos_intel.sh         # Intel Mac build script
├── build_macos_universal.sh     # Universal Mac build script
└── dist/                        # Output directory
```

## Application Features

- **Cross-Platform GUI**: Works on Windows 10+ and macOS
- **Drag & Drop Support**: With graceful fallback
- **Multiple File Encodings**: Automatic encoding detection
- **Progress Indication**: Real-time processing feedback
- **Error Handling**: Comprehensive error reporting
- **Platform-Specific UI**: Optimized for each operating system

## Distribution

### Windows
Distribute `Realisierungsdatenvisualizer.exe` - no additional files needed.

### macOS
Distribute the `.dmg` file. Users drag the app to Applications folder.

## Version History

- **v1.0.0**: Initial cross-platform release
  - Windows 10+ support
  - Intel Mac support  
  - Universal Mac support
  - Enhanced error handling
  - Platform-specific optimizations

---

For support or questions, contact the Changing Waves development team.