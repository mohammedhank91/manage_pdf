#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import platform
import traceback
import shutil

def build_executable():
    """
    Build executable for the PDF Manager application.
    This will create a standalone executable compatible with 32-bit Windows.
    """
    # Check if we're running in a 32-bit Python environment
    is_32bit = platform.architecture()[0] == '32bit'
    if not is_32bit:
        print("\n=========================================================================")
        print("WARNING: You are not using 32-bit Python. The executable will only work on 64-bit systems.")
        print("For 32-bit compatibility, you need to:")
        print(" 1. Install 32-bit Python from https://www.python.org/downloads/windows/")
        print(" 2. Install the required packages in that environment:")
        print("    pip install PyQt6 Pillow pyinstaller")
        print(" 3. Run this script with the 32-bit Python installation")
        print("=========================================================================\n")
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Build aborted. Please install 32-bit Python to create a 32-bit compatible executable.")
            return

    # Check if required packages are installed
    try:
        import PyQt6
        import PIL
    except ImportError as e:
        print(f"Error: Missing required package: {e}")
        print("Please install all required packages: pip install PyQt6 Pillow pyinstaller")
        return

    # Verify PyInstaller is installed and available
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: PyInstaller is not installed or not working correctly.")
        print("Please install it with: pip install pyinstaller")
        return
    except FileNotFoundError:
        print("Error: Could not run the PyInstaller command.")
        print("Make sure Python is in your PATH and PyInstaller is installed.")
        return

    # Check if icon file exists
    icon_file = os.path.abspath('manage_pdf.ico')
    if not os.path.exists(icon_file):
        print(f"Warning: Icon file not found at {icon_file}")
        print("The application will be built without an icon.")
        icon_option = "None"
    else:
        print(f"Found icon file: {icon_file}")
        icon_option = f"'{icon_file}'"

    # Create the spec file
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
import platform

block_cipher = None

# Get the ImageMagick directory from environment variable if set
imagemagick_dir = os.environ.get('IMAGEMAGICK_DIR', None)
added_data = []

if imagemagick_dir and os.path.exists(imagemagick_dir):
    # Add ImageMagick files if the directory is specified and exists
    added_data.append((imagemagick_dir, 'ImageMagick'))

# Add the icon file to the data files
icon_file = {repr(icon_file)}
if os.path.exists(icon_file):
    added_data.append((icon_file, '.'))

a = Analysis(
    ['manage_pdf_qt.py'],
    pathex=[],
    binaries=[],
    datas=added_data,
    hiddenimports=['PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDFManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86' if platform.architecture()[0] == '32bit' else None,
    codesign_identity=None,
    entitlements_file=None,
    icon={icon_option},
)
"""

    # Write the spec file
    spec_file_path = 'pdf_manager.spec'
    with open(spec_file_path, 'w') as spec_file:
        spec_file.write(spec_content)
    
    print(f"Created PyInstaller spec file: {spec_file_path}")
    
    # Ensure the icon file is in the current directory for the build process
    if os.path.exists(icon_file) and not os.path.exists(os.path.join(os.getcwd(), 'manage_pdf.ico')):
        try:
            shutil.copy(icon_file, os.getcwd())
            print(f"Copied icon file to current directory for build process")
        except Exception as e:
            print(f"Warning: Could not copy icon file: {e}")
    
    # Run PyInstaller using python -m PyInstaller with just the spec file
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', spec_file_path]
    
    try:
        print("Building executable with PyInstaller...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.stdout:
            print("PyInstaller output:")
            print(result.stdout)
        
        print("\nBuild completed successfully!")
        exe_path = os.path.abspath(os.path.join('dist', 'PDFManager.exe'))
        if os.path.exists(exe_path):
            print(f"Executable created at: {exe_path}")
            
            # Copy icon file to dist directory to ensure it's available at runtime
            try:
                if os.path.exists(icon_file):
                    shutil.copy(icon_file, os.path.join('dist'))
                    print(f"Copied icon file to dist directory")
            except Exception as e:
                print(f"Warning: Could not copy icon file to dist directory: {e}")
                
            # Print architecture info
            arch_info = "32-bit" if is_32bit else "64-bit"
            print(f"\nExecutable architecture: {arch_info}")
            if not is_32bit:
                print("NOTE: This executable will only work on 64-bit Windows systems")
            else:
                print("NOTE: This executable will work on both 32-bit and 64-bit Windows systems")
            
            # Reminder about ImageMagick
            print("\nIMPORTANT: Remember that ImageMagick must be installed on the target computer")
            print("and must be included in the system PATH for the application to work correctly.")
            print("For 32-bit Windows systems, use the 32-bit version of ImageMagick.")
        else:
            print(f"Error: Expected executable at {exe_path} was not found.")
            print("Check the PyInstaller output for more information.")
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        if e.stdout:
            print("Output:")
            print(e.stdout)
        if e.stderr:
            print("Error output:")
            print(e.stderr)
    except Exception as e:
        print(f"An unexpected error occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    build_executable() 