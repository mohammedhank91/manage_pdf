import os
import sys
import subprocess
import logging
from PyQt6.QtWidgets import QMessageBox

def check_dependencies(self):
    """Check if required dependencies are available and warn the user if not."""
    logging.info("Checking dependencies...")
    
    # Check for ImageMagick
    self.has_imagick = False
    base_dir = self._app_base()
    parent_dir = os.path.dirname(base_dir)
    
    # Potential locations for imagick_portable
    imagick_paths = [
        os.path.join(base_dir, "imagick_portable_64"),
        os.path.join(parent_dir, "imagick_portable_64"),
        os.path.join(os.path.dirname(sys.executable), "imagick_portable_64"),
        "imagick_portable_64"  # Check in current working directory
    ]
    
    for path in imagick_paths:
        if os.path.exists(path):
            logging.info(f"Found ImageMagick at {path}")
            self.has_imagick = True
            break
            
    if not self.has_imagick:
        # Check if available in PATH
        try:
            result = subprocess.run(["magick", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if result.returncode == 0:
                self.has_imagick = True
                logging.info("Found ImageMagick in PATH")
        except (subprocess.SubprocessError, FileNotFoundError):
            logging.warning("ImageMagick not found in PATH")
            
    if not self.has_imagick:
        logging.warning("ImageMagick not found")
        QMessageBox.warning(
            self,
            "ImageMagick Not Found",
            "ImageMagick not found. Please place 'imagick_portable_64' folder next to the app."
        )
    
    # Check for QtWebEngine (needed for PDF preview)
    self.has_webengine = False
    try:
        from PyQt6 import QtWebEngineWidgets
        self.has_webengine = True
        logging.info("QtWebEngine is available")
    except ImportError:
        logging.warning("QtWebEngine not available - PDF viewer will be limited")
        # Disable the PDF Viewer tab if QtWebEngine is not available
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "PDF Viewer":
                self.tab_widget.setTabEnabled(i, False)
                break
        
        QMessageBox.warning(
            self,
            "PDF Viewer Limited",
            "The PDF Viewer tab is disabled because PyQt6-WebEngine is not installed.\n\n"
            "To enable the PDF viewer, install the required dependency:\n"
            "pip install PyQt6-WebEngine"
        )

def check_command_exists(self, cmd):
    """Check if a command exists by running it with '--version'"""
    try:
        exe_name = os.path.basename(cmd)
        subprocess.run(
            [cmd, "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=3  # Only wait 3 seconds max
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError, PermissionError):
        return False

def show_dependency_warning(self, title, message):
    """Show a warning about missing dependencies with more helpful instructions"""
    msg_box = QMessageBox(self)
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    
    # Make the message box wider
    msg_box.setStyleSheet("QLabel{min-width: 450px;}")
    
    msg_box.exec()
