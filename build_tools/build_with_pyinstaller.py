#!/usr/bin/env python
"""
Build script for PDF Manager using PyInstaller
This script will create a standalone executable that includes ImageMagick and Poppler
"""
import os
import sys
import shutil
import subprocess
import platform
import site
from pathlib import Path

# Ensure working directory is the project root
project_root = Path(__file__).parent.parent.absolute()
os.chdir(project_root)

print("=" * 60)
print("PDF Manager - PyInstaller Build Script")
print("=" * 60)

# Verify dependencies are installed
try:
    import PyInstaller
except ImportError:
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

# Check for ImageMagick folder
imagick_dir = Path(project_root) / "imagick_portable_64"
poppler_dir = Path(project_root) / "poppler_portable_64"
icon_file = Path(project_root) / "src" / "resources" / "manage_pdf.ico"

if not imagick_dir.exists():
    print(f"WARNING: ImageMagick directory not found at {imagick_dir}")

if not poppler_dir.exists():
    print(f"WARNING: Poppler directory not found at {poppler_dir}")

# Run PyInstaller directly without creating a spec file
print("\nBuilding executable with PyInstaller...")

# Convert Windows paths to use forward slashes to avoid escape issues
script_path = str(project_root / "src" / "pdf_manage.py").replace("\\", "/")
icon_path = str(icon_file).replace("\\", "/")
work_path = str(project_root / "build").replace("\\", "/")
dist_path = str(project_root / "dist").replace("\\", "/")

# Create the PyInstaller command
pyinstaller_cmd = [
    sys.executable, 
    "-m", 
    "PyInstaller",
    "--name=PDFManager",
    "--clean",
    "--windowed",  # No console window
    f"--icon={icon_path}",
    f"--workpath={work_path}",
    f"--distpath={dist_path}",
    "--noconfirm",
    "--hidden-import=PIL",
    "--hidden-import=PyPDF2",
    "--hidden-import=pikepdf",
    "--hidden-import=pdf2image",
    "--hidden-import=xml",
    "--hidden-import=xml.dom",
    # Exclude the extra Qt binding
    "--exclude-module=PyQt5",
]

# Add path to ImageMagick as additional data
if imagick_dir.exists():
    dest_im_dir = "imagick_portable_64"
    pyinstaller_cmd.append(f"--add-data={str(imagick_dir).replace('\\', '/')}{os.pathsep}{dest_im_dir}")
    print(f"Adding ImageMagick from: {imagick_dir}")

# Add path to Poppler as additional data
if poppler_dir.exists():
    dest_poppler_dir = "poppler_portable_64"
    pyinstaller_cmd.append(f"--add-data={str(poppler_dir).replace('\\', '/')}{os.pathsep}{dest_poppler_dir}")
    print(f"Adding Poppler from: {poppler_dir}")

# Add the script path at the end
pyinstaller_cmd.append(script_path)

print("Running PyInstaller with command:")
print(" ".join(pyinstaller_cmd))

try:
    subprocess.check_call(pyinstaller_cmd)
    print("\nBuild successful!")
    print(f"Executable created at: {project_root}/dist/PDFManager/PDFManager.exe")
    
    # Copy the InnoSetup script for the PyInstaller build
    original_iss = Path(project_root) / "build_tools" / "PDFManager_PyInstaller_Setup.iss"
    
    print("\nTo create an installer, run:")
    print(f"iscc \"{original_iss}\"")
    
except subprocess.CalledProcessError as e:
    print(f"Error building executable: {e}")
    sys.exit(1) 