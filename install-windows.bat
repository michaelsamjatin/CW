@echo off
REM Simple installer for Realisierungsdatenvisualizer on Windows
REM This script helps users set up the application quickly

echo ========================================
echo Realisierungsdatenvisualizer Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed on this system.
    echo.
    echo Please download and install Python 3.8 or higher from:
    echo https://python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

REM Show Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not available
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)

REM Install dependencies
echo Installing required packages...
echo This may take a few minutes...
echo.

python -m pip install --upgrade pip
pip install pandas>=1.5.0 numpy>=1.21.0 tkinterdnd2>=0.4.0

if errorlevel 1 (
    echo.
    echo Error: Failed to install some packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo To run the application:
echo   python csv_formatter_gui.py
echo.
echo Or double-click on csv_formatter_gui.py
echo.
pause