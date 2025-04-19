# Image to PDF Converter

A Python application to convert image files (JPG, PNG) to PDF with optional compression.

## Features

- Convert multiple images to a single PDF
- Convert each image to a separate PDF
- Rotate images
- Add margins
- Choose orientation (portrait/landscape)
- Rearrange image order
- Preview PDFs
- Print PDFs
- Compress PDFs to reduce file size

## Version Information

Two versions of the application are available:

- **manage_pdf.py** - Limited version with only image-to-PDF conversion functionality
- **manage_pdf_qt.py** - Full version with all features (compression, merging, splitting, etc.)

## Requirements

- Python 3.6+
- Pillow (PIL Fork)
- PyQt6 (for GUI)
- ImageMagick (must be installed separately)

## Installation

1. Install Python 3.6 or higher if not already installed
2. Install ImageMagick from [https://imagemagick.org/script/download.php](https://imagemagick.org/script/download.php)
3. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Limited Version (Image-to-PDF only)
```
python manage_pdf.py
```

### Full Version (Recommended)
```
python manage_pdf_qt.py
```

### Basic Steps

1. Click "Select Images" to choose JPG or PNG files
2. Arrange and rotate images as needed
3. Set margin and orientation options
4. Click "Convert to PDF" to create your PDF file
5. Use "Compress PDF" to reduce the file size (Full version only)
6. Use Merge and Split features for additional PDF management (Full version only)

## PDF Compression

The compression feature (Full version only) reduces PDF file size by:
- Lowering image resolution to 150 DPI
- Using JPEG compression for images
- Slightly reducing image quality (90%)

## Notes

- For full functionality, ensure ImageMagick is properly installed and accessible in your system PATH 

# PDF Manager

A powerful desktop application to manage PDF files. Features include converting images to PDF, compressing PDFs, merging multiple PDFs, and splitting PDFs.

## Creating a 32-bit Compatible Executable

To create an executable file that works on both 32-bit and 64-bit Windows systems, follow these steps:

### Prerequisites
- Install a 32-bit version of Python (3.6+ recommended) from the [official Python website](https://www.python.org/downloads/windows/)
- Install all required dependencies:
  ```
  pip install PyQt6 Pillow pyinstaller
  ```
- Install 32-bit ImageMagick from [https://imagemagick.org/script/download.php](https://imagemagick.org/script/download.php)
  - During installation, ensure "Add to system PATH" is checked
  - Optional: Set the IMAGEMAGICK_DIR environment variable to the installation directory

### Build Instructions

1. Make sure you have all prerequisites installed and working
2. Run the build script:
   ```
   python build.py
   ```
3. The script will verify if you're using a 32-bit Python environment
4. The executable will be created in the `dist` folder as `PDFManager.exe`

### Notes on 32-bit Compatibility
- The executable must be built using a 32-bit Python environment
- Users running the executable will still need ImageMagick installed on their computer
- When distributing the application, ensure you provide a link to the 32-bit version of ImageMagick
- The executable can be run on both 32-bit and 64-bit Windows systems
- If you encounter errors during the build process, check that all dependencies are correctly installed in your 32-bit Python environment

### Troubleshooting
- If the script reports you're not using 32-bit Python, install a 32-bit version and try again
- Ensure your PYTHONPATH is pointing to the 32-bit installation when running the build script
- If ImageMagick-related features don't work in the executable, verify that ImageMagick is properly installed on the target system 