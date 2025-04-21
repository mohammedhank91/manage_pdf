# PDF Manager

A versatile PDF management tool built with Python and PyQt.

## Features

- Convert images to PDF
- Merge multiple PDFs
- Split PDFs into separate files
- Compress PDFs
- Extract pages from PDFs
- Rearrange and rotate PDF pages

## Project Structure

```
manage_pdf/
├── src/                        # Source code
│   ├── resources/              # Icons and resources
│   ├── manage_pdf_qt.py        # Main application (PyQt6 version)
│   ├── manage_pdf_qt5.py       # PyQt5 version for compatibility
│   └── manage_pdf_old.py       # Original script version
├── build_tools/                # Build scripts
│   ├── setup.py                # cx_Freeze build configuration
│   ├── requirements.txt        # Python dependencies
│   ├── PDFManager_Setup.iss    # Inno Setup script for installer
│   ├── PDFManager_Dual_Setup.iss # Dual version installer script
│   └── managepdf.ps1           # PowerShell automation script
├── temp/                       # Temporary files
└── README.md                   # This file
```

## Versions

The project contains three different implementations:

1. **manage_pdf_qt.py** - Modern PyQt6-based GUI application with PyQt5 fallback
2. **manage_pdf_qt5.py** - PyQt5-only version for older systems like Windows 7
3. **manage_pdf_old.py** - Original script version with basic functionality

## Requirements

- Python 3.6 or higher
- PyQt6 (preferred) or PyQt5
- Pillow (PIL)
- cx_Freeze (for building executables)
- ImageMagick (for some advanced image operations)

## Running the Application

To run the application directly:

```bash
# Using PyQt6 (recommended for Windows 10/11)
python src/manage_pdf_qt.py

# Using PyQt5 (for Windows 7 or if PyQt6 is not available)
python src/manage_pdf_qt5.py

# Original script version
python src/manage_pdf_old.py
```

## Building Executables

### Python Executable
Use the setup.py script in the build_tools directory to create standalone executables:

```bash
# Build PyQt6 version (64-bit, for Windows 10/11)
python build_tools/setup.py --pyqt6

# Build PyQt5 version (32-bit, for Windows 7)
python build_tools/setup.py --pyqt5 --arch=32

# Build all versions
python build_tools/setup.py --all
```

The executables will be created in the build directory.

### Windows Installer
For creating Windows installers, use the Inno Setup scripts:

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Open the appropriate script:
   - `PDFManager_Setup.iss` - For single version installer
   - `PDFManager_Dual_Setup.iss` - For dual version installer (PyQt5 & PyQt6)
3. Compile the script to create the installer

### PowerShell Automation
The project includes a PowerShell script (`managepdf.ps1`) for automating certain tasks. Run it as needed for custom automation workflows.

## ImageMagick Integration

For full functionality, install ImageMagick or place the portable version in:
- `imagick_portable_64/` (for 64-bit)
- `imagick_portable/` (for 32-bit)

## License

This project is provided as-is for personal use.

## Credits

- Developed by mohammedhank91 