#!/bin/bash
# Build script for PDF Manager

echo "====================================="
echo "PDF Manager - Build Script"
echo "====================================="
echo ""

# Ensure in project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Check dependencies
echo "Checking for required dependencies..."
python -m pip install -r build_tools/requirements.txt

# Run the PyInstaller build script
echo ""
echo "Building application with PyInstaller..."
python build_tools/build_with_pyinstaller.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to build application!"
    exit 1
fi

# Check if InnoSetup is available (for Windows)
if command -v iscc &> /dev/null; then
    echo ""
    echo "Creating installer with InnoSetup..."
    iscc "build_tools/PDFManager_PyInstaller_Setup.iss"
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create installer!"
        exit 1
    fi
    
    echo ""
    echo "Installer created successfully in 'installer_64' directory."
else
    echo ""
    echo "InnoSetup not found. Skipping installer creation."
    echo "If you want to create an installer, please install InnoSetup and add 'iscc' to your PATH."
fi

echo ""
echo "Build completed successfully!"
echo "Application is available in 'dist/PDFManager' directory."
echo "=====================================" 