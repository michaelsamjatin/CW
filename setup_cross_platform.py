import platform
import sys
import os
from pathlib import Path

def get_platform_info():
    """Get platform and architecture information."""
    system = platform.system()
    machine = platform.machine()
    
    print(f"System: {system}")
    print(f"Machine: {machine}")
    print(f"Python: {sys.version}")
    
    return system, machine

def setup_windows():
    """Setup for Windows 10+ compatibility."""
    from cx_Freeze import setup, Executable
    
    # Dependencies for Windows
    build_exe_options = {
        "packages": [
            "tkinter", "tkinter.ttk", "tkinter.messagebox", "tkinter.filedialog",
            "pandas", "numpy", "tkinterdnd2", "collections", "datetime", "threading", "os"
        ],
        "excludes": [
            "matplotlib", "scipy", "IPython", "jupyter", "sympy", "test", "unittest"
        ],
        "include_files": [],
        "optimize": 2,
        "zip_include_packages": ["*"],
        "zip_exclude_packages": []
    }
    
    # Executable configuration
    exe = Executable(
        "csv_formatter_gui.py",
        base="Win32GUI",  # Use Win32GUI for windowed app
        target_name="Realisierungsdatenvisualizer.exe",
        icon=None  # Add icon path if available
    )
    
    setup(
        name="Realisierungsdatenvisualizer",
        version="1.0.0",
        description="CSV Formatter for World Vision Deutschland",
        options={"build_exe": build_exe_options},
        executables=[exe]
    )

def setup_macos_intel():
    """Setup for Intel Mac compatibility using py2app."""
    from setuptools import setup
    import py2app
    
    APP = ['csv_formatter_gui.py']
    DATA_FILES = []
    OPTIONS = {
        'argv_emulation': True,
        'arch': 'x86_64',  # Force Intel architecture
        'plist': {
            'CFBundleName': 'Realisierungsdatenvisualizer',
            'CFBundleDisplayName': 'CSV Formatter - Changing Waves',
            'CFBundleGetInfoString': 'CSV Formatter for Changing Waves',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHumanReadableCopyright': '© 2025 Changing Waves',
            'LSMinimumSystemVersion': '10.13',  # Support older macOS versions
        },
        'includes': [
            'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog',
            'pandas', 'numpy', 'tkinterdnd2', 'collections', 'datetime', 'threading', 'os'
        ],
        'excludes': ['matplotlib', 'scipy', 'IPython', 'jupyter', 'sympy'],
        'resources': [],
        'strip': False,
        'optimize': 2,
    }
    
    setup(
        name='Realisierungsdatenvisualizer',
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )

def setup_macos_universal():
    """Setup for Universal Mac (Intel + Apple Silicon) using py2app."""
    from setuptools import setup
    import py2app
    
    APP = ['csv_formatter_gui.py']
    DATA_FILES = []
    OPTIONS = {
        'argv_emulation': True,
        'arch': 'universal2',  # Universal binary
        'plist': {
            'CFBundleName': 'Realisierungsdatenvisualizer',
            'CFBundleDisplayName': 'CSV Formatter - Changing Waves',
            'CFBundleGetInfoString': 'CSV Formatter for Changing Waves',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHumanReadableCopyright': '© 2025 Changing Waves',
            'LSMinimumSystemVersion': '10.15',  # Universal requires 10.15+
        },
        'includes': [
            'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog',
            'pandas', 'numpy', 'tkinterdnd2', 'collections', 'datetime', 'threading', 'os'
        ],
        'excludes': ['matplotlib', 'scipy', 'IPython', 'jupyter', 'sympy'],
        'resources': [],
        'strip': False,
        'optimize': 2,
    }
    
    setup(
        name='Realisierungsdatenvisualizer',
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )

def main():
    """Main setup function that detects platform and runs appropriate setup."""
    system, machine = get_platform_info()
    
    if len(sys.argv) < 2:
        print("Usage: python setup_cross_platform.py [windows|macos-intel|macos-universal|auto]")
        sys.exit(1)
    
    target = sys.argv[1].lower()
    
    if target == "auto":
        if system == "Windows":
            target = "windows"
        elif system == "Darwin":
            if machine == "x86_64":
                target = "macos-intel"
            else:
                target = "macos-universal"
        else:
            print(f"Unsupported platform: {system}")
            sys.exit(1)
    
    print(f"Setting up for: {target}")
    
    # Remove the platform argument so setup doesn't get confused
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    
    if target == "windows":
        setup_windows()
    elif target == "macos-intel":
        setup_macos_intel()
    elif target == "macos-universal":
        setup_macos_universal()
    else:
        print(f"Unknown target: {target}")
        sys.exit(1)

if __name__ == "__main__":
    main()