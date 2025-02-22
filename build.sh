#!/bin/bash

# Ensure PyInstaller is installed
pip install pyinstaller

# Define the script to be packaged
SCRIPT="src/cli.py"

# Define the output directory
OUTPUT_DIR="dist"

# Create a binary for macOS
echo "Building for macOS..."
pyinstaller --onefile --name ontol_macos $SCRIPT

# Create a binary for Linux
echo "Building for Linux..."
pyinstaller --onefile --name ontol_linux $SCRIPT

# Clean up
rm -rf build __pycache__ *.spec

echo "Binaries created in $OUTPUT_DIR:"
ls $OUTPUT_DIR
