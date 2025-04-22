#!/usr/bin/env python
"""
Build script for PDF Manager using PyInstaller
This script will create a standalone executable that includes ImageMagick and Ghostscript
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

# Check for ImageMagick and Ghostscript folders
imagick_dir = Path(project_root) / "imagick_portable_64"
ghostscript_dir = Path(project_root) / "ghostscript_portable"
icon_file = Path(project_root) / "src" / "resources" / "manage_pdf.ico"

if not imagick_dir.exists():
    print(f"WARNING: ImageMagick directory not found at {imagick_dir}")
if not ghostscript_dir.exists():
    print(f"WARNING: Ghostscript directory not found at {ghostscript_dir}")

# Run PyInstaller directly without creating a spec file
print("\nBuilding executable with PyInstaller...")

# Convert Windows paths to use forward slashes to avoid escape issues
script_path = str(project_root / "src" / "manage_pdf_qt.py").replace("\\", "/")
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
    "--hidden-import=xml",
    "--hidden-import=xml.dom",
    # Exclude the extra Qt binding
    "--exclude-module=PyQt5",
]

# Add paths to ImageMagick and Ghostscript as additional data
if imagick_dir.exists():
    dest_im_dir = "imagick_portable_64"
    pyinstaller_cmd.append(f"--add-data={str(imagick_dir).replace('\\', '/')}{os.pathsep}{dest_im_dir}")

if ghostscript_dir.exists():
    dest_gs_dir = "ghostscript_portable"
    pyinstaller_cmd.append(f"--add-data={str(ghostscript_dir).replace('\\', '/')}{os.pathsep}{dest_gs_dir}")

# Add the script path at the end
pyinstaller_cmd.append(script_path)

print("Running PyInstaller with command:")
print(" ".join(pyinstaller_cmd))

try:
    subprocess.check_call(pyinstaller_cmd)
    print("\nBuild successful!")
    print(f"Executable created at: {project_root}/dist/PDFManager/PDFManager.exe")
    
    # Copy the InnoSetup script for the PyInstaller build
    original_iss = Path(project_root) / "build_tools" / "PDFManager_Setup.iss"
    pyinstaller_iss = Path(project_root) / "build_tools" / "PDFManager_PyInstaller_Setup.iss"
    
    with open(original_iss, "r") as original:
        content = original.read()
        
    # Update the content for PyInstaller's output
    content = content.replace(
        r'Source: "..\build\exe.win-amd64-3.13\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs',
        r'Source: "..\dist\PDFManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs'
    )
    
    # Remove the explicit ImageMagick and Ghostscript includes since PyInstaller bundles them
    content = content.replace(
        r'Source: "..\imagick_portable_64\*"; DestDir: "{app}\imagick_portable_64"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: ImageMagickDirExists',
        r'; Source: "..\imagick_portable_64\*"; DestDir: "{app}\imagick_portable_64"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: ImageMagickDirExists'
    )
    
    content = content.replace(
        r'Source: "..\ghostscript_portable\*"; DestDir: "{app}\ghostscript_portable"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: GhostScriptDirExists',
        r'; Source: "..\ghostscript_portable\*"; DestDir: "{app}\ghostscript_portable"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: GhostScriptDirExists'
    )
    
    # Fix the executable name
    content = content.replace(
        '#define MyAppExeName "PDFManager_PyQt6.exe"',
        '#define MyAppExeName "PDFManager.exe"'
    )
    
    with open(pyinstaller_iss, "w") as new_iss:
        new_iss.write(content)
    
    print(f"\nInnoSetup script created at: {pyinstaller_iss}")
    print("To create the installer, run:")
    print(f"iscc \"{pyinstaller_iss}\"")
    
except subprocess.CalledProcessError as e:
    print(f"Error building executable: {e}")
    sys.exit(1) 