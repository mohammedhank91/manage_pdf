import sys
import os
import shutil
import platform
from cx_Freeze import setup, Executable

def build_exe(use_pyqt5, arch="64"):
    """Build an executable with either PyQt5 or PyQt6 for the specified architecture"""
    print(f"Building {'32-bit' if arch == '32' else '64-bit'} executable with {'PyQt5' if use_pyqt5 else 'PyQt6'}")
    
    # Try to remove the build directory first to avoid permission errors
    build_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build")
    if os.path.exists(build_dir):
        try:
            print(f"Attempting to remove existing build directory: {build_dir}")
            shutil.rmtree(build_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Could not completely remove build directory: {e}")
            print("You may need to close applications using these files or run as administrator")

    # Add application icon
    icon_file = os.path.join("src", "resources", "manage_pdf.ico")

    # Determine which version of the script to use (PyQt5 or PyQt6)
    script_name = os.path.join("src", "manage_pdf_qt5.py") if use_pyqt5 else os.path.join("src", "manage_pdf_qt.py")
    
    # Set a different target name based on the version
    if use_pyqt5:
        target_name = "PDFManager_Win7_32bit.exe" if arch == "32" else "PDFManager_PyQt5.exe"
    else:
        target_name = "PDFManager_PyQt6.exe"

    # Basic dependencies
    build_exe_options = {
        "packages": ["os", "sys", "PIL"],
        "excludes": [
            "tkinter", "unittest", "email", "http", "xml", "pydoc",
            "PyQt5.QtQml", "PyQt5.QtQuick", "PyQt6.QtQml", "PyQt6.QtQuick",
            "QtQml", "QtQuick"
        ],
        "include_files": [(icon_file, icon_file)],
        "include_msvcr": True,
    }

    # Add ImageMagick portable folder if it exists
    if arch == "64":
        imagick_dir = "imagick_portable_64"
    else:
        imagick_dir = "imagick_portable"
        
    if os.path.exists(imagick_dir):
        build_exe_options["include_files"].append((imagick_dir, imagick_dir))
        print(f"Including {imagick_dir} in the build")
    else:
        print(f"Warning: {imagick_dir} not found")

    # Add the appropriate PyQt version
    if use_pyqt5:
        import PyQt5
        build_exe_options["packages"].append("PyQt5")
        # Explicitly include only the modules we need
        build_exe_options["includes"] = [
            "PyQt5.QtCore", 
            "PyQt5.QtGui", 
            "PyQt5.QtWidgets",
            "PyQt5.QtPrintSupport"
        ]
        qt_base = os.path.dirname(PyQt5.__file__)
        qt_plugins = os.path.join(qt_base, "Qt5", "plugins", "platforms")
        build_exe_options["include_files"].append(
            (qt_plugins, os.path.join("PyQt5", "Qt5", "plugins", "platforms"))
        )
    else:
        import PyQt6
        build_exe_options["packages"].append("PyQt6")
        # Explicitly include only the modules we need
        build_exe_options["includes"] = [
            "PyQt6.QtCore", 
            "PyQt6.QtGui", 
            "PyQt6.QtWidgets",
            "PyQt6.QtPrintSupport"
        ] 
        qt_base = os.path.dirname(PyQt6.__file__)
        qt_plugins = os.path.join(qt_base, "Qt6", "plugins", "platforms")
        build_exe_options["include_files"].append(
            (qt_plugins, os.path.join("PyQt6", "Qt6", "plugins", "platforms"))
        )

    # Hide the console on Windows
    base = "Win32GUI" if sys.platform == "win32" else None

    executables = [
        Executable(
            script_name,
            base=base,
            icon=icon_file,
            target_name=target_name,
            shortcut_name="PDF Manager",
            shortcut_dir="DesktopFolder",
        )
    ]

    # Save original sys.argv and replace with minimal version for cx_Freeze setup
    orig_argv = sys.argv
    sys.argv = [orig_argv[0], "build"]
    
    try:
        # Build the executable
        setup(
            name="PDF Manager",
            version="1.0.0",
            description="PDF Management Tool",
            author="mohammedhank91",
            options={"build_exe": build_exe_options},
            executables=executables,
        )
    finally:
        # Restore original sys.argv
        sys.argv = orig_argv

if __name__ == "__main__":
    # Adjust the working directory to ensure correct paths
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Parse command line arguments manually
    args_pyqt5 = "--pyqt5" in sys.argv
    args_pyqt6 = "--pyqt6" in sys.argv
    args_all = "--all" in sys.argv
    args_arch = "32" if "--arch=32" in sys.argv or "--arch" in sys.argv and sys.argv[sys.argv.index("--arch")+1] == "32" else "64"
    
    if args_all:
        # Build PyQt5 32-bit for Win7
        build_exe(use_pyqt5=True, arch="32")
        # Build PyQt6 64-bit for Win10/11
        build_exe(use_pyqt5=False, arch="64")
    elif args_pyqt5:
        build_exe(use_pyqt5=True, arch=args_arch)
    elif args_pyqt6:
        build_exe(use_pyqt5=False, arch=args_arch)
    else:
        # Default: build both
        build_exe(use_pyqt5=True, arch="32")
        build_exe(use_pyqt5=False, arch="64")
