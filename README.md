# Realisierungsdatenvisualizer

A cross-platform application for processing and visualizing fundraising realization data. Automatically calculates points based on donor demographics and generates individual HTML reports for each fundraiser.

## Download

**Get the latest version for your operating system:**

[![Download for Windows](https://img.shields.io/badge/Download-Windows-blue?style=for-the-badge&logo=windows)](../../releases/latest/download/Realisierungsdatenvisualizer-Windows.exe)
[![Download for macOS](https://img.shields.io/badge/Download-macOS-lightgrey?style=for-the-badge&logo=apple)](../../releases/latest/download/Realisierungsdatenvisualizer-macOS)
[![Download for Linux](https://img.shields.io/badge/Download-Linux-orange?style=for-the-badge&logo=linux)](../../releases/latest/download/Realisierungsdatenvisualizer-Linux)

Or visit the [Releases page](../../releases) to download specific versions.

## Features

### Core Functionality
- **CSV Processing**: Import and format fundraising data with automatic validation
- **Point Calculation**: Sophisticated scoring system based on donor age, donation interval, and amount
- **HTML Generation**: Individual reports for each fundraiser with weekly breakdowns
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
- **HTML Reports**: Individual files for each fundraiser with complete donor breakdowns
- **Weekly Summaries**: Point totals and bonus eligibility per calendar week

## Quick Start

### Option 1: Download Pre-Built Executable (Recommended)
1. Download the appropriate version for your operating system from the links above
2. **Windows**: Run `Realisierungsdatenvisualizer-Windows.exe`
3. **macOS**: Run `Realisierungsdatenvisualizer-macOS` (may need to right-click → Open first time)
4. **Linux**: Run `./Realisierungsdatenvisualizer-Linux`

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
   - Formatted CSV file will be saved in the same directory
   - HTML files will be generated in the `html_output/` folder

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

# Build app bundle
pyinstaller --onefile --windowed --name "Realisierungsdatenvisualizer" csv_formatter_gui.py
```

#### Linux
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3-tk

# Install Python dependencies
pip install -r requirements-linux.txt

# Build executable
pyinstaller --onefile --windowed --name "Realisierungsdatenvisualizer" csv_formatter_gui.py
```

## File Structure

```
CW/
├── csv_formatter_gui.py          # Main GUI application
├── csv_formatter.py              # Core processing logic
├── html_generator.py             # HTML report generation
├── realisierungsdaten.html       # HTML template
├── requirements.txt              # Base dependencies
├── requirements-windows.txt      # Windows-specific deps
├── requirements-macos.txt        # macOS-specific deps
├── requirements-linux.txt        # Linux-specific deps
├── build_windows.bat             # Windows build script
├── build_macos_intel.sh          # Intel Mac build script
├── build_macos_universal.sh      # Universal Mac build script
├── build_linux.sh               # Linux build script
└── .github/workflows/            # Automated build configuration
```

## System Requirements

### Windows
- Windows 10 or later
- 4GB RAM minimum
- 100MB free disk space

### macOS
- macOS 10.13 (High Sierra) or later
- Intel or Apple Silicon processor
- 4GB RAM minimum
- 100MB free disk space

### Linux
- Ubuntu 18.04+, CentOS 7+, Fedora 30+, or equivalent
- Python 3.8+ with tkinter support
- 4GB RAM minimum
- 100MB free disk space

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