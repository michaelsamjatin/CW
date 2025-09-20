from setuptools import setup
import py2app

APP = ['csv_formatter_gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': 'CSV Formatter',
        'CFBundleDisplayName': 'CSV Formatter - World Vision',
        'CFBundleGetInfoString': 'CSV Formatter for World Vision Deutschland',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2025 World Vision Deutschland',
    },
    'includes': ['tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'pandas', 'numpy', 'tkinterdnd2'],
    'excludes': ['matplotlib', 'scipy', 'IPython', 'jupyter', 'sympy'],
    'resources': [],
    'strip': False,
}

setup(
    name='CSV Formatter',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)