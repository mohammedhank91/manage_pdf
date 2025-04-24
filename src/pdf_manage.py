import sys
import os
import logging
import types
import shutil

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, 
    QSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar, 
    QListWidget, QFrame, QVBoxLayout, QHBoxLayout, QWidget, 
    QTabWidget, QScrollArea, QListWidgetItem, QGridLayout, QGroupBox, QLineEdit, QRadioButton, QInputDialog
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

from utils.style import apply_modern_style
from utils.convert import convert_to_pdf
from utils.merge import merge_pdfs, update_merge_summary, add_pdf, remove_pdf, move_pdf_up, move_pdf_down
from utils.edit_pdf import setup_pdf_editor
from utils.compress import select_pdf, preview_pdf, print_pdf, compress_pdf
from utils.convert import update_conversion_ui, save_conversion_settings, load_conversion_settings
from utils.drag_drop import setupDragDrop, dragEnterEvent, dropEvent
from utils.magick import find_imagick, run_imagemagick
from utils.split import extract_pages, parse_page_range, extract_single_page_with_pypdf2, select_pdf_to_split, count_pages, extract_pages_with_pypdf2, set_page_range

# Import tab setup functions
from tabs.main_tab import setup_main_tab
from tabs.convert_tab import setup_convert_tab  
from tabs.compress_tab import setup_tools_tab
from tabs.merge_tab import setup_merge_tab
from tabs.split_tab import setup_split_tab

# Import utility functions
from utils.developer import add_developer_credit
from utils.check_dependencies import check_dependencies
from utils.image_tool import select_images, prev_image, next_image, update_picture_box, rotate_image
from utils.image_tool import on_listbox_select, move_up, move_down, delete_image, reset_inputs, wheelEvent

