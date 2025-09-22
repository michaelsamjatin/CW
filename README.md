# Realisierungsdatenvisualizer

A cross-platform application for processing and visualizing fundraising realization data. Automatically calculates points based on donor demographics and generates individual PDF reports for each fundraiser.

## Download

**Get the latest version for your operating system:**

[![Download for Windows](https://img.shields.io/badge/Download-Windows-blue?style=for-the-badge&logo=windows)](../../releases/latest/download/Realisierungsdatenvisualizer-Setup.exe)

**macOS Downloads:**
[![Download for macOS Intel](https://img.shields.io/badge/Download-macOS%20Intel-lightgrey?style=for-the-badge&logo=apple)](../../releases/latest/download/Realisierungsdatenvisualizer-Intel.dmg)
[![Download for macOS Apple Silicon](https://img.shields.io/badge/Download-macOS%20Apple%20Silicon-black?style=for-the-badge&logo=apple)](../../releases/latest/download/Realisierungsdatenvisualizer-AppleSilicon.dmg)

Or visit the [Releases page](../../releases) to download specific versions.

## Features

### Core Functionality
- **CSV Processing**: Import and format fundraising data with automatic validation
- **Point Calculation**: Sophisticated scoring system based on donor age, donation interval, and amount
- **PDF Generation**: Professional individual reports for each fundraiser with weekly breakdowns
- **Cross-Platform**: Runs on Windows 10+, macOS 10.13+, and major Linux distributions

### Point Calculation Rules
- **Under 25**: 0.5 points regardless of amount or interval
- **25-29 years**: 0.5 points for monthly donations, 1 point for other intervals
- **30+ years**: Points calculated according to contribution table
- **Over 40 years**: Additional +1 bonus point
- **70% Rule**: Bonus only awarded if ≥70% of donors are successfully realized

### Point Calculation Table
| Annual Amount | Yearly | Semi-Annual | Monthly |
|---------------|--------|-------------|---------|
| 120€+         | 2      | 1.5         | 1       |
| 180€+         | 3      | 2.5         | 1.5     |
| 240€+         | 4      | 3           | 2       |
| 360€+         | 5      | 4           | 3       |

### Output Formats
- **Formatted CSV**: Sorted by calendar week and fundraiser with automatic subtotals
- **PDF Reports**: Professional individual files for each fundraiser with complete donor breakdowns
- **Weekly Summaries**: Point totals and bonus eligibility per calendar week

## Quick Start

### Option 1: Download Installer (Recommended)
1. Download the appropriate installer for your operating system from the links above
2. **Windows**: Run `Realisierungsdatenvisualizer-Setup.exe` and follow the installation wizard
3. **macOS**:
   - **Intel Macs**: Download and open `Realisierungsdatenvisualizer-Intel.dmg`
   - **Apple Silicon Macs (M1/M2/M3)**: Download and open `Realisierungsdatenvisualizer-AppleSilicon.dmg`
   - Drag the app to your Applications folder

### Option 2: Run from Source
```bash
# Clone the repository
git clone <repository_url>
cd CW

# Install dependencies
pip install -r requirements.txt

# Run the application
python csv_formatter_gui.py
```

## Usage

### Using the GUI
1. **Launch** the application
2. **Drag & Drop** your CSV file into the application window, or click to browse
3. **Wait** for processing to complete
4. **View Results**:
   - Formatted CSV file will be saved in the same directory as your input file
   - PDF files will be generated in a `pdf_output/` folder next to your input file

### Input File Format
Your CSV should contain these columns:
- `Fundraiser ID` - Unique identifier for each fundraiser
- `Fundraiser Name` - Name of the fundraiser
- `Calendar week` - Week designation (e.g., "18/2025", "KW19")
- `Public RefID` - Unique donor reference
- `Age` - Donor age in years
- `Interval` - Donation frequency (Monthly, Half-Yearly, Yearly)
- `Amount Yearly` - Annual donation amount in euros
- `status_agency` - Donor status (approved, cancelled, etc.)

## Building from Source

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Platform-Specific Instructions

#### Windows
```cmd
# Install dependencies
pip install -r requirements-windows.txt

# Build executable
pyinstaller --onefile --windowed --name "Realisierungsdatenvisualizer" csv_formatter_gui.py
```

#### macOS
```bash
# Install dependencies
pip install -r requirements-macos.txt

# Build app bundle and DMG
pyinstaller --windowed --name "Realisierungsdatenvisualizer" csv_formatter_gui.py
brew install create-dmg
create-dmg "Realisierungsdatenvisualizer.dmg" "dist/Realisierungsdatenvisualizer.app"
```

## File Structure

```
CW/
├── csv_formatter_gui.py          # Main GUI application
├── csv_formatter.py              # Core processing logic
├── pdf_generator.py              # PDF report generation
├── requirements.txt              # Base dependencies
├── requirements-windows.txt      # Windows-specific deps
├── requirements-macos.txt        # macOS-specific deps
├── installer.iss                 # Windows installer script
├── build_windows.bat             # Windows build script
├── build_macos_intel.sh          # Intel Mac build script
├── build_macos_universal.sh      # Universal Mac build script
└── .github/workflows/            # Automated build configuration
```

## System Requirements

### Windows
- Windows 10 or later
- 4GB RAM minimum
- 100MB free disk space

### macOS
- **Intel Macs**: macOS 10.13 (High Sierra) or later
- **Apple Silicon Macs**: macOS 11.0 (Big Sur) or later
- 4GB RAM minimum
- 100MB free disk space

**Note**: Download the correct version for your Mac architecture:
- Use Intel version for older Intel-based Macs
- Use Apple Silicon version for M1, M2, M3 Macs


## Troubleshooting

### Common Issues

**"File not found" errors**
- Ensure your CSV file follows the expected format
- Check that all required columns are present

**"Encoding errors"**
- The application automatically tries multiple encodings (UTF-8, CP1252, ISO-8859-1)
- If issues persist, try saving your CSV as UTF-8

**"Permission denied" (macOS/Linux)**
- Run `chmod +x filename` to make the executable runnable
- On macOS, right-click → Open for unsigned applications

**Missing dependencies**
- Install required system packages for your platform
- Ensure Python 3.8+ is installed

### Getting Help

1. Check the [Issues page](../../issues) for known problems
2. Create a new issue with:
   - Your operating system and version
   - Error message (if any)
   - Steps to reproduce the problem

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

### Version 1.0.0
- Initial release with cross-platform support
- Point calculation system implementation
- HTML report generation
- Automated build pipeline
- Windows, macOS, and Linux compatibility

---

**Built by Changing Waves** | [Website](https://changingwaves.org) | [Support](mailto:support@changingwaves.org)