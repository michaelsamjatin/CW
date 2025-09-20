@echo off
REM Build script for Windows 10+

echo Building Realisierungsdatenvisualizer for Windows...

REM Check if Python is installed and version
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Install Windows requirements
echo Installing Windows requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-windows.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if template file exists
if not exist "realisierungsdaten.html" (
    echo Warning: realisierungsdaten.html template not found
    echo HTML generation may not work properly
)

REM Build with PyInstaller
echo Building with PyInstaller...
pyinstaller --onefile --windowed ^
    --name "Realisierungsdatenvisualizer" ^
    --add-data "realisierungsdaten.html;." ^
    --hidden-import=tkinterdnd2 ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --distpath=dist ^
    --workpath=build ^
    csv_formatter_gui.py

if errorlevel 1 (
    echo Error: Build failed
    pause
    exit /b 1
)

if exist "dist\Realisierungsdatenvisualizer.exe" (
    echo.
    echo Build completed successfully!
    echo Executable location: dist\Realisierungsdatenvisualizer.exe
    echo File size:
    dir "dist\Realisierungsdatenvisualizer.exe" | find "Realisierungsdatenvisualizer.exe"
    echo.
    echo You can now distribute this file to other Windows computers.
    echo No additional installation required!
) else (
    echo Error: Executable was not created
    exit /b 1
)

echo.
pause