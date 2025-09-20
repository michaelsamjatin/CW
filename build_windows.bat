@echo off
REM Build script for Windows 10+

echo Building Realisierungsdatenvisualizer for Windows...

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Install Windows requirements
echo Installing Windows requirements...
pip install -r requirements.txt
pip install -r requirements-windows.txt

REM Build with cx_Freeze
echo Building with cx_Freeze...
python setup_cross_platform.py windows build

REM Alternative: Build with PyInstaller (comment out cx_Freeze above and uncomment below)
REM echo Building with PyInstaller...
REM pyinstaller --onefile --windowed --name "Realisierungsdatenvisualizer" --icon=logo.ico csv_formatter_gui.py

echo.
echo Build complete! Check the dist/ folder for the executable.
echo.
pause