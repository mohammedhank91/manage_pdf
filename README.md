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
│   ├── pdf_manage.py        # Main application (PyQt6 version)
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
├── poppler_portable_64/        # Optional portable Poppler (64-bit)
├── temp/                       # Temporary files
└── README.md                   # This file
```

## Versions

The project contains three different implementations:

1. **pdf_manage.py** - Modern PyQt6-based GUI application with PyQt5 fallback
2. **manage_pdf_qt5.py** - PyQt5-only version for older systems like Windows 7
3. **manage_pdf_old.py** - Original script version with basic functionality

## Requirements

- Python 3.9 or higher
- PyQt6 (preferred) or PyQt5
- Pillow (PIL)
- PyPDF2
- pikepdf (for advanced PDF compression)
- ImageMagick (for some advanced image operations)
- Poppler (for high-quality PDF previews)

## Running the Application

To run the application directly:

```bash
# Using PyQt6 (recommended for Windows 10/11)
python src/pdf_manage.py

# Using PyQt5 (for Windows 7 or if PyQt6 is not available)
python src/manage_pdf_qt5.py

# Original script version
python src/manage_pdf_old.py
```

## Building and Distributing

### Building with PyInstaller

PyInstaller creates a compact and reliable executable:

```bash
# Install required dependencies first
pip install -r build_tools/requirements.txt

# On Windows, run the batch file
build_tools/build_with_pyinstaller.bat

# Or run the Python script directly
python build_tools/build_with_pyinstaller.py

# On macOS/Linux, use the shell script
chmod +x build_tools/build_app.sh
./build_tools/build_app.sh
```

The executable will be created in the `dist/PDFManager` directory.

### Creating a Windows Installer

For creating a professional Windows installer:

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Compile the InnoSetup script:
   ```
   iscc "build_tools\PDFManager_PyInstaller_Setup.iss"
   ```
3. The installer will be created in the `installer_64` directory

### Simple Distribution Method

If you prefer not to create an installer:

1. Copy the entire `dist/PDFManager` directory
2. Zip the folder
3. Share the ZIP file with users who can extract and run PDFManager.exe directly

## External Dependencies

### ImageMagick Integration

For full functionality, install ImageMagick or place the portable version in:

- `imagick_portable_64/` (for 64-bit)
- `imagick_portable/` (for 32-bit)

### Poppler for PDF Previews

For high-quality PDF previews, you need Poppler:

#### Windows

- **Portable Poppler (Recommended)**:
  - Download from [here](https://github.com/oschwartz10612/poppler-windows/releases/)
  - Extract to `poppler_portable_64/` folder next to the executable
  - No PATH configuration needed - the application will find it automatically

- **System-wide Installation**:
  - Download Poppler from [here](https://github.com/oschwartz10612/poppler-windows/releases/)
  - Add the `bin` directory to your PATH

#### macOS

```bash
# For Poppler
brew install poppler
```

#### Linux (Debian/Ubuntu)

```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

## License

This project is provided as-is for personal use.

## Credits

- Developed by mohammedhank91

## Troubleshooting

### Installation Issues

- If you encounter unusual folder or shortcut names during installation, make sure you're using the latest version of the installer
- For optimal performance, install in a path without special characters or spaces

### Runtime Issues

- **Missing Dependencies**: Make sure ImageMagick is properly installed if you're using compression features
- **ImageMagick Not Found**: Place the `imagick_portable_64` folder next to the executable or install ImageMagick system-wide
- **PDF Preview Not Working**: Install Poppler for high-quality PDF previews
  - For easiest setup, place the Poppler files in a `poppler_portable_64` folder next to the executable
- **PDF Processing Errors**: Some PDFs may be protected or corrupted. Try opening and resaving them with another PDF reader first

### Building Issues

- When building with PyInstaller, make sure all dependencies are installed: `pip install pyinstaller pillow pyqt6 pypdf2`
- If the built application doesn't find its resources, check that all paths are correctly specified in the build scripts
- For best results, include portable versions of both ImageMagick and Poppler in your distribution

### Contact and Support

If you encounter any issues not covered here, please create an issue on the GitHub repository.
