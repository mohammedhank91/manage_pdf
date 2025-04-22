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
│   ├── requirements.txt        # Python dependencies
│   ├── PDFManager_PyInstaller_Setup.iss # InnoSetup installer script
│   ├── build_with_pyinstaller.py # PyInstaller build script
│   └── managepdf.ps1           # PowerShell automation script
├── dist/                       # PyInstaller build output
│   └── PDFManager/             # Standalone executable and resources
├── installer_64/               # Generated installers
├── imagick_portable_64/        # Optional portable ImageMagick (64-bit)
├── ghostscript_portable/       # Optional portable Ghostscript
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
- PyPDF2
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

## Building and Distributing

### Building with PyInstaller

PyInstaller creates a compact and reliable executable:

```bash
# Run the PyInstaller build script
python build_tools/build_with_pyinstaller.py
```

The executable will be created in the `dist/PDFManager` directory.

### Creating a Windows Installer

For creating a professional Windows installer:

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Compile the InnoSetup script:
   ```
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "build_tools\PDFManager_PyInstaller_Setup.iss"
   ```
3. The installer will be created in the `installer_64` directory

### Simple Distribution Method

If you prefer not to create an installer:

1. Copy the entire `dist/PDFManager` directory
2. Zip the folder
3. Share the ZIP file with users who can extract and run PDFManager.exe directly

## ImageMagick Integration

For full functionality, install ImageMagick or place the portable version in:
- `imagick_portable_64/` (for 64-bit)
- `imagick_portable/` (for 32-bit)

## License

This project is provided as-is for personal use.

## Credits

- Developed by mohammedhank91 

## Troubleshooting

### Installation Issues
- If you encounter unusual folder or shortcut names during installation, make sure you're using the latest version of the installer
- For optimal performance, install in a path without special characters or spaces

### Runtime Issues
- **Missing Dependencies**: Make sure ImageMagick and Ghostscript are properly installed if you're using compression features
- **ImageMagick Not Found**: Place the `imagick_portable_64` folder next to the executable or install ImageMagick system-wide
- **PDF Processing Errors**: Some PDFs may be protected or corrupted. Try opening and resaving them with another PDF reader first

### Building Issues
- When building with PyInstaller, make sure all dependencies are installed: `pip install pyinstaller pillow pyqt6 pypdf2`
- If the built application doesn't find its resources, check that all paths are correctly specified in the build scripts

### Contact and Support
If you encounter any issues not covered here, please create an issue on the GitHub repository. 