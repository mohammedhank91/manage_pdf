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
    import PyInstaller  # noqa: F401
except ImportError:
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

# Check for ImageMagick and Poppler
imagick_dir = project_root / "imagick_portable_64"
poppler_dir = project_root / "poppler_portable_64"
icon_file = project_root / "src" / "resources" / "manage_pdf.ico"

if not imagick_dir.exists():
    print(f"WARNING: ImageMagick directory not found at {imagick_dir}")
if not poppler_dir.exists():
    print(f"WARNING: Poppler directory not found at {poppler_dir}")

# Paths
script_path = str(project_root / "src" / "pdf_manage.py").replace("\\", "/")
icon_path = str(icon_file).replace("\\", "/")
work_path = str(project_root / "build").replace("\\", "/")
dist_path = str(project_root / "dist").replace("\\", "/")

# Build PyInstaller command
pyinstaller_cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--name=PDFManager",
    "--clean",
    "--onedir",
    "--windowed",
    f"--icon={icon_path}",
    f"--workpath={work_path}",
    f"--distpath={dist_path}",
    "--noconfirm",
    "--log-level=DEBUG",  # Add debug logging
    # Add src directory to Python's module search path
    f"--paths={str(project_root / 'src').replace('\\', '/')}",
    # Add the whole src package to the build
    f"--add-data={str(project_root / 'src/utils').replace('\\', '/')}{os.pathsep}utils",
    f"--add-data={str(project_root / 'src/tabs').replace('\\', '/')}{os.pathsep}tabs",
    # Explicit imports for all modules
    "--hidden-import=utils",
    "--hidden-import=utils.convert",
    "--hidden-import=utils.merge",
    "--hidden-import=utils.edit_pdf",
    "--hidden-import=utils.compress",
    "--hidden-import=utils.drag_drop",
    "--hidden-import=utils.magick",
    "--hidden-import=utils.split",
    "--hidden-import=utils.developer",
    "--hidden-import=utils.check_dependencies",
    "--hidden-import=utils.image_tool",
    "--hidden-import=utils.style",
    "--hidden-import=tabs.main_tab",
    "--hidden-import=tabs.convert_tab",
    "--hidden-import=tabs.compress_tab",
    "--hidden-import=tabs.merge_tab",
    "--hidden-import=tabs.split_tab",
    "--hidden-import=PyQt6",
    "--hidden-import=PyQt6.QtWidgets",
    "--hidden-import=PyQt6.QtGui",
    "--hidden-import=PyQt6.QtCore",
    # Exclude unnecessary Qt binding
    "--exclude-module=PyQt5",
]

# Include ImageMagick and Poppler
if imagick_dir.exists():
    pyinstaller_cmd.append(f"--add-data={str(imagick_dir).replace('\\', '/')}{os.pathsep}imagick_portable_64")
if poppler_dir.exists():
    pyinstaller_cmd.append(f"--add-data={str(poppler_dir).replace('\\', '/')}{os.pathsep}poppler_portable_64")

# Add script to end
pyinstaller_cmd.append(script_path)

print("Running PyInstaller with command:")
print(" ".join(pyinstaller_cmd))

# Execute build with detailed error capture
try:
    result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"\nBuild failed with return code: {result.returncode}")
        print("\nSTDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        sys.exit(1)
    else:
        print("\nBuild successful!")
        print(f"Executable created at: {dist_path}/PDFManager/PDFManager.exe")
        print("\nTo create an installer, run:")
        print(f"iscc \"{project_root / 'build_tools' / 'PDFManager_PyInstaller_Setup.iss'}\"")
except Exception as e:
    print(f"Error building executable: {e}")
    sys.exit(1)
