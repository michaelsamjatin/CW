#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate analysis
pyinstaller --onefile --windowed --name "Realisierungsdatenvisualizer" --icon="logo.png" --add-data "/Users/michaelsamjatin/miniconda3/envs/analysis/lib/python3.9/site-packages/tkinterdnd2:tkinterdnd2" csv_formatter_gui.py