class PdfManager(QMainWindow):
    def __init__(self):
        """Initialize the Image to PDF converter."""
        # Call parent constructor
        super().__init__()
        
        # Initialize UI
        self.setWindowTitle("PDF Manager | by mohammedhank91")
        self.setGeometry(100, 100, 900, 650)  # Slightly smaller default size
        
        # Explicitly set window to be resizable
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        self.setMinimumSize(850, 690)  # Set reasonable minimum window size
        
        # Determine the application base path (works in both script and frozen mode)
        if getattr(sys, 'frozen', False):
            # We're running in a frozen/compiled environment
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller bundle
                self.base_path = sys._MEIPASS
            else:
                # cx_Freeze build
                self.base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            self.base_path = os.path.abspath(os.path.dirname(__file__))
        
        # Configure ImageMagick path - first check for portable installation
        self.imagick_path = types.MethodType(find_imagick, self)
        
        # Set application icon - try multiple potential locations
        icon_found = False
        icon_paths = [
            os.path.join(self.base_path, 'resources', 'manage_pdf.ico'),  # Icon in resources subdirectory
            os.path.join(self.base_path, 'manage_pdf.ico'),  # Icon in base directory
            os.path.join(os.path.dirname(self.base_path), 'resources', 'manage_pdf.ico'),  # Icon in parent resources
            os.path.join(os.path.dirname(self.base_path), 'manage_pdf.ico'),  # Icon in parent directory
            os.path.abspath('manage_pdf.ico'),  # Icon in current working directory
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                icon_found = True
                print(f"Icon loaded from: {icon_path}")
                break
                
        if not icon_found:
            print("Warning: Application icon could not be found at any of these locations:")
            for path in icon_paths:
                print(f"  - {path}")
        
        # Create a mutex/resource identifier for the application
        # This helps prevent multiple instances and is used by the installer
        if sys.platform == 'win32':
            try:
                import ctypes
                self.app_mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "PDFManagerMutex")
            except Exception as e:
                logging.warning(f"Could not create application mutex: {str(e)}")
        
        # call to setupdragdrop
        self.setupDragDrop = types.MethodType(setupDragDrop, self)
        self.dragEnterEvent = types.MethodType(dragEnterEvent, self)
        self.dropEvent = types.MethodType(dropEvent, self)
        self.setupDragDrop()
        
        # Apply modern styling
        apply_modern_style(self)
        
        # Global variables
        self.zoom_factor = 1.0
        self.latest_pdf = None
        self.selected_files = []
        self.rotations = {}  # Key: index, Value: rotation angle (0,90,180,270)
        self.current_index = 0
        
        # Setup logging
        log_dir = os.path.join(os.environ.get('APPDATA', ''), 'PDF Manager')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'error.log')
        logging.basicConfig(filename=log_file, level=logging.ERROR, 
                           format='%(asctime)s : %(message)s', 
                           datefmt='%Y-%m-%d %H:%M:%S')
        
        # Create central widget and tab layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        # Create tabs
        self.main_tab = QWidget()
        self.convert_tab = QWidget()
        self.tools_tab = QWidget()
        self.merge_tab = QWidget()
        self.split_tab = QWidget()
        
        # Add tabs to widget
        self.tab_widget.addTab(self.main_tab, "Main")
        self.tab_widget.addTab(self.convert_tab, "Convert")
        self.tab_widget.addTab(self.tools_tab, "Compress PDF")
        self.tab_widget.addTab(self.merge_tab, "Merge PDFs")
        self.tab_widget.addTab(self.split_tab, "Split PDF")
        
        # Add tab widget to main layout
        self.main_layout.addWidget(self.tab_widget)
        
        # Create layouts for each tab
        self.main_tab_layout = QVBoxLayout(self.main_tab)
        self.convert_tab_layout = QVBoxLayout(self.convert_tab)
        self.tools_tab_layout = QVBoxLayout(self.tools_tab)
        self.merge_tab_layout = QVBoxLayout(self.merge_tab)
        self.split_tab_layout = QVBoxLayout(self.split_tab)
        
        # Status bar at the bottom of main window (visible across all tabs)
        self.status_layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setObjectName("progressBar")
        self.status_layout.addWidget(self.progress_bar)
        
        # Add status layout to main layout
        self.main_layout.addLayout(self.status_layout)
        
        # Set up image handling methods
        self.select_images = types.MethodType(select_images, self)
        self.prev_image = types.MethodType(prev_image, self)
        self.next_image = types.MethodType(next_image, self)
        self.update_picture_box = types.MethodType(update_picture_box, self)
        self.rotate_image = types.MethodType(rotate_image, self)
        self.on_listbox_select = types.MethodType(on_listbox_select, self)
        self.move_up = types.MethodType(move_up, self)
        self.move_down = types.MethodType(move_down, self)
        self.delete_image = types.MethodType(delete_image, self)
        self.reset_inputs = types.MethodType(reset_inputs, self)
        self.wheelEvent = types.MethodType(wheelEvent, self)
        
        # PDF operations
        self.convert_to_pdf = types.MethodType(convert_to_pdf, self)
        
        # Conversion settings
        self.update_conversion_ui = types.MethodType(update_conversion_ui, self)
        self.save_conversion_settings = types.MethodType(save_conversion_settings, self)
        self.load_conversion_settings = types.MethodType(load_conversion_settings, self)
        
        # PDF merge
        self.add_pdf = types.MethodType(add_pdf, self)
        self.remove_pdf = types.MethodType(remove_pdf, self)
        self.move_pdf_up = types.MethodType(move_pdf_up, self)
        self.move_pdf_down = types.MethodType(move_pdf_down, self)
        self.merge_pdfs = types.MethodType(merge_pdfs, self)
        self.update_merge_summary = types.MethodType(update_merge_summary, self)
        
        # PDF splitting
        self.extract_pages = types.MethodType(extract_pages, self)
        self.parse_page_range = types.MethodType(parse_page_range, self)
        self.extract_single_page_with_pypdf2 = types.MethodType(extract_single_page_with_pypdf2, self)
        self.extract_pages_with_pypdf2 = types.MethodType(extract_pages_with_pypdf2, self)
        self.select_pdf_to_split = types.MethodType(select_pdf_to_split, self)
        self.count_pages = types.MethodType(count_pages, self)
        self.set_page_range = types.MethodType(set_page_range, self)
        
        # PDF compression
        self.select_pdf = types.MethodType(select_pdf, self)
        self.preview_pdf = types.MethodType(preview_pdf, self)
        self.print_pdf = types.MethodType(print_pdf, self)
        self.compress_pdf = types.MethodType(compress_pdf, self)
        
        # Set up each tab with widgets
        setup_main_tab(self)
        setup_convert_tab(self)
        setup_tools_tab(self)
        setup_merge_tab(self)
        setup_split_tab(self)
        
        # Add developer credit
        add_developer_credit(self)
        
        # Check dependencies on startup
        check_dependencies(self)

    def _app_base(self):
        """Return the base directory of the application."""
        return self.base_path

    def run_imagemagick(self, cmd):
        """Run an ImageMagick command with the portable executable if available."""
        import os
        import subprocess
        import logging
        import shutil
        
        # Always use portable version - no checking for system installation
        portable_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "imagick_portable_64", "magick.exe")
        
        if os.path.exists(portable_path):
            magick_path = portable_path
            print(f"Using portable ImageMagick: {portable_path}")
        else:
            # Fallback if portable version is not found
            magick_path = "magick"
            print(f"Portable ImageMagick not found at {portable_path}, falling back to 'magick' command")
            
        # Replace 'magick' with the full path to the executable if needed
        if magick_path != 'magick':
            # Quote the path to handle spaces
            if 'magick -' in cmd:
                invocation = cmd.replace('magick -', f'"{magick_path}" -', 1)
            elif cmd.startswith('magick '):
                invocation = cmd.replace('magick ', f'"{magick_path}" ', 1)
            else:
                invocation = cmd
        else:
            # Just use the command as is
            invocation = cmd
        
        print(f"Executing ImageMagick command: {invocation}")
        
        try:
            # Set environment variables
            env = os.environ.copy()
            
            # Simplify command for testing if there are issues
            if " -page " in invocation and " -density " in invocation:
                print("Simplifying command for better compatibility...")
                # Remove complex options that might cause issues
                invocation = invocation.replace(" -page ", " ")
                
            result = subprocess.run(
                invocation, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                env=env
            )
            print("ImageMagick command executed successfully")
            return result
        except subprocess.CalledProcessError as e:
            stderr = e.stderr if hasattr(e, 'stderr') else ""
            stdout = e.stdout if hasattr(e, 'stdout') else ""
            
            # Show more detailed error information
            error_info = f"Exit code: {e.returncode}\nStdout: {stdout}\nStderr: {stderr}"
            logging.error(f"ImageMagick failed: {error_info}")
            print(f"ImageMagick command failed: {error_info}")
            
            # Check for common error patterns
            if "not recognized" in str(stderr).lower():
                raise RuntimeError(
                    f"ImageMagick not found. Please ensure the portable version is available in the imagick_portable_64 folder."
                )
            elif "cannot find the path" in str(stderr).lower():
                raise RuntimeError(
                    f"ImageMagick error: The system cannot find one of the paths in the command. Check that all files exist."
                )
            
            # Generic error
            raise RuntimeError(f"ImageMagick error: {stderr}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PdfManager()
    window.show()
    sys.exit(app.exec())