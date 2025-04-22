import sys
import os
import subprocess
import math
import logging
from datetime import datetime
import tempfile
import PyPDF2  # Add global import for PyPDF2
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, 
        QSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar, 
        QListWidget, QFrame, QVBoxLayout, QHBoxLayout, QWidget, 
        QTabWidget, QScrollArea, QListWidgetItem, QGridLayout, QGroupBox, QLineEdit, QRadioButton, QInputDialog
    )
    from PyQt6.QtGui import (
        QPixmap, QImage, QIcon
    )
    from PyQt6.QtCore import (
        Qt, QSize
    )
except ImportError:
    # Fallback to PyQt5 if PyQt6 is not available
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, 
        QSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar, 
        QListWidget, QFrame, QVBoxLayout, QHBoxLayout, QWidget, 
        QTabWidget, QScrollArea, QListWidgetItem, QGridLayout, QGroupBox, QLineEdit, QRadioButton
    )
    from PyQt5.QtGui import (
        QPixmap, QImage, QIcon
    )
    from PyQt5.QtCore import (
        Qt, QSize
    )
from PIL import Image

# Get the application base path in a way that works with cx_Freeze and normal Python
def get_base_path():
    """Get the base path for resources that works with cx_Freeze and normal Python"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable (cx_Freeze)
        return os.path.dirname(sys.executable)
    else:
        # Running from script
        return os.path.dirname(os.path.abspath(__file__))



class ImageToPdfConverter(QMainWindow):
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
        self.imagick_path = self.find_imagick()
        
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
        self.setupDragDrop()
        
        # Apply modern styling
        self.apply_modern_style()
        
        # Global variables
        self.zoom_factor = 1.0
        self.latest_pdf = None
        self.selected_files = []
        self.rotations = {}  # Key: index, Value: rotation angle (0,90,180,270)
        self.current_index = 0
        
        # Setup logging
        logging.basicConfig(filename="error.log", level=logging.ERROR, 
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
        
        # Set up each tab with widgets
        self.setup_main_tab()
        self.setup_convert_tab()
        self.setup_tools_tab()
        self.setup_merge_tab()
        self.setup_split_tab()
        
        # Add developer credit
        self.add_developer_credit()
        
        # Check dependencies on startup
        self.check_dependencies()
        
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
        
        # Check for Ghostscript
        self.has_ghostscript = False
        
        # Potential locations for ghostscript_portable
        gs_paths = [
            os.path.join(base_dir, "ghostscript_portable"),
            os.path.join(parent_dir, "ghostscript_portable"),
            os.path.join(os.path.dirname(sys.executable), "ghostscript_portable"),
            "ghostscript_portable"  # Check in current working directory
        ]
        
        for path in gs_paths:
            if os.path.exists(path):
                logging.info(f"Found Ghostscript at {path}")
                self.has_ghostscript = True
                break
                
        if not self.has_ghostscript:
            # Check if available in PATH
            try:
                result = subprocess.run(["gswin64c", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                if result.returncode == 0:
                    self.has_ghostscript = True
                    logging.info("Found Ghostscript in PATH")
            except (subprocess.SubprocessError, FileNotFoundError):
                logging.warning("Ghostscript not found in PATH")
                
        if not self.has_ghostscript:
            logging.warning("Ghostscript not found")
            QMessageBox.warning(
                self,
                "Ghostscript Not Found",
                "Ghostscript not found. Please place 'ghostscript_portable' folder next to the app."
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
    
    def apply_modern_style(self):
        """Apply a modern style to the entire application"""
        # Main style for the app
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f5f5f7;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
            }
            
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 8px;
                background-color: white;
                padding: 6px;
            }
            
            QTabBar::tab {
                background-color: #e0e0e5;
                color: #505050;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                padding: 6px 12px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 80px;
                font-weight: bold;
                font-size: 9pt;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                color: #1e88e5;
                border-bottom: none;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #efefef;
                color: #1976d2;
                border-color: #aaaaaa;
            }
            
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 9pt;
            }
            
            QPushButton:hover {
                background-color: #1976d2;
                border: 1px solid #1565c0;
                color: white;
            }
            
            QPushButton:pressed {
                background-color: #0d47a1;
                color: white;
            }
            
            QPushButton:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
            
            /* Specific button styles */
            QPushButton[objectName="btn_convert"] {
                background-color: #4caf50;
            }
            
            QPushButton[objectName="btn_convert"]:hover {
                background-color: #388e3c;
                border: 1px solid #2e7d32;
            }
            
            QPushButton[objectName="btn_compress"] {
                background-color: #9c27b0;
            }
            
            QPushButton[objectName="btn_compress"]:hover {
                background-color: #7b1fa2;
                border: 1px solid #6a1b9a;
            }
            
            QPushButton[objectName="btn_extract_pages"] {
                background-color: #4caf50;
            }
            
            QPushButton[objectName="btn_extract_pages"]:hover {
                background-color: #388e3c;
                border: 1px solid #2e7d32;
            }
            
            QPushButton[objectName="btn_merge_pdfs"] {
                background-color: #ff9800;
            }
            
            QPushButton[objectName="btn_merge_pdfs"]:hover {
                background-color: #f57c00;
                border: 1px solid #ef6c00;
            }
            
            QPushButton[objectName="btn_delete"], QPushButton[objectName="btn_remove_pdf"] {
                background-color: #f44336;
            }
            
            QPushButton[objectName="btn_delete"]:hover, QPushButton[objectName="btn_remove_pdf"]:hover {
                background-color: #d32f2f;
                border: 1px solid #c62828;
            }
            
            QPushButton[objectName="btn_preview_pdf"], QPushButton[objectName="btn_print_pdf"] {
                background-color: #03a9f4;
            }
            
            QPushButton[objectName="btn_preview_pdf"]:hover, QPushButton[objectName="btn_print_pdf"]:hover {
                background-color: #0288d1;
                border: 1px solid #0277bd;
            }
            
            /* Common button styles */
            QPushButton#btn_select, QPushButton#btn_select_pdf, QPushButton#btn_select_pdf_to_split, QPushButton#btn_add_pdf {
                background-color: #2196f3;
            }
            
            QPushButton#btn_select:hover, QPushButton#btn_select_pdf:hover, 
            QPushButton#btn_select_pdf_to_split:hover, QPushButton#btn_add_pdf:hover {
                background-color: #1976d2;
                border: 1px solid #1565c0;
            }
            
            /* Navigation button styles */
            QPushButton#btn_prev, QPushButton#btn_next, QPushButton#btn_up, QPushButton#btn_down,
            QPushButton#btn_move_pdf_up, QPushButton#btn_move_pdf_down {
                background-color: #607d8b;
                padding: 4px 8px;
            }
            
            QPushButton#btn_prev:hover, QPushButton#btn_next:hover, QPushButton#btn_up:hover, QPushButton#btn_down:hover,
            QPushButton#btn_move_pdf_up:hover, QPushButton#btn_move_pdf_down:hover {
                background-color: #455a64;
                border: 1px solid #37474f;
            }
            
            /* Quick selection button styles */
            QPushButton[text="All Pages"], QPushButton[text="Even Pages"], QPushButton[text="Odd Pages"] {
                background-color: #03a9f4;
                padding: 4px 8px;
            }
            
            QPushButton[text="All Pages"]:hover, QPushButton[text="Even Pages"]:hover, QPushButton[text="Odd Pages"]:hover {
                background-color: #0288d1;
                border: 1px solid #0277bd;
            }
            
            QLabel {
                color: #424242;
                font-size: 9pt;
            }
            
            QLabel[objectName="statusLabel"] {
                color: #1976d2;
                font-weight: bold;
                padding: 5px;
                background-color: rgba(225, 245, 254, 0.7);
                border-radius: 4px;
            }
            
            QProgressBar {
                border: 1px solid #bbbbbb;
                border-radius: 4px;
                background-color: #f5f5f5;
                text-align: center;
                height: 18px;
            }
            
            QProgressBar::chunk {
                background-color: #2196f3;
                width: 10px;
                border-radius: 3px;
            }
            
            QSpinBox, QComboBox {
                border: 1px solid #bbbbbb;
                border-radius: 4px;
                padding: 3px;
                background-color: white;
                font-size: 9pt;
            }
            
            QSpinBox:hover, QComboBox:hover {
                border: 1px solid #2196f3;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid #bbbbbb;
            }
            
            QComboBox::drop-down:hover {
                background-color: #e3f2fd;
            }
            
            QListWidget {
                border: 1px solid #bbbbbb;
                border-radius: 4px;
                background-color: white;
                font-size: 9pt;
            }
            
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #eeeeee;
            }
            
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QCheckBox {
                spacing: 4px;
                font-size: 9pt;
            }
            
            QCheckBox:hover {
                color: #1976d2;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            
            QCheckBox::indicator:unchecked {
                border: 1px solid #bbbbbb;
                background-color: white;
                border-radius: 3px;
            }
            
            QCheckBox::indicator:unchecked:hover {
                border: 1px solid #2196f3;
            }
            
            QCheckBox::indicator:checked {
                border: 1px solid #2196f3;
                background-color: #2196f3;
                border-radius: 3px;
            }
            
            QFrame[frameShape="4"] {
                color: #e0e0e0;
                margin: 8px 0px;
            }
            
            /* Header styles */
            QLabel[objectName="main_header"], QLabel[objectName="convert_header"], 
            QLabel[objectName="tools_header"], QLabel[objectName="merge_header"],
            QLabel[objectName="split_header"] {
                font-size: 14pt;
                font-weight: bold;
                color: #1e88e5;
            }
        """)
        
    def add_developer_credit(self):
        """Add developer credit to the application"""
        credit_layout = QHBoxLayout()
        
        credit_label = QLabel("© Developed by: <a href='https://github.com/mohammedhank91'>mohammedhank91</a>")
        credit_label.setStyleSheet("color: #757575; font-size: 8pt;")
        credit_label.setOpenExternalLinks(True)
        credit_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        credit_layout.addStretch()
        credit_layout.addWidget(credit_label)
        
        self.main_layout.addLayout(credit_layout)
        
    def setup_main_tab(self):
        """Setup the Main Tab - Image selection, preview, and management"""
        # Set smaller content margins for the entire tab
        main_layout_margins = self.main_tab_layout.contentsMargins()
        self.main_tab_layout.setContentsMargins(main_layout_margins.left(), 5, main_layout_margins.right(), 5)
        self.main_tab_layout.setSpacing(5)  # Reduce overall spacing in the tab
        
        # Header label - Smaller with reduced margin
        self.main_header = QLabel("Select and Manage Images")
        self.main_header.setObjectName("main_header")
        self.main_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_header.setStyleSheet("font-size: 12pt; margin-bottom: 2px;")
        self.main_tab_layout.addWidget(self.main_header)
        
        # Select images button - Smaller with tighter layout
        select_button_layout = QHBoxLayout()
        select_button_layout.setContentsMargins(0, 2, 0, 2)  # Minimal margins
        select_button_layout.setSpacing(0)
        
        self.btn_select = QPushButton("Select Images")
        self.btn_select.setObjectName("btn_select")
        self.btn_select.clicked.connect(self.select_images)
        self.btn_select.setFixedSize(130, 25)  # Smaller button
        self.btn_select.setStyleSheet("padding: 2px;")
        select_button_layout.addWidget(self.btn_select)
        select_button_layout.addStretch()
        self.main_tab_layout.addLayout(select_button_layout)
        
        # Middle section layout with proper sizing
        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(8)
        
        # Image preview area - Allow flexible sizing
        preview_group = QVBoxLayout()
        preview_group.setContentsMargins(0, 0, 0, 0)
        
        preview_label = QLabel("Image Preview:")
        preview_label.setStyleSheet("font-weight: bold; font-size: 9pt; color: #424242; margin: 0px;")
        preview_group.addWidget(preview_label)
        
        self.preview_frame = QFrame()
        self.preview_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.preview_frame.setStyleSheet("border: 1px solid #cccccc; border-radius: 4px; background-color: white;")
        # Use reasonable minimum size but allow resizing
        self.preview_frame.setMinimumSize(350, 400)
        
        self.preview_layout = QVBoxLayout(self.preview_frame)
        self.preview_layout.setContentsMargins(3, 3, 3, 3)  # Minimal internal padding
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: none; background-color: white;")
        self.preview_layout.addWidget(self.preview_label)
        
        preview_group.addWidget(self.preview_frame)
        
        # Navigation buttons - Smaller and more compact
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 2, 0, 0)  # Minimal margins
        nav_layout.setSpacing(4)  # Minimal spacing
        
        self.btn_prev = QPushButton("Prev")  # Shorter text
        self.btn_prev.setObjectName("btn_prev")
        self.btn_prev.clicked.connect(self.prev_image)
        self.btn_prev.setFixedHeight(22)  # Smaller height
        self.btn_prev.setStyleSheet("padding: 1px 4px;")  # Smaller padding
        nav_layout.addWidget(self.btn_prev)
        
        self.btn_next = QPushButton("Next")
        self.btn_next.setObjectName("btn_next")
        self.btn_next.clicked.connect(self.next_image)
        self.btn_next.setFixedHeight(22)  # Smaller height
        self.btn_next.setStyleSheet("padding: 1px 4px;")  # Smaller padding
        nav_layout.addWidget(self.btn_next)
        
        self.btn_rotate = QPushButton("Rotate")  # Shorter text
        self.btn_rotate.clicked.connect(self.rotate_image)
        self.btn_rotate.setFixedHeight(22)  # Smaller height
        self.btn_rotate.setStyleSheet("padding: 1px 4px;")  # Smaller padding
        nav_layout.addWidget(self.btn_rotate)
        
        nav_layout.addStretch()
        preview_group.addLayout(nav_layout)
        middle_layout.addLayout(preview_group, 3)  # Give more width to preview
        
        # Right panel - Use flexible sizing
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(0, 0, 0, 0)
        right_panel.setSpacing(2)
        
        list_label = QLabel("Images List:")
        list_label.setStyleSheet("font-weight: bold; font-size: 9pt; color: #424242; margin: 0px;")
        right_panel.addWidget(list_label)
        
        # Image list - Use a reasonable minimum height
        self.listbox = QListWidget()
        self.listbox.currentRowChanged.connect(self.on_listbox_select)
        self.listbox.setMinimumHeight(100)  # Reasonable minimum but allows resizing
        self.listbox.setStyleSheet("""
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
                padding: 2px;
                font-size: 9pt;
            }
            QListWidget::item {
                border-bottom: 1px solid #eeeeee;
                padding: 2px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        right_panel.addWidget(self.listbox)
        
        # Image control buttons - More compact
        img_controls = QVBoxLayout()
        img_controls.setContentsMargins(0, 0, 0, 0)
        img_controls.setSpacing(2)
        
        img_controls_label = QLabel("Image Actions:")
        img_controls_label.setStyleSheet("font-weight: bold; font-size: 9pt; color: #424242; margin: 1px 0px;")
        img_controls.addWidget(img_controls_label)
        
        # Delete button
        self.btn_delete = QPushButton("Delete")  # Shorter text
        self.btn_delete.setObjectName("btn_delete")
        self.btn_delete.clicked.connect(self.delete_image)
        self.btn_delete.setFixedHeight(22)  # Smaller height
        self.btn_delete.setStyleSheet("padding: 1px 4px;")  # Smaller padding
        img_controls.addWidget(self.btn_delete)
        
        # Reorder buttons layout - More compact and horizontal
        reorder_layout = QHBoxLayout()
        reorder_layout.setContentsMargins(0, 0, 0, 0)
        reorder_layout.setSpacing(3)
        
        reorder_label = QLabel("Reorder:")
        reorder_label.setStyleSheet("font-size: 9pt;")
        reorder_layout.addWidget(reorder_label)
        
        self.btn_up = QPushButton("↑")  # Use arrow symbol to save space
        self.btn_up.setObjectName("btn_up")
        self.btn_up.clicked.connect(self.move_up)
        self.btn_up.setFixedSize(22, 22)  # Square button
        self.btn_up.setStyleSheet("padding: 0px;")  # No padding
        reorder_layout.addWidget(self.btn_up)
        
        self.btn_down = QPushButton("↓")  # Use arrow symbol to save space
        self.btn_down.setObjectName("btn_down")
        self.btn_down.clicked.connect(self.move_down)
        self.btn_down.setFixedSize(22, 22)  # Square button
        self.btn_down.setStyleSheet("padding: 0px;")  # No padding
        reorder_layout.addWidget(self.btn_down)
        
        reorder_layout.addStretch()
        img_controls.addLayout(reorder_layout)
        
        # Reset button
        self.btn_reset = QPushButton("Reset All")
        self.btn_reset.setStyleSheet("background-color: #ff9800; color: white; padding: 1px 4px;")
        self.btn_reset.clicked.connect(self.reset_inputs)
        self.btn_reset.setFixedHeight(22)  # Smaller height
        img_controls.addWidget(self.btn_reset)
        
        right_panel.addLayout(img_controls)
        middle_layout.addLayout(right_panel, 2)  # Slightly less width for list panel
        
        self.main_tab_layout.addLayout(middle_layout)
        
        # Add a small spacing at the bottom
        self.main_tab_layout.addSpacing(5)
    
    def setup_convert_tab(self):
        # Convert Tab - PDF conversion settings and actions
        
        # Header label
        self.convert_header = QLabel("PDF Conversion Settings")
        self.convert_header.setObjectName("convert_header")
        self.convert_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.convert_tab_layout.addWidget(self.convert_header)
        
        # Main container with two columns
        container_layout = QHBoxLayout()
        
        # Left panel - Settings
        settings_panel = QFrame()
        settings_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        settings_panel.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #e0e0e0; padding: 2px;")
        settings_layout = QVBoxLayout(settings_panel)
        
        # Settings panel header
        settings_title = QLabel("Configuration Options")
        settings_title.setStyleSheet("font-weight: bold; color: #1e88e5; font-size: 12pt;")
        settings_layout.addWidget(settings_title)
        
        # Output section
        output_group = QFrame()
        output_group.setStyleSheet("background-color: #f5f5f7; border-radius: 8px; padding: 2px;")
        output_layout = QVBoxLayout(output_group)
        
        output_header = QLabel("Output Settings")
        output_header.setStyleSheet("font-weight: bold; color: #424242;")
        output_layout.addWidget(output_header)
        
        # Checkbox for separate PDFs
        self.chk_separate = QCheckBox("Save each image as a separate PDF")
        self.chk_separate.setStyleSheet("color: #424242;")
        output_layout.addWidget(self.chk_separate)
        
        # Paper settings
        paper_layout = QGridLayout()
        
        paper_layout.addWidget(QLabel("Paper Size:"), 0, 0)
        self.paper_size = QComboBox()
        self.paper_size.addItems(["A4", "Letter", "Legal", "A3", "A5"])
        self.paper_size.setStyleSheet("""
            QComboBox {
                padding: 4px;
                padding-right: 20px; /* Make room for the arrow */
                border: 1px solid #100101;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 16px;
                border-left: 1px solid #090707;
            }
            QComboBox::down-arrow {
                width: 8px;
                height: 8px;
                background: none;
                border-top: 5px solid #000000;
                border-right: 4px solid transparent;
                border-left: 4px solid transparent;
            }
        """)
        self.paper_size.setCurrentIndex(0)  # Default to A4
        
        paper_layout.addWidget(self.paper_size, 0, 1)
        
        paper_layout.addWidget(QLabel("Orientation:"), 1, 0)
        self.combo_orient = QComboBox()
        self.combo_orient.addItems(["Portrait", "Landscape"])
        self.combo_orient.setStyleSheet("""
            QComboBox {
                padding: 4px;
                padding-right: 20px; /* Make room for the arrow */
                border: 1px solid #100101;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 16px;
                border-left: 1px solid #090707;
            }
            QComboBox::down-arrow {
                width: 8px;
                height: 8px;
                background: none;
                border-top: 5px solid #000000;
                border-right: 4px solid transparent;
                border-left: 4px solid transparent;
            }
        """)
        self.combo_orient.setCurrentIndex(0)  # Default to Portrait
        
        paper_layout.addWidget(self.combo_orient, 1, 1)
        
        paper_layout.addWidget(QLabel("Margin (px):"), 2, 0)
        self.num_margin = QSpinBox()
        self.num_margin.setRange(0, 100)
        self.num_margin.setValue(10)
        paper_layout.addWidget(self.num_margin, 2, 1)
        
        output_layout.addLayout(paper_layout)
        settings_layout.addWidget(output_group)
        
        # Quality section
        quality_group = QFrame()
        quality_group.setStyleSheet("background-color: #f5f5f7; border-radius: 8px; padding: 10px; margin-top: 15px;")
        quality_layout = QVBoxLayout(quality_group)
        
        quality_header = QLabel("Quality Settings")
        quality_header.setStyleSheet("font-weight: bold; color: #424242;")
        quality_layout.addWidget(quality_header)
        
        # Resolution
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Resolution:"))
        self.resolution = QComboBox()
        self.resolution.addItems(["Standard (150 DPI)", "Web (72 DPI)", "Print (300 DPI)", "High Quality (600 DPI)"])
        self.resolution.setStyleSheet("""
            QComboBox {
                padding: 4px;
                padding-right: 20px; /* Make room for the arrow */
                border: 1px solid #100101;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 16px;
                border-left: 1px solid #090707;
            }
            QComboBox::down-arrow {
                width: 8px;
                height: 8px;
                background: none;
                border-top: 5px solid #000000;
                border-right: 4px solid transparent;
                border-left: 4px solid transparent;
            }
        """)
        self.resolution.setCurrentIndex(0)  # Default to balanced
        
        resolution_layout.addWidget(self.resolution)
        quality_layout.addLayout(resolution_layout)
        
        # Compression
        compression_layout = QHBoxLayout()
        compression_layout.addWidget(QLabel("Compression:"))
        self.compression = QComboBox()
        self.compression.addItems(["Maximum Quality (300 DPI, 100%)", 
                                   "High Quality (250 DPI, 95%)", 
                                   "Balanced (200 DPI, 90%)", 
                                   "Maximum Compression (150 DPI, 85%)"])
        self.compression.setStyleSheet("""
            QComboBox {
                padding: 4px;
                padding-right: 20px; /* Make room for the arrow */
                border: 1px solid #100101;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 16px;
                border-left: 1px solid #090707;
            }
            QComboBox::down-arrow {
                width: 8px;
                height: 8px;
                background: none;
                border-top: 5px solid #000000;
                border-right: 4px solid transparent;    
                border-left: 4px solid transparent;
            }
        """)
        self.compression.setCurrentIndex(0)  # Default to balanced
            
        compression_layout.addWidget(self.compression)
        quality_layout.addLayout(compression_layout)
        
        settings_layout.addWidget(quality_group)
        
        # Add stretch to push everything up
        settings_layout.addStretch()
        
        # Right panel - Preview and actions
        action_panel = QFrame()
        action_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        action_panel.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #e0e0e0; padding: 15px;")
        action_layout = QVBoxLayout(action_panel)
        
        # Action panel header
        action_title = QLabel("Actions")
        action_title.setStyleSheet("font-weight: bold; color: #1e88e5; font-size: 12pt;")
        action_layout.addWidget(action_title)
        
        # Image summary
        self.image_summary = QLabel("No images selected yet")
        self.image_summary.setStyleSheet("background-color: #e8f5e9; padding: 10px; border-radius: 8px;")
        self.image_summary.setWordWrap(True)
        self.image_summary.setMinimumHeight(60)
        action_layout.addWidget(self.image_summary)
        
        # Settings summary
        self.settings_summary = QLabel("Current settings: A4, Portrait, 10px margins")
        self.settings_summary.setStyleSheet("color: #616161; font-style: italic; margin-top: 5px;")
        action_layout.addWidget(self.settings_summary)
        
        # Conversion button - large and prominent
        self.btn_convert = QPushButton("Convert to PDF")
        self.btn_convert.setObjectName("btn_convert")
        self.btn_convert.clicked.connect(self.convert_to_pdf)
        self.btn_convert.setFixedHeight(50)
        self.btn_convert.setStyleSheet("background-color: #4caf50; font-size: 12pt;")
        action_layout.addWidget(self.btn_convert)
        
        # Quick action buttons
        quick_actions = QHBoxLayout()
        
        self.btn_save_settings = QPushButton("Save Settings")
        self.btn_save_settings.setObjectName("btn_save_settings")
        self.btn_save_settings.clicked.connect(self.save_conversion_settings)
        self.btn_save_settings.setStyleSheet("color: white; background-color: #2196f3; font-weight: bold;")
        
        self.btn_load_settings = QPushButton("Load Settings")
        self.btn_load_settings.setObjectName("btn_load_settings")
        self.btn_load_settings.clicked.connect(self.load_conversion_settings)
        self.btn_load_settings.setStyleSheet("color: white; background-color: #2196f3; font-weight: bold;")
        
        quick_actions.addWidget(self.btn_save_settings)
        quick_actions.addWidget(self.btn_load_settings)
        action_layout.addLayout(quick_actions)
        
        # Tips and help
        tips_box = QLabel(
            "Tips:\n"
            "• Higher resolution gives better quality but larger files\n"
            "• Use Landscape for wide images\n"
            "• Add margins for better document presentation\n"
            "• You can save your settings for future use"
        )
        tips_box.setStyleSheet("background-color: #e3f2fd; color: #1565c0; padding: 12px; border-radius: 8px; margin-top: 15px;")
        tips_box.setWordWrap(True)
        action_layout.addWidget(tips_box)
        
        # Add stretch to push everything up
        action_layout.addStretch()
        
        # Add panels to container
        container_layout.addWidget(settings_panel, 3)  # 60% width
        container_layout.addWidget(action_panel, 2)    # 40% width
        
        # Add container to tab layout
        self.convert_tab_layout.addLayout(container_layout)
        
        # Update UI based on selected images
        self.update_conversion_ui()
        
        # Connect signals
        self.paper_size.currentTextChanged.connect(self.update_conversion_ui)
        self.combo_orient.currentTextChanged.connect(self.update_conversion_ui)
        self.num_margin.valueChanged.connect(self.update_conversion_ui)
        self.resolution.currentTextChanged.connect(self.update_conversion_ui)
        self.compression.currentTextChanged.connect(self.update_conversion_ui)
    
    def update_conversion_ui(self):
        """Update the conversion UI based on selected files and settings"""
        if hasattr(self, 'image_summary') and hasattr(self, 'settings_summary'):
            # Update image summary
            if self.selected_files:
                num_files = len(self.selected_files)
                total_size = sum(os.path.getsize(f) for f in self.selected_files) / 1024  # KB
                
                if total_size > 1024:
                    size_str = f"{total_size/1024:.1f} MB"
                else:
                    size_str = f"{total_size:.1f} KB"
                    
                self.image_summary.setText(f"Ready to convert {num_files} image{'s' if num_files > 1 else ''}\nTotal size: {size_str}")
            else:
                self.image_summary.setText("No images selected yet. Please select images in the Main tab first.")
            
            # Update settings summary
            self.settings_summary.setText(
                f"Current settings: {self.paper_size.currentText()}, "
                f"{self.combo_orient.currentText()}, "
                f"{self.num_margin.value()}px margins, "
                f"{self.resolution.currentText()}"
            )
    
    def save_conversion_settings(self):
        """Save the current conversion settings to a preset"""
        # This would normally save to a config file, but for simplicity just show a message
        QMessageBox.information(self, "Settings Saved", "Settings have been saved as a preset.\n(This is just a placeholder - actual saving would be implemented in a real application)")
    
    def load_conversion_settings(self):
        """Load saved conversion settings from a preset"""
        # This would normally load from a config file, but for simplicity just show a message
        QMessageBox.information(self, "Settings Loaded", "Settings have been loaded from a preset.\n(This is just a placeholder - actual loading would be implemented in a real application)")
    
    def setupDragDrop(self):
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        """Handle dropping files onto the application"""
        if event.mimeData().hasUrls():
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            
            # Determine which tab is active and process files accordingly
            current_tab = self.tab_widget.currentIndex()
            
            if current_tab == 0:  # Main tab
                # Proceed only if image files are dropped
                image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
                if image_files:
                    for file in image_files:
                        if file not in self.selected_files:
                            self.selected_files.append(file)
                            self.listbox.addItem(os.path.basename(file))
                    
                    if len(self.selected_files) > 0:
                        if self.current_index < 0:
                            self.current_index = 0
                        self.update_picture_box()
                        self.status_label.setText(f"Added {len(image_files)} images. Total: {len(self.selected_files)}")
            elif current_tab == 3:  # Merge tab
                # Add PDFs to merge list
                pdf_files = [f for f in files if f.lower().endswith('.pdf')]
                for pdf in pdf_files:
                    self.pdf_listbox.addItem(pdf)
                self.btn_merge_pdfs.setEnabled(self.pdf_listbox.count() > 1)
            elif current_tab == 4:  # Split tab
                pdf_files = [f for f in files if f.lower().endswith('.pdf')]
                if pdf_files and os.path.exists(pdf_files[0]):
                    pdf_file = pdf_files[0]
                    self.split_pdf_path.setText(pdf_file)
                    self.btn_extract_pages.setEnabled(True)
                    
                    # Get file size information
                    file_size = os.path.getsize(pdf_file) / 1024  # KB
                    if file_size > 1024:
                        file_size = file_size / 1024  # MB
                        size_str = f"{file_size:.2f} MB"
                    else:
                        size_str = f"{file_size:.2f} KB"
                    
                    # Try to get page count using our improved method
                    try:
                        page_count = self.count_pages(pdf_file)
                        self.split_pdf_info.setText(f"PDF Information: {os.path.basename(pdf_file)}\nPages: {page_count}\nSize: {size_str}")
                    except Exception as e:
                        logging.error(f"Failed to count pages: {str(e)}")
                        self.split_pdf_info.setText(f"PDF Information: {os.path.basename(pdf_file)}\nPages: Unknown\nSize: {size_str}")
                        QMessageBox.warning(self, "Warning", f"Could not determine page count: {str(e)}\n\nYou can still extract pages, but you'll need to know the total number of pages in the document.")
    
    def setup_pdf_editor(self):
        # Add a new tab or dialog
        self.editor_tab = QWidget()
        editor_layout = QVBoxLayout(self.editor_tab)
        
        # PDF Preview with pages
        self.page_preview = QScrollArea()
        self.page_container = QWidget()
        self.page_layout = QHBoxLayout(self.page_container)
        self.page_previews = []
        
        # Rotation buttons for each page
        editor_layout.addWidget(QLabel("Rotate or Reorder Pages:"))
        
        # Page controls
        controls_layout = QHBoxLayout()
        self.btn_rotate_left = QPushButton("Rotate Left")
        self.btn_rotate_right = QPushButton("Rotate Right")
        self.btn_move_page_left = QPushButton("Move Left")
        self.btn_move_page_right = QPushButton("Move Right")
        
        self.btn_rotate_left.clicked.connect(lambda: self.rotate_pdf_page(-90))
        self.btn_rotate_right.clicked.connect(lambda: self.rotate_pdf_page(90))
        self.btn_move_page_left.clicked.connect(self.move_pdf_page_left)
        self.btn_move_page_right.clicked.connect(self.move_pdf_page_right)
        
        controls_layout.addWidget(self.btn_rotate_left)
        controls_layout.addWidget(self.btn_rotate_right)
        controls_layout.addWidget(self.btn_move_page_left)
        controls_layout.addWidget(self.btn_move_page_right)
        
        editor_layout.addLayout(controls_layout)
        
        # Apply changes button
        self.btn_apply_changes = QPushButton("Apply Changes")
        self.btn_apply_changes.clicked.connect(self.apply_pdf_changes)
        editor_layout.addWidget(self.btn_apply_changes)
    
    def rotate_pdf_page(self, angle):
        # Implement PDF page rotation using PyMuPDF or PyPDF2
        # Update the preview of the selected page
        pass
    
    def move_pdf_page_left(self):
        # Swap the selected page with the one before it
        pass
    
    def move_pdf_page_right(self):
        # Swap the selected page with the one after it
        pass
    
    def apply_pdf_changes(self):
        # Save the PDF with the new page order and orientations
        pass

    def select_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp)"
        )
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    self.listbox.addItem(os.path.basename(file))
            
            if self.current_index < 0 or self.current_index >= len(self.selected_files):
                self.current_index = 0
            
            self.update_picture_box()
            self.status_label.setText(f"Added {len(files)} images. Total: {len(self.selected_files)}")
            
            # Update conversion tab UI if it exists
            if hasattr(self, 'update_conversion_ui'):
                self.update_conversion_ui()

    def prev_image(self):
        """Navigate to the previous image in the selected files list"""
        if self.selected_files and self.current_index > 0:
            self.current_index -= 1
            self.update_picture_box()
    
    def next_image(self):
        """Navigate to the next image in the selected files list"""
        if self.selected_files and self.current_index < len(self.selected_files) - 1:
            self.current_index += 1
            self.update_picture_box()

    def update_picture_box(self):
        """Update the image preview based on the current index"""
        if len(self.selected_files) > 0 and 0 <= self.current_index < len(self.selected_files):
            try:
                # Open the image
                img = Image.open(self.selected_files[self.current_index])
                
                # Apply rotation if stored
                if self.current_index in self.rotations:
                    angle = self.rotations[self.current_index]
                    if angle == 90:
                        img = img.transpose(Image.Transpose.ROTATE_90)
                    elif angle == 180:
                        img = img.transpose(Image.Transpose.ROTATE_180)
                    elif angle == 270:
                        img = img.transpose(Image.Transpose.ROTATE_270)
                
                # Apply zoom factor and resize to fit preview
                img_width, img_height = img.size
                new_width = int(img_width * self.zoom_factor)
                new_height = int(img_height * self.zoom_factor)
                
                # Resize the image maintaining aspect ratio
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert PIL Image to QPixmap for display
                img_data = img.tobytes("raw", "RGB")
                qimage = QImage(img_data, img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                
                self.preview_label.setPixmap(pixmap)
                self.status_label.setText(f"Image {self.current_index + 1} of {len(self.selected_files)}")
                
                # Update listbox selection
                if self.listbox.count() > 0:
                    self.listbox.setCurrentRow(self.current_index)
            except Exception as e:
                logging.error(f"Error in update_picture_box: {str(e)}")
                self.status_label.setText("Error loading image.")
        else:
            self.preview_label.clear()
            self.status_label.setText("No images selected!")

    def rotate_image(self):
        """Rotate the current image 90 degrees clockwise"""
        if len(self.selected_files) == 0:
            self.status_label.setText("No image to rotate!")
            return
        
        if self.current_index in self.rotations:
            self.rotations[self.current_index] = (self.rotations[self.current_index] + 90) % 360
        else:
            self.rotations[self.current_index] = 90
        
        self.update_picture_box()
        self.status_label.setText(f"Rotated image {self.current_index + 1} to {self.rotations[self.current_index]}°")

    def on_listbox_select(self, current_row):
        """Handle the selection of an item in the listbox"""
        if current_row >= 0:
            self.current_index = current_row
            self.update_picture_box()

    def move_up(self):
        """Move the selected image up in the list"""
        current_row = self.listbox.currentRow()
        if current_row > 0:
            # Swap items in list widget
            item_text = self.listbox.item(current_row).text()
            self.listbox.takeItem(current_row)
            self.listbox.insertItem(current_row - 1, item_text)
            
            # Swap selected files
            self.selected_files[current_row], self.selected_files[current_row - 1] = \
                self.selected_files[current_row - 1], self.selected_files[current_row]
            
            # Swap rotations if they exist
            if current_row in self.rotations and current_row - 1 in self.rotations:
                self.rotations[current_row], self.rotations[current_row - 1] = \
                    self.rotations[current_row - 1], self.rotations[current_row]
            elif current_row in self.rotations:
                self.rotations[current_row - 1] = self.rotations.pop(current_row)
            elif current_row - 1 in self.rotations:
                self.rotations[current_row] = self.rotations.pop(current_row - 1)
            
            self.current_index = current_row - 1
            self.listbox.setCurrentRow(self.current_index)
            self.update_picture_box()
            self.status_label.setText(f"Moved image up. Current position: {self.current_index + 1}")
    
    def move_down(self):
        """Move the selected image down in the list"""
        current_row = self.listbox.currentRow()
        if current_row >= 0 and current_row < self.listbox.count() - 1:
            # Swap items in list widget
            item_text = self.listbox.item(current_row).text()
            self.listbox.takeItem(current_row)
            self.listbox.insertItem(current_row + 1, item_text)
            
            # Swap selected files
            self.selected_files[current_row], self.selected_files[current_row + 1] = \
                self.selected_files[current_row + 1], self.selected_files[current_row]
            
            # Swap rotations if they exist
            if current_row in self.rotations and current_row + 1 in self.rotations:
                self.rotations[current_row], self.rotations[current_row + 1] = \
                    self.rotations[current_row + 1], self.rotations[current_row]
            elif current_row in self.rotations:
                self.rotations[current_row + 1] = self.rotations.pop(current_row)
            elif current_row + 1 in self.rotations:
                self.rotations[current_row] = self.rotations.pop(current_row + 1)
            
            self.current_index = current_row + 1
            self.listbox.setCurrentRow(self.current_index)
            self.update_picture_box()
            self.status_label.setText(f"Moved image down. Current position: {self.current_index + 1}")

    def delete_image(self):
        """Delete the selected image from the list"""
        current_row = self.listbox.currentRow()
        if current_row >= 0:
            try:
                # Remove from selected files list
                del self.selected_files[current_row]
                
                # Update rotations dictionary
                if current_row in self.rotations:
                    del self.rotations[current_row]
                
                # Reindex rotations for items after the deleted one
                new_rotations = {}
                for key, value in self.rotations.items():
                    if key > current_row:
                        new_rotations[key - 1] = value
                    elif key < current_row:
                        new_rotations[key] = value
                self.rotations = new_rotations
                
                # Remove from listbox
                self.listbox.takeItem(current_row)
                
                # Update current index
                if self.listbox.count() == 0:
                    self.current_index = -1
                elif current_row >= self.listbox.count():
                    self.current_index = self.listbox.count() - 1
                else:
                    self.current_index = current_row
                
                self.update_picture_box()
                self.status_label.setText(f"Deleted image. Remaining: {len(self.selected_files)}")
                
                # Update conversion tab UI if it exists
                if hasattr(self, 'update_conversion_ui'):
                    self.update_conversion_ui()
            except Exception as e:
                logging.error(f"Error in delete_image: {str(e)}")
                QMessageBox.critical(self, "Error", "Error deleting image. See error.log for details.")
    
    def reset_inputs(self):
        """Reset all inputs and image selections"""
        self.selected_files = []
        self.rotations = {}
        self.current_index = 0
        self.listbox.clear()
        self.update_picture_box()
        self.progress_bar.setValue(0)
        self.status_label.setText("All images and settings have been reset")
        self.zoom_factor = 1.0
        self.latest_pdf = None
        
        # Reset UI elements if they exist
        if hasattr(self, 'btn_preview_pdf'):
            self.btn_preview_pdf.setEnabled(False)
        if hasattr(self, 'btn_print_pdf'):
            self.btn_print_pdf.setEnabled(False)
        if hasattr(self, 'btn_compress'):
            self.btn_compress.setEnabled(False)
        if hasattr(self, 'pdf_info'):
            self.pdf_info.setText("No PDF has been selected or created yet.")
        
        # Update conversion tab UI if it exists
        if hasattr(self, 'update_conversion_ui'):
            self.update_conversion_ui()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming"""
        # Mouse wheel for zooming
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_factor += 0.1
        else:
            self.zoom_factor = max(0.1, self.zoom_factor - 0.1)
        self.update_picture_box()

    def convert_to_pdf(self):
        """Convert selected images to PDF based on current settings"""
        if len(self.selected_files) == 0:
            self.status_label.setText("No images selected!")
            QMessageBox.warning(self, "Warning", "Please select images first before converting.")
            self.tab_widget.setCurrentIndex(0)  # Switch to main tab to select images
            return
        
        margin = self.num_margin.value()
        orientation = self.combo_orient.currentText()
        apply_global_orientation = (orientation == "Landscape")
        
        # Get paper size from dropdown
        paper_size = self.paper_size.currentText()
        
        # Get resolution settings from dropdown if it exists
        dpi = 150  # Default DPI
        quality = 95  # Default quality
        if hasattr(self, 'resolution'):
            resolution_text = self.resolution.currentText()
            if "72" in resolution_text:
                dpi = 72
            elif "300" in resolution_text:
                dpi = 300
            elif "600" in resolution_text:
                dpi = 600
                
        # Get compression settings if they exist
        compression = "JPEG"  # Default compression
        if hasattr(self, 'compression'):
            compression_text = self.compression.currentText()
            if "Maximum Quality" in compression_text:
                compression = "LZW"
                quality = 100
            elif "High Quality" in compression_text:
                compression = "JPEG"
                quality = 95
            elif "Balanced" in compression_text:
                compression = "JPEG"
                quality = 90
            elif "Maximum Compression" in compression_text:
                compression = "JPEG"
                quality = 85
        
        try:
            if self.chk_separate.isChecked():
                # Save as separate PDFs
                folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
                if folder:
                    self.progress_bar.setValue(0)
                    total = len(self.selected_files)
                    count = 0
                    
                    for i, img_file in enumerate(self.selected_files):
                        out_file = os.path.join(folder, os.path.splitext(os.path.basename(img_file))[0] + ".pdf")
                        
                        # Build ImageMagick command
                        rotate_option = f"-rotate {self.rotations[i]}" if i in self.rotations else ""
                        border_option = f"-border {margin} -bordercolor white" if margin > 0 else ""
                        orient_option = "-rotate 90" if apply_global_orientation else ""
                        quality_option = f"-quality {quality}" if quality != 95 else ""
                        density_option = f"-density {dpi}" if dpi != 150 else ""
                        compress_option = f"-compress {compression}" if compression != "JPEG" else ""
                        
                        # Add paper size option
                        page_size_option = f"-page {paper_size}"
                        
                        # Combine options
                        options = " ".join(filter(None, [rotate_option, border_option, orient_option, 
                                                         page_size_option, quality_option, density_option, compress_option]))
                        
                        cmd = f'magick "{img_file}" {options} "{out_file}"'
                        try:
                            self.run_imagemagick(cmd)
                            
                            count += 1
                            self.progress_bar.setValue(math.floor((count / total) * 100))
                            QApplication.processEvents()
                        except Exception as e:
                            # Show error but continue with other files
                            error_message = f"Error processing file {img_file}: {str(e)}"
                            logging.error(error_message)
                            QMessageBox.warning(self, "Processing Error", 
                                f"Error converting {os.path.basename(img_file)}\n{str(e)}\n\nContinuing with remaining files.")
                    
                    self.status_label.setText(f"All {count} images saved as separate PDFs in: {folder}")
                    QMessageBox.information(self, "Success", f"Created {count} PDF files in:\n{folder}")
                    
                    # We don't enable the tools for multiple PDFs
            else:
                # Save as single PDF
                output_pdf, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save PDF As",
                    "",
                    "PDF Files (*.pdf)"
                )
                if output_pdf:
                    self.progress_bar.setValue(0)
                    
                    # Apply formatting options
                    border_option = f"-border {margin} -bordercolor white" if margin > 0 else ""
                    orient_option = "-rotate 90" if apply_global_orientation else ""
                    quality_option = f"-quality {quality}" if quality != 95 else ""
                    density_option = f"-density {dpi}" if dpi != 150 else ""
                    compress_option = f"-compress {compression}" if compression != "JPEG" else ""
                    
                    # Add paper size option
                    page_size_option = f"-page {paper_size}"
                    
                    # Combine global options
                    common_options = " ".join(filter(None, [border_option, orient_option, page_size_option,
                                                           quality_option, density_option, compress_option]))
                    
                    # Build command with individual file options
                    files_with_rotations = []
                    for i, file in enumerate(self.selected_files):
                        # Add rotation if needed
                        file_options = f'"{file}"'
                        if i in self.rotations:
                            file_options = f'"{file}" -rotate {self.rotations[i]}'
                        files_with_rotations.append(file_options)
                    
                    cmd = f'magick {" ".join(files_with_rotations)} {common_options} "{output_pdf}"'
                    self.run_imagemagick(cmd)
                    
                    self.progress_bar.setValue(100)
                    self.status_label.setText(f"PDF created with {len(self.selected_files)} images: {output_pdf}")
                    QMessageBox.information(self, "Success", "PDF conversion complete!")
                    
                    # Store the latest PDF file path and enable preview/print/compress buttons
                    self.latest_pdf = output_pdf
                    
                    # Enable buttons if they exist
                    if hasattr(self, 'btn_preview_pdf'):
                        self.btn_preview_pdf.setEnabled(True)
                    if hasattr(self, 'btn_print_pdf'):
                        self.btn_print_pdf.setEnabled(True)
                    if hasattr(self, 'btn_compress'):
                        self.btn_compress.setEnabled(True)
                    
                    # Update PDF info if it exists
                    if hasattr(self, 'pdf_info'):
                        file_size = os.path.getsize(output_pdf) / 1024  # KB
                        if file_size > 1024:
                            file_size = file_size / 1024  # MB
                            size_str = f"{file_size:.2f} MB"
                        else:
                            size_str = f"{file_size:.2f} KB"
                        
                        self.pdf_info.setText(f"Current PDF: {os.path.basename(output_pdf)}\nSize: {size_str}\nLocation: {os.path.dirname(output_pdf)}")
                    
                    # Switch to Tools tab if it exists
                    if self.tab_widget.count() > 2:
                        self.tab_widget.setCurrentIndex(2)
        except Exception as e:
            logging.error(f"Error in conversion: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error during PDF conversion: {str(e)}\nSee error.log for details.")
            self.progress_bar.setValue(0)

    def setup_tools_tab(self):
        """Setup the Tools Tab - PDF operations (compression, preview, print)"""
        
        # Header label
        self.tools_header = QLabel("Compress PDF")
        self.tools_header.setObjectName("tools_header")
        self.tools_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tools_tab_layout.addWidget(self.tools_header)
        
        # Tools description
        tools_desc = QLabel("Compress your PDF files to reduce their size")
        tools_desc.setStyleSheet("font-size: 10pt; color: #424242; margin-bottom: 10px;")
        tools_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tools_tab_layout.addWidget(tools_desc)
        
        # Create a horizontal layout to hold all three steps side-by-side
        steps_layout = QHBoxLayout()
        steps_layout.setSpacing(15)  # Increased spacing between steps
        
        # Step 1: Select PDF
        select_pdf_panel = QFrame()
        select_pdf_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        select_pdf_panel.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #e0e0e0; padding: 15px;")
        select_pdf_panel.setMinimumHeight(260)  # Consistent panel height
        select_pdf_layout = QVBoxLayout(select_pdf_panel)
        select_pdf_layout.setSpacing(15)  # Increased spacing
        
        select_pdf_header = QLabel("Step 1: Select PDF")
        select_pdf_header.setStyleSheet("font-size: 10pt; font-weight: bold; color: #333333;")
        select_pdf_layout.addWidget(select_pdf_header)
        
        select_pdf_desc = QLabel("Select an existing PDF file to work with")
        select_pdf_desc.setStyleSheet("font-style: italic; color: #424242; font-size: 9pt;")
        select_pdf_desc.setWordWrap(True)
        select_pdf_layout.addWidget(select_pdf_desc)
        
        select_pdf_layout.addStretch(1)  # Add stretch to push button down
        
        self.btn_select_pdf = QPushButton("Select PDF File")
        self.btn_select_pdf.setObjectName("btn_select_pdf")
        self.btn_select_pdf.clicked.connect(self.select_pdf)
        self.btn_select_pdf.setFixedHeight(50)
        self.btn_select_pdf.setStyleSheet("color: white; background-color: #2196f3; font-weight: bold;")
        select_pdf_layout.addWidget(self.btn_select_pdf)
        
        # Add step 1 panel to horizontal layout
        steps_layout.addWidget(select_pdf_panel)
        
        # Step 2: Compress PDF
        compression_panel = QFrame()
        compression_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        compression_panel.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #e0e0e0; padding: 15px;")
        compression_panel.setMinimumHeight(260)  # Consistent panel height
        compression_layout = QVBoxLayout(compression_panel)
        compression_layout.setSpacing(15)  # Increased spacing
        
        compress_header = QLabel("Step 2: Compress PDF")
        compress_header.setStyleSheet("font-size: 10pt; font-weight: bold;padding:0px; color: #333333;")
        compress_header.setFixedHeight(40)
        compression_layout.addWidget(compress_header)
        
        compress_desc = QLabel("Reduce your PDF file size while maintaining reasonable quality.")
        compress_desc.setStyleSheet("font-style: italic; color: #424242; font-size: 9pt;")
        compress_desc.setWordWrap(True)
        compression_layout.addWidget(compress_desc)
        
        # Compression details - Replace static label with options
        compress_options_layout = QVBoxLayout()
        compress_options_label = QLabel("Compression Profile:")
        compress_options_label.setStyleSheet(" padding:4px; ")  
        compress_options_layout.addWidget(compress_options_label)

        self.compression_profile = QComboBox()
        self.compression_profile.addItems(["Maximum Quality (300 DPI, 100%)", 
                                           "High Quality (250 DPI, 95%)", 
                                           "Balanced (200 DPI, 90%)", 
                                           "Maximum Compression (150 DPI, 85%)"])
        # Add a visual indicator that this is a dropdown not icon just symbol using css 
        self.compression_profile.setStyleSheet("""
            QComboBox {
                padding: 4px;
                padding-right: 20px; /* Make room for the arrow */
                border: 1px solid #100101;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 16px;
                border-left: 1px solid #090707;
            }
            QComboBox::down-arrow {
                width: 8px;
                height: 8px;
                background: none;
                border-top: 5px solid #000000;
                border-right: 4px solid transparent;
                border-left: 4px solid transparent;
            }
        """)
        self.compression_profile.setCurrentIndex(1)  # Default to balanced
        compress_options_layout.addWidget(self.compression_profile)

        compression_layout.addLayout(compress_options_layout)
        
        # Compress PDF button
        self.btn_compress = QPushButton("Compress PDF")
        self.btn_compress.setObjectName("btn_compress")
        self.btn_compress.clicked.connect(self.compress_pdf)
        self.btn_compress.setFixedHeight(50)
        self.btn_compress.setStyleSheet("color: white; background-color: #9c27b0; font-weight: bold;")
        self.btn_compress.setEnabled(False)  # Disabled until PDF is created or selected
        compression_layout.addWidget(self.btn_compress)
        
        # Add step 2 panel to horizontal layout
        steps_layout.addWidget(compression_panel)
        
        # Step 3: Use PDF
        actions_panel = QFrame()
        actions_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        actions_panel.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #e0e0e0; padding: 15px;")
        actions_panel.setMinimumHeight(260)  # Consistent panel height
        actions_layout = QVBoxLayout(actions_panel)
        actions_layout.setSpacing(15)  # Increased spacing
        
        actions_header = QLabel("Step 3: Use PDF")
        actions_header.setStyleSheet("font-size: 10pt; font-weight: bold; color: #333333;")
        actions_layout.addWidget(actions_header)
        
        actions_desc = QLabel("View or print your PDF file")
        actions_desc.setStyleSheet("font-style: italic; color: #424242; font-size: 9pt;")
        actions_desc.setWordWrap(True)
        actions_layout.addWidget(actions_desc)
        
        actions_layout.addStretch(1)  # Add stretch to push buttons down
        
        # Actions buttons layout
        pdf_actions = QVBoxLayout()
        pdf_actions.setSpacing(10)  # Increased spacing
        
        # Preview PDF button
        self.btn_preview_pdf = QPushButton("Preview PDF")
        self.btn_preview_pdf.setObjectName("btn_preview_pdf")
        self.btn_preview_pdf.clicked.connect(self.preview_pdf)
        self.btn_preview_pdf.setFixedHeight(50)
        self.btn_preview_pdf.setStyleSheet("color: white; background-color: #03a9f4; font-weight: bold;")
        self.btn_preview_pdf.setEnabled(False)
        pdf_actions.addWidget(self.btn_preview_pdf)
        
        # Print PDF button
        self.btn_print_pdf = QPushButton("Print PDF")
        self.btn_print_pdf.setObjectName("btn_print_pdf")
        self.btn_print_pdf.clicked.connect(self.print_pdf)
        self.btn_print_pdf.setFixedHeight(50)
        self.btn_print_pdf.setStyleSheet("color: white; background-color: #03a9f4; font-weight: bold;")
        self.btn_print_pdf.setEnabled(False)
        pdf_actions.addWidget(self.btn_print_pdf)
        
        actions_layout.addLayout(pdf_actions)
        
        # Add step 3 panel to horizontal layout
        steps_layout.addWidget(actions_panel)
        
        # Add the horizontal steps layout to the main tab layout
        self.tools_tab_layout.addLayout(steps_layout)
        
        # Current PDF info section (spans full width)
        self.pdf_info = QLabel("No PDF has been selected or created yet.")
        self.pdf_info.setStyleSheet("background-color: #f8f8f8; padding: 12px; border-radius: 8px; color: #424242; font-size: 9pt; margin-top: 15px;")
        self.pdf_info.setMinimumHeight(50)
        self.pdf_info.setWordWrap(True)
        self.tools_tab_layout.addWidget(self.pdf_info)
        
        # Add bottom stretch to push everything up
        self.tools_tab_layout.addStretch()

    def setup_merge_tab(self):
        """Setup the Merge PDFs Tab"""
        
        # Header label
        self.merge_header = QLabel("Merge PDFs")
        self.merge_header.setObjectName("merge_header")
        self.merge_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.merge_tab_layout.addWidget(self.merge_header)
        
        # Description
        desc = QLabel("Combine multiple PDF files into a single document")
        desc.setStyleSheet("font-size: 10pt; color: #424242; margin-bottom: 5px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.merge_tab_layout.addWidget(desc)
        
        # Main content with two panels
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)  # Reduce spacing between panels
        
        # Left panel - PDF List with better styling
        list_panel = QFrame()
        list_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        list_panel.setStyleSheet("background-color: white; border-radius: 6px; border: 1px solid #e0e0e0; padding: 8px;")
        list_layout = QVBoxLayout(list_panel)
        list_layout.setContentsMargins(8, 8, 8, 8)  # Reduce margins
        list_layout.setSpacing(5)  # Reduce spacing
        
        # Left panel header
        list_header = QLabel("PDF Files to Merge")
        list_header.setStyleSheet("font-weight: bold; font-size: 11pt; color: #1e88e5; margin-bottom: 5px;")
        list_layout.addWidget(list_header)
        
        # PDF list description
        list_desc = QLabel("Add PDFs in the order you want them combined.")
        list_desc.setStyleSheet("color: #424242; font-style: italic; margin-bottom: 5px;")
        list_desc.setWordWrap(True)
        list_layout.addWidget(list_desc)
        
        # PDF list widget with better styling
        self.pdf_listbox = QListWidget()
        self.pdf_listbox.setMinimumHeight(150)  # Reduce minimum height
        self.pdf_listbox.setStyleSheet("""
            QListWidget {
                border: 1px solid #bbbbbb;
                border-radius: 4px;
                background-color: #f9f9f9;
                padding: 3px;
            }
            QListWidget::item {
                border-bottom: 1px solid #eeeeee;
                padding: 3px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1565c0;
            }
        """)
        list_layout.addWidget(self.pdf_listbox)
        
        # PDF list buttons in a nicer layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        
        # Add PDF button
        self.btn_add_pdf = QPushButton("Add PDF")
        self.btn_add_pdf.setObjectName("btn_add_pdf")
        self.btn_add_pdf.clicked.connect(self.add_pdf)
        self.btn_add_pdf.setStyleSheet("color: white; background-color: #2196f3; font-weight: bold;")
        self.btn_add_pdf.setFixedHeight(28)  # Smaller height
        buttons_layout.addWidget(self.btn_add_pdf)
        
        # Remove PDF button
        self.btn_remove_pdf = QPushButton("Remove PDF")
        self.btn_remove_pdf.setObjectName("btn_remove_pdf")
        self.btn_remove_pdf.clicked.connect(self.remove_pdf)
        self.btn_remove_pdf.setStyleSheet("color: white; background-color: #f44336; font-weight: bold;")
        self.btn_remove_pdf.setFixedHeight(28)  # Smaller height
        buttons_layout.addWidget(self.btn_remove_pdf)
        
        list_layout.addLayout(buttons_layout)
        
        # Reorder section with clearer grouping
        reorder_group = QFrame()
        reorder_group.setStyleSheet("background-color: #f5f5f7; border-radius: 4px; padding: 5px; margin-top: 5px;")
        reorder_layout = QVBoxLayout(reorder_group)
        reorder_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        reorder_layout.setSpacing(3)  # Reduce spacing
        
        reorder_label = QLabel("Reorder PDFs:")
        reorder_label.setStyleSheet("font-weight: bold; color: #424242;")
        reorder_layout.addWidget(reorder_label)
        
        reorder_buttons = QHBoxLayout()
        reorder_buttons.setSpacing(5)  # Reduce spacing
        
        # Move up button
        self.btn_move_pdf_up = QPushButton("Move Up")
        self.btn_move_pdf_up.setObjectName("btn_move_pdf_up")
        self.btn_move_pdf_up.clicked.connect(self.move_pdf_up)
        self.btn_move_pdf_up.setFixedHeight(30)  # Smaller height
        self.btn_move_pdf_up.setStyleSheet("background-color: #607d8b; color: white;")
        reorder_buttons.addWidget(self.btn_move_pdf_up)
        
        # Move down button
        self.btn_move_pdf_down = QPushButton("Move Down")
        self.btn_move_pdf_down.setObjectName("btn_move_pdf_down")
        self.btn_move_pdf_down.clicked.connect(self.move_pdf_down)
        self.btn_move_pdf_down.setFixedHeight(30)  # Smaller height
        self.btn_move_pdf_down.setStyleSheet("background-color: #607d8b; color: white;")
        reorder_buttons.addWidget(self.btn_move_pdf_down)
        
        reorder_layout.addLayout(reorder_buttons)
        list_layout.addWidget(reorder_group)
        
        # Add left panel to content layout
        content_layout.addWidget(list_panel, 3)
        
        # Right panel - Options and actions
        options_panel = QFrame()
        options_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        options_panel.setStyleSheet("background-color: white; border-radius: 6px; border: 1px solid #e0e0e0; padding: 8px;")
        options_layout = QVBoxLayout(options_panel)
        options_layout.setContentsMargins(8, 8, 8, 8)  # Reduce margins
        options_layout.setSpacing(5)  # Reduce spacing
        
        # Right panel header
        options_header = QLabel("Merge Options")
        options_header.setStyleSheet("font-weight: bold; font-size: 11pt; color: #1e88e5; padding:0px; margin-bottom: 5px;")
        options_layout.addWidget(options_header)
        
        # Options group with better styling
        options_group = QFrame()
        options_group.setStyleSheet("background-color: #f5f5f7; border-radius: 4px; padding: 8px;")
        options_inner_layout = QVBoxLayout(options_group)
        options_inner_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        options_inner_layout.setSpacing(3)  # Reduce spacing
        
        # Options header
        options_group_header = QLabel("PDF Settings")
        options_group_header.setStyleSheet("font-weight: bold; color: #424242;")
        options_inner_layout.addWidget(options_group_header)
        
        # Add options with better spacing
        self.chk_add_bookmarks = QCheckBox("Add bookmarks for each file")
        self.chk_add_bookmarks.setChecked(True)
        self.chk_add_bookmarks.setStyleSheet("margin-top: 3px;")
        options_inner_layout.addWidget(self.chk_add_bookmarks)
        
        self.chk_add_page_numbers = QCheckBox("Add page numbers")
        self.chk_add_page_numbers.setStyleSheet("margin-top: 3px;")
        options_inner_layout.addWidget(self.chk_add_page_numbers)
        
        options_layout.addWidget(options_group)
        
        # Summary preview section
        summary_frame = QFrame()
        summary_frame.setStyleSheet("background-color: #e8f5e9; border-radius: 4px; padding: 8px; margin-top: 5px;")
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        summary_layout.setSpacing(3)  # Reduce spacing
        
        summary_header = QLabel("Merge Summary")
        summary_header.setStyleSheet("font-weight: bold; color: #2e7d32;")
        summary_layout.addWidget(summary_header)
        
        self.merge_summary = QLabel("No PDF files selected yet")
        self.merge_summary.setWordWrap(True)
        summary_layout.addWidget(self.merge_summary)
        
        options_layout.addWidget(summary_frame)
        
        # Merge button with more prominence
        self.btn_merge_pdfs = QPushButton("Merge PDFs")
        self.btn_merge_pdfs.setObjectName("btn_merge_pdfs")
        self.btn_merge_pdfs.clicked.connect(self.merge_pdfs)
        self.btn_merge_pdfs.setFixedHeight(40)  # Smaller height
        self.btn_merge_pdfs.setStyleSheet("""
            QPushButton {
                color: white; 
                background-color: #ff9800; 
                font-weight: bold; 
                font-size: 11pt;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:pressed {
                background-color: #ef6c00;
            }
            QPushButton:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
        """)
        self.btn_merge_pdfs.setEnabled(False)
        options_layout.addWidget(self.btn_merge_pdfs)
        
        # Help text with better styling
        help_text = QLabel(
            "Tips:\n"
            "• Add PDFs in order you want them combined\n"
            "• Use Move Up/Down to reorder files\n"
            "• Bookmarks help navigate merged document"
        )
        help_text.setStyleSheet("background-color: #e3f2fd; color: #1565c0; padding: 8px; border-radius: 4px; margin-top: 5px; font-size: 9pt;")
        help_text.setWordWrap(True)
        options_layout.addWidget(help_text)
        
        options_layout.addStretch()
        
        # Add right panel to content layout
        content_layout.addWidget(options_panel, 2)
        
        # Add content layout to tab
        self.merge_tab_layout.addLayout(content_layout)
        
        # Connect signals
        self.pdf_listbox.currentRowChanged.connect(self.update_merge_summary)
        
        # Add bottom stretch to push everything up
        self.merge_tab_layout.addStretch()
    
    def extract_pages(self):
        """Extract pages from the PDF using PyPDF2 with support for complex page ranges"""
        pdf_file = self.split_pdf_path.text()
        page_range = self.page_range_input.text().strip()
        
        if not pdf_file or pdf_file == "No PDF selected":
            QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
            return
        
        if not page_range:
            QMessageBox.warning(self, "Warning", "Please specify the page range to extract.")
            return
        
        # Choose save path
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save Extracted Pages As", "", "PDF Files (*.pdf)"
        )
        
        if not output_file:
            return
            
        try:
            import PyPDF2
            
            self.status_label.setText(f"Extracting pages {page_range}...")
            self.progress_bar.setValue(10)
            
            # Parse page range and extract pages
            success, message = self.extract_pages_with_pypdf2(pdf_file, output_file, page_range)
            
            if success:
                self.progress_bar.setValue(100)
                self.status_label.setText(f"Successfully extracted pages {page_range}")
                QMessageBox.information(self, "Success", f"Successfully extracted pages to {output_file}")
            else:
                self.progress_bar.setValue(0)
                QMessageBox.critical(self, "Error", message)
                
        except Exception as e:
            logging.error(f"Error in page extraction: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error extracting pages: {str(e)}")
            self.progress_bar.setValue(0)
            
    def parse_page_range(self, range_str, max_pages):
        """
        Parse a page range string into a list of page numbers.
        
        Supports formats:
        - Single page: "5"
        - Page range: "1-5"
        - Mixed: "1,3,5-8,10"
        
        Args:
            range_str: String containing page ranges
            max_pages: Maximum number of pages in the PDF
            
        Returns:
            List of page numbers (1-based indexing)
        """
        pages = []
        
        # Handle empty input
        if not range_str.strip():
            return pages
        
        # Split by comma
        parts = range_str.split(',')
        
        for part in parts:
            part = part.strip()
            
            # Skip empty parts
            if not part:
                continue
                
            # Handle range (e.g., "1-5")
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    
                    # Validate range
                    if start < 1:
                        self.status_label.setText(f"Warning: Page number {start} is less than 1, using 1 instead.")
                        start = 1
                        
                    if end > max_pages:
                        self.status_label.setText(f"Warning: Page number {end} exceeds maximum of {max_pages}, using {max_pages} instead.")
                        end = max_pages
                    
                    # Add all pages in the range
                    for page in range(start, end + 1):
                        if page not in pages:
                            pages.append(page)
                except ValueError:
                    QMessageBox.warning(self, "Invalid Range", f"Invalid page range '{part}', skipping.")
                    
            # Handle single page
            else:
                try:
                    page = int(part)
                    
                    # Validate page number
                    if page < 1:
                        self.status_label.setText(f"Warning: Page number {page} is less than 1, using 1 instead.")
                        page = 1
                        
                    if page > max_pages:
                        self.status_label.setText(f"Warning: Page number {page} exceeds maximum of {max_pages}, using {max_pages} instead.")
                        page = max_pages
                    
                    if page not in pages:
                        pages.append(page)
                except ValueError:
                    QMessageBox.warning(self, "Invalid Page", f"Invalid page number '{part}', skipping.")
        
        return sorted(pages)

    def extract_pages_with_pypdf2(self, input_pdf, output_pdf, page_range):
        """
        Extract specified pages from a PDF file
        
        Args:
            input_pdf: Path to input PDF file
            output_pdf: Path to output PDF file
            page_range: String representation of pages to extract (e.g., "1,3,5-8,10")
            
        Returns:
            (success, message) tuple
        """
        try:
            # Import PyPDF2 here to ensure it's available
            import PyPDF2
            
            # Open the input PDF
            with open(input_pdf, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Parse page range
                pages_to_extract = self.parse_page_range(page_range, total_pages)
                
                if not pages_to_extract:
                    return False, "No valid pages specified for extraction."
                
                self.status_label.setText(f"PDF has {total_pages} total pages. Extracting {len(pages_to_extract)} pages...")
                
                # Update progress bar
                self.progress_bar.setValue(20)
                QApplication.processEvents()  # Keep UI responsive
                
                # Create a PDF writer
                pdf_writer = PyPDF2.PdfWriter()
                
                # Add each specified page
                for i, page_num in enumerate(pages_to_extract):
                    # Convert from 1-based to 0-based indexing
                    pdf_writer.add_page(pdf_reader.pages[page_num - 1])
                    
                    # Update progress (from 20% to 80%)
                    progress = 20 + int(60 * (i + 1) / len(pages_to_extract))
                    self.progress_bar.setValue(progress)
                    QApplication.processEvents()  # Keep UI responsive
                
                # Write to the output file
                with open(output_pdf, 'wb') as output:
                    pdf_writer.write(output)
                
                # Final progress update
                self.progress_bar.setValue(100)
                    
                return True, f"Successfully extracted {len(pages_to_extract)} pages to {output_pdf}"
                    
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def select_pdf(self):
        """Select a PDF file for compression or preview"""
        pdf_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF File",
            "",
            "PDF Files (*.pdf)"
        )
        
        if pdf_file and os.path.exists(pdf_file):
            self.latest_pdf = pdf_file
            
            # Enable buttons
            self.btn_compress.setEnabled(True)
            self.btn_preview_pdf.setEnabled(True)
            self.btn_print_pdf.setEnabled(True)
            
            # Update PDF info display
            file_size = os.path.getsize(pdf_file) / 1024  # KB
            if file_size > 1024:
                file_size = file_size / 1024  # MB
                size_str = f"{file_size:.2f} MB"
            else:
                size_str = f"{file_size:.2f} KB"
            
            self.pdf_info.setText(f"Current PDF: {os.path.basename(pdf_file)}\nSize: {size_str}\nLocation: {os.path.dirname(pdf_file)}")
            self.status_label.setText(f"PDF file selected: {os.path.basename(pdf_file)}")
    
    def compress_pdf(self):
        """Compress the current PDF file"""
        if not self.latest_pdf or not os.path.exists(self.latest_pdf):
            QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
            return
        
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Compressed PDF As",
            "",
            "PDF Files (*.pdf)"
        )
        
        if output_file:
            try:
                self.status_label.setText("Compressing PDF...")
                self.progress_bar.setValue(0)
                
                # Get original file size for later comparison
                original_size = os.path.getsize(self.latest_pdf) / 1024  # KB
                
                # Get compression settings from dropdown
                compression_profile = self.compression_profile.currentText()
                
                # First try with direct GhostScript if it's available
                try:
                    gs_path = self.find_ghostscript()
                    if os.path.isfile(gs_path) or "gs" in gs_path:
                        # Use Ghostscript directly for better PDF compression
                        success = self.compress_with_ghostscript(self.latest_pdf, output_file, compression_profile)
                        if success:
                            self.status_label.setText("Compression with Ghostscript completed.")
                        else:
                            raise RuntimeError("Ghostscript compression failed or produced larger file")
                    else:
                        # Fall back to ImageMagick if Ghostscript not found directly
                        self.status_label.setText("Using ImageMagick for compression...")
                        # Set parameters based on profile
                        if "Maximum Quality" in compression_profile:
                            dpi = 300
                            quality = 100
                            compression = "LZW"  # Use lossless compression for max quality
                        elif "High Quality" in compression_profile:
                            dpi = 250
                            quality = 90
                        elif "Balanced" in compression_profile:
                            dpi = 200
                            quality = 85
                        else:  # Maximum Compression
                            dpi = 150
                            quality = 75
                        
                        # Use ImageMagick to compress the PDF
                        cmd = f'magick -density {dpi} "{self.latest_pdf}" -quality {quality}'
                        
                        # Add compression algorithm if specified for maximum quality
                        if "Maximum Quality" in compression_profile:
                            cmd += f' -compress {compression}'
                            
                        cmd += f' "{output_file}"'
                        
                        self.run_imagemagick(cmd)
                        self.status_label.setText("Compression with ImageMagick completed.")
                except Exception as e:
                    self.status_label.setText("External tools failed, falling back to PyPDF2...")
                    logging.warning(f"External compression failed: {str(e)}. Falling back to PyPDF2.")
                    
                    # Fallback to PyPDF2-based compression
                    self.compress_with_pypdf2(self.latest_pdf, output_file, compression_profile)
                    self.status_label.setText("Compression with PyPDF2 completed.")
                
                self.progress_bar.setValue(100)
                
                # Verify the output file was created and compare sizes
                if not os.path.exists(output_file):
                    raise RuntimeError("Output file was not created")
                
                # Compare file sizes
                compressed_size = os.path.getsize(output_file) / 1024  # KB
                
                # If compressed file is larger than original, use the original instead
                if compressed_size > original_size * 1.05:  # Allow 5% increase for edge cases
                    logging.warning(f"Compression increased file size ({compressed_size:.2f}KB > {original_size:.2f}KB). Using PyPDF2 compression.")
                    os.remove(output_file)  # Remove the larger file
                    self.compress_with_pypdf2(self.latest_pdf, output_file, "Maximum Compression")  # Try with maximum compression
                    if os.path.exists(output_file):
                        compressed_size = os.path.getsize(output_file) / 1024  # KB
                        
                        # If still larger, just copy the original
                        if compressed_size > original_size:
                            os.remove(output_file)
                            import shutil
                            shutil.copy2(self.latest_pdf, output_file)
                            compressed_size = original_size
                            QMessageBox.information(self, "Information", "The PDF was already optimally compressed. No further reduction was possible.")
                
                if original_size > 1024:
                    original_str = f"{original_size/1024:.2f} MB"
                else:
                    original_str = f"{original_size:.2f} KB"
                    
                if compressed_size > 1024:
                    compressed_str = f"{compressed_size/1024:.2f} MB"
                else:
                    compressed_str = f"{compressed_size:.2f} KB"
                
                # Calculate reduction percentage
                reduction = ((original_size - compressed_size) / original_size) * 100
                
                # Update the latest PDF reference
                self.latest_pdf = output_file
                
                # Update PDF info
                self.pdf_info.setText(
                    f"Compressed PDF: {os.path.basename(output_file)}\n"
                    f"Original Size: {original_str}\n"
                    f"Compressed Size: {compressed_str}\n"
                    f"Reduction: {reduction:.1f}%"
                )
                
                self.status_label.setText(f"PDF compressed successfully. Size reduced by {reduction:.1f}%")
                
                QMessageBox.information(
                    self, 
                    "Compression Complete", 
                    f"PDF successfully compressed!\n\n"
                    f"Original Size: {original_str}\n"
                    f"Compressed Size: {compressed_str}\n"
                    f"Reduction: {reduction:.1f}%"
                )
                
            except Exception as e:
                logging.error(f"Error in PDF compression: {str(e)}")
                QMessageBox.critical(self, "Error", f"Error compressing PDF: {str(e)}\nSee error.log for details.")
                self.progress_bar.setValue(0)

    def compress_with_ghostscript(self, input_pdf, output_pdf, compression_profile):
        """Compress PDF using Ghostscript directly with optimized settings"""
        try:
            gs_path = self.find_ghostscript()
            logging.info(f"Compressing with Ghostscript at {gs_path}")
            
            # Set compression parameters based on profile
            if "Maximum Quality" in compression_profile:
                preset = "prepress"    # Prepress quality (high resolution)
                dpi = "300"
            elif "High Quality" in compression_profile:
                preset = "printer"     # High quality printing
                dpi = "200"
            elif "Balanced" in compression_profile:
                preset = "ebook"       # Medium quality - good compromise
                dpi = "150"
            else:  # Maximum Compression
                preset = "screen"      # Lowest quality - screen viewing
                dpi = "96"
            
            # Build the Ghostscript command
            cmd = f'"{gs_path}" -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 '
            cmd += f'-dPDFSETTINGS=/{preset} -dNOPAUSE -dQUIET -dBATCH '
            cmd += f'-dDownsampleColorImages=true -dColorImageResolution={dpi} '
            cmd += f'-dDownsampleGrayImages=true -dGrayImageResolution={dpi} '
            cmd += f'-dDownsampleMonoImages=true -dMonoImageResolution={dpi} '
            cmd += f'-sOutputFile="{output_pdf}" "{input_pdf}"'
            
            # Run the command
            logging.info(f"Executing Ghostscript command: {cmd}")
            self.progress_bar.setValue(20)
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            self.progress_bar.setValue(90)
            
            # Check if output file exists and is smaller
            if os.path.exists(output_pdf):
                original_size = os.path.getsize(input_pdf)
                new_size = os.path.getsize(output_pdf)
                
                if new_size < original_size:
                    return True
                else:
                    logging.warning(f"Ghostscript compression did not reduce file size ({new_size} > {original_size})")
                    return False
            else:
                logging.error("Ghostscript did not create output file")
                return False
                
        except Exception as e:
            logging.error(f"Ghostscript compression error: {str(e)}")
            raise RuntimeError(f"Error during Ghostscript compression: {str(e)}")
                
    def compress_with_pypdf2(self, input_pdf, output_pdf, compression_profile):
        """Compress PDF using PyPDF2 without requiring external tools"""
        try:
            import PyPDF2
            import io
            from PIL import Image
            
            self.progress_bar.setValue(10)
            self.status_label.setText("Reading PDF...")
            QApplication.processEvents()
            
            # Open the PDF
            reader = PyPDF2.PdfReader(input_pdf)
            writer = PyPDF2.PdfWriter()
            
            # Determine image quality based on compression profile
            if "Maximum Quality" in compression_profile:
                image_quality = 95
            elif "High Quality" in compression_profile:
                image_quality = 85  
            elif "Balanced" in compression_profile:
                image_quality = 65
            else:  # Maximum Compression
                image_quality = 50
            
            total_pages = len(reader.pages)
            
            # Process each page
            for i, page in enumerate(reader.pages):
                # Add each page to the writer
                writer.add_page(page)
                
                # Update progress
                progress = 10 + int(80 * (i + 1) / total_pages)
                self.progress_bar.setValue(progress)
                self.status_label.setText(f"Processing page {i+1}/{total_pages}...")
                QApplication.processEvents()
            
            # Set PDF version and compression options
            writer.remove_images = False  # Keep images but compress them
            writer._compress = True  # Enable compression
            
            # Write the output file
            self.status_label.setText("Writing compressed PDF...")
            self.progress_bar.setValue(90)
            QApplication.processEvents()
            
            with open(output_pdf, "wb") as f:
                writer.write(f)
                
            self.progress_bar.setValue(100)
            
        except ImportError:
            QMessageBox.critical(self, "Error", "PyPDF2 or PIL module is not installed. Please install it using 'pip install PyPDF2 Pillow'")
            raise
        except Exception as e:
            raise RuntimeError(f"PyPDF2 compression failed: {str(e)}")
    
    def preview_pdf(self):
        """Preview the current PDF file using system's default PDF viewer"""
        if not self.latest_pdf or not os.path.exists(self.latest_pdf):
            QMessageBox.warning(self, "Warning", "Please select or create a PDF file first.")
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(self.latest_pdf)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', self.latest_pdf])
            else:  # Linux
                subprocess.run(['xdg-open', self.latest_pdf])
            
            self.status_label.setText(f"Opening {os.path.basename(self.latest_pdf)} in default PDF viewer")
            
        except Exception as e:
            logging.error(f"Error previewing PDF: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error opening PDF: {str(e)}\nSee error.log for details.")
    
    def print_pdf(self):
        """Print the current PDF file using system's default print dialog"""
        if not self.latest_pdf or not os.path.exists(self.latest_pdf):
            QMessageBox.warning(self, "Warning", "Please select or create a PDF file first.")
            return
        
        try:
            self.status_label.setText(f"Printing {os.path.basename(self.latest_pdf)}")
            
            if sys.platform == 'win32':
                # Windows printing using default application
                os.system(f'start /min "" "print" "{self.latest_pdf}"')
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['lpr', self.latest_pdf])
            else:  # Linux
                subprocess.run(['lpr', self.latest_pdf])
            
            self.status_label.setText(f"Sent {os.path.basename(self.latest_pdf)} to printer")
            
        except Exception as e:
            logging.error(f"Error printing PDF: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error printing PDF: {str(e)}\nSee error.log for details.")

    def _app_base(self):
        """Return the base directory of the application, whether it's running as a script or a frozen executable."""
        if getattr(sys, 'frozen', False):
            # We're running in a frozen/compiled environment
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller bundle
                return sys._MEIPASS
            else:
                # cx_Freeze build or other frozen app
                return os.path.dirname(sys.executable)
        else:
            # Running as script
            return os.path.abspath(os.path.dirname(__file__))
        
    def find_imagick(self):
        """
        Locate the portable ImageMagick exe, or fallback to 'magick'.
        Returns the path to the executable.
        """
        # Try all possible locations for ImageMagick
        possible_paths = []
        
        # Get the base directory
        base = self._app_base()
        
        # Add possible paths for frozen/PyInstaller environment
        if getattr(sys, "frozen", False):
            # 1. Try in the same directory as the executable
            possible_paths.extend([
                os.path.join(base, "imagick_portable_64", "magick.exe"),
                os.path.join(base, "magick.exe"),
            ])
            
            # 2. Try in various relative paths from executable
            for rel_path in [".", "..", "../..", "../../.."]:
                possible_paths.append(os.path.join(base, rel_path, "imagick_portable_64", "magick.exe"))
        else:
            # Running as script - try various relative paths
            for rel_path in [".", "..", "../.."]:
                possible_paths.append(os.path.join(base, rel_path, "imagick_portable_64", "magick.exe"))
        
        # Also look in APPDATA directories which is where it might be extracted by the installer
        appdata = os.environ.get('APPDATA', '')
        localappdata = os.environ.get('LOCALAPPDATA', '')
        programfiles = os.environ.get('PROGRAMFILES', '')
        
        if appdata:
            possible_paths.append(os.path.join(appdata, "PDF Manager", "imagick_portable_64", "magick.exe"))
        if localappdata:
            possible_paths.append(os.path.join(localappdata, "PDF Manager", "imagick_portable_64", "magick.exe"))
        if programfiles:
            possible_paths.append(os.path.join(programfiles, "PDF Manager", "imagick_portable_64", "magick.exe"))
        
        # Log the search process
        logging.info(f"Searching for ImageMagick executable in {len(possible_paths)} possible locations")
        for i, path in enumerate(possible_paths):
            logging.info(f"Location #{i+1}: {path}")
            if os.path.isfile(path):
                logging.info(f"✓ Found ImageMagick at: {path}")
                return path
            else:
                logging.info(f"✗ Not found at: {path}")
                
        # If we get here, check if there's any magick.exe in the application directory
        # This is to handle PyInstaller bundling situation
        if getattr(sys, "frozen", False):
            for root, dirs, files in os.walk(base):
                for file in files:
                    if file.lower() == "magick.exe":
                        full_path = os.path.join(root, file)
                        logging.info(f"✓ Found ImageMagick by directory scan at: {full_path}")
                        return full_path
        
        # Last resort - try system "magick" command
        logging.warning("⚠ ImageMagick not found in any expected location, defaulting to system 'magick'")
        return "magick"

    def run_imagemagick(self, cmd):
        """Run an ImageMagick command with the portable executable if available."""
        magick_path = self.find_imagick()
        
        # Find Ghostscript path for ImageMagick
        gs_path = self.find_ghostscript()
        logging.info(f"Using Ghostscript at: {gs_path}")
        
        # Replace 'magick' with the full path to the portable executable
        if 'magick -' in cmd:
            invocation = cmd.replace('magick -', f'"{magick_path}" -', 1)
        elif cmd.startswith('magick '):
            invocation = cmd.replace('magick ', f'"{magick_path}" ', 1)
        else:
            invocation = cmd
        
        logging.info(f"Executing ImageMagick: {invocation}")
        
        try:
            # Set environment variables so ImageMagick can find Ghostscript
            env = os.environ.copy()
            env['MAGICK_GHOSTSCRIPT_PATH'] = os.path.dirname(gs_path)
            
            result = subprocess.run(
                invocation, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                env=env
            )
            return result
        except subprocess.CalledProcessError as e:
            stderr = e.stderr if hasattr(e, 'stderr') else ""
            logging.error(f"ImageMagick failed ({e.returncode}): {stderr}")
            
            # Check for common error patterns
            if "FailedToExecuteCommand `\"gswin64c.exe\"" in stderr or "PDFDelegateFailed" in stderr:
                raise RuntimeError(
                    "Ghostscript is required but not found. Either install Ghostscript or use PyPDF2 as a fallback."
                )
            elif "not recognized" in str(stderr).lower():
                raise RuntimeError(
                    f"ImageMagick not found. Please place 'imagick_portable...' next to the app."
                )
            
            # Generic error
            raise RuntimeError(f"ImageMagick error: {stderr}")
    def find_ghostscript(self):
        """Locate the portable Ghostscript gswin64c.exe, or fallback to 'gswin64c'."""
        # Try all possible locations for Ghostscript
        possible_paths = []
        
        # Get the base directory
        base = self._app_base()
        
        # Define executable names to look for
        gs_executables = ["gswin64c.exe", "gswin32c.exe", "gs.exe"]
        
        # Add possible paths for frozen/PyInstaller environment
        if getattr(sys, "frozen", False):
            # 1. Try in the application directory structure
            for exe in gs_executables:
                possible_paths.append(os.path.join(base, "ghostscript_portable", "bin", exe))
                possible_paths.append(os.path.join(base, exe))
            
            # 2. Try in various relative paths from executable
            for rel_path in [".", "..", "../..", "../../.."]:
                for exe in gs_executables:
                    possible_paths.append(os.path.join(base, rel_path, "ghostscript_portable", "bin", exe))
        else:
            # Running as script - try various relative paths
            for rel_path in [".", "..", "../.."]:
                for exe in gs_executables:
                    possible_paths.append(os.path.join(base, rel_path, "ghostscript_portable", "bin", exe))
        
        # Also look in APPDATA directories which is where it might be extracted by the installer
        appdata = os.environ.get('APPDATA', '')
        localappdata = os.environ.get('LOCALAPPDATA', '')
        programfiles = os.environ.get('PROGRAMFILES', '')
        
        if appdata:
            for exe in gs_executables:
                possible_paths.append(os.path.join(appdata, "PDF Manager", "ghostscript_portable", "bin", exe))
        if localappdata:
            for exe in gs_executables:
                possible_paths.append(os.path.join(localappdata, "PDF Manager", "ghostscript_portable", "bin", exe))
        if programfiles:
            for exe in gs_executables:
                possible_paths.append(os.path.join(programfiles, "PDF Manager", "ghostscript_portable", "bin", exe))
                possible_paths.append(os.path.join(programfiles, "gs", "bin", exe))
                possible_paths.append(os.path.join(programfiles, "ghostscript", "bin", exe))
        
        # Log the search process
        logging.info(f"Searching for Ghostscript executable in {len(possible_paths)} possible locations")
        for i, path in enumerate(possible_paths):
            logging.info(f"Location #{i+1}: {path}")
            if os.path.isfile(path):
                logging.info(f"✓ Found Ghostscript at: {path}")
                return path
            else:
                logging.info(f"✗ Not found at: {path}")
                
        # If we get here, check if there's any gswin*.exe in the application directory
        # This is to handle PyInstaller bundling situation
        if getattr(sys, "frozen", False):
            for root, dirs, files in os.walk(base):
                for file in files:
                    if any(file.lower().startswith(name.lower()) for name in ["gswin64c", "gswin32c", "gs"]) and file.lower().endswith(".exe"):
                        full_path = os.path.join(root, file)
                        logging.info(f"✓ Found Ghostscript by directory scan at: {full_path}")
                        return full_path
        
        # Last resort - try system executable
        logging.warning("⚠ Ghostscript not found in any expected location, defaulting to system 'gswin64c'")
        return "gswin64c"
    def run_ghostscript(self, cmd):
        """
        Run a Ghostscript command, replacing the bare 'gswin64c' with the portable
        executable if found.
        """
        gs_path = self.find_ghostscript()
        invocation = cmd.replace("gswin64c", f'"{gs_path}"', 1)
        logging.info(f"Executing Ghostscript: {invocation}")
        try:
            result = subprocess.run(
                invocation, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            stderr = e.stderr if hasattr(e, 'stderr') else ""
            logging.error(f"Ghostscript failed ({e.returncode}): {stderr}")
            if "not recognized" in str(stderr).lower():
                raise RuntimeError(
                    f"Ghostscript not found. Please place 'ghostscript_portable...' next to the app."
                )
            raise RuntimeError(f"Ghostscript error: {stderr}")
    def _find_ghostscript_exe(self):
            """
            Return the full path to the bundled Ghostscript executable.
            Looks in <base>/ghostscript_portable/bin/{gswin64c.exe, gswin32c.exe, gs.exe}.
            Falls back to system gswin64c if nothing bundled.
            """
            if getattr(sys, "frozen", False):
                base = os.path.dirname(sys.executable)
            else:
                base = os.path.dirname(os.path.abspath(__file__))

            gs_folder = os.path.join(base, "ghostscript_portable", "bin")
            for name in ("gswin64c.exe", "gswin32c.exe", "gs.exe"):
                candidate = os.path.join(gs_folder, name)
                if os.path.isfile(candidate):
                    return candidate

            # no bundled copy found → rely on system installation
            return "gswin64c"

        # -------------------------------------------------------------------------
    def merge_pdfs(self):
        """Merge PDFs in the list using PyPDF2."""
        if self.pdf_listbox.count() < 2:
            QMessageBox.warning(self, "Warning", "Please add at least two PDF files to merge.")
            return

        output_pdf, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF As",
            "",
            "PDF Files (*.pdf)"
        )
        if not output_pdf:
            return

        try:
            self.status_label.setText("Merging PDFs...")
            self.progress_bar.setValue(0)

            # Collect files
            pdf_files = [self.pdf_listbox.item(i).text()
                          for i in range(self.pdf_listbox.count())]
            
            # Import PyPDF2 here to ensure it's available
            import PyPDF2
            
            # Create a PDF merger object
            pdf_merger = PyPDF2.PdfMerger()
            
            total_files = len(pdf_files)
            for i, pdf in enumerate(pdf_files):
                # Ensure the file exists
                if not os.path.exists(pdf):
                    QMessageBox.warning(self, "File Not Found", f"The file '{pdf}' does not exist.")
                    continue
                    
                # Add PDF with a bookmark if requested
                if self.chk_add_bookmarks.isChecked():
                    bookmark_name = os.path.basename(pdf)  # Use filename as bookmark
                    pdf_merger.append(pdf, outline_item=bookmark_name)
                else:
                    pdf_merger.append(pdf)
                
                # Update progress
                progress = int(((i + 1) / total_files) * 90)  # Reserve last 10% for writing
                self.progress_bar.setValue(progress)
                self.status_label.setText(f"Merging PDF {i+1}/{total_files}")
                QApplication.processEvents()  # Keep UI responsive
            
            # Write the merged PDF to output file
            with open(output_pdf, 'wb') as f:
                pdf_merger.write(f)
            
            self.progress_bar.setValue(100)
            self.status_label.setText(f"Successfully merged {total_files} PDFs")
            
            QMessageBox.information(self, "Success", f"PDFs merged into:\n{output_pdf}")
            self.latest_pdf = output_pdf

            # Re-enable any tool buttons
            if hasattr(self, 'btn_preview_pdf'):
                self.btn_preview_pdf.setEnabled(True)
            if hasattr(self, 'btn_print_pdf'):
                self.btn_print_pdf.setEnabled(True)
            if hasattr(self, 'btn_compress'):
                self.btn_compress.setEnabled(True)
            
            # Update PDF info if it exists
            if hasattr(self, 'pdf_info'):
                file_size = os.path.getsize(output_pdf) / 1024  # KB
                if file_size > 1024:
                    file_size = file_size / 1024  # MB
                    size_str = f"{file_size:.2f} MB"
                else:
                    size_str = f"{file_size:.2f} KB"
                
                self.pdf_info.setText(f"Current PDF: {os.path.basename(output_pdf)}\nSize: {size_str}\nLocation: {os.path.dirname(output_pdf)}")
                
        except Exception as e:
            logging.error(f"Error in PDF merge: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error merging PDFs: {str(e)}\nSee error.log for details.")
            self.progress_bar.setValue(0)
    def select_pdf_to_split(self):
        """Select a PDF file to split"""
        pdf_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF to Split",
            "",
            "PDF Files (*.pdf)"
        )
        
        if pdf_file and os.path.exists(pdf_file):
            self.split_pdf_path.setText(pdf_file)
            self.btn_extract_pages.setEnabled(True)
            
            # Get file size information
            file_size = os.path.getsize(pdf_file) / 1024  # KB
            if file_size > 1024:
                file_size = file_size / 1024  # MB
                size_str = f"{file_size:.2f} MB"
            else:
                size_str = f"{file_size:.2f} KB"
            
            # Try to get page count using our improved method
            try:
                page_count = self.count_pages(pdf_file)
                self.split_pdf_info.setText(f"PDF Information: {os.path.basename(pdf_file)}\nPages: {page_count}\nSize: {size_str}")
            except Exception as e:
                logging.error(f"Failed to count pages: {str(e)}")
                self.split_pdf_info.setText(f"PDF Information: {os.path.basename(pdf_file)}\nPages: Unknown\nSize: {size_str}")
                QMessageBox.warning(self, "Warning", f"Could not determine page count: {str(e)}\n\nYou can still extract pages, but you'll need to know the total number of pages in the document.")
    def count_pages(self, pdf_file):
        """Count the number of pages in a PDF file using multiple methods with fallbacks"""
        # First try using PyPDF2 as it's the most reliable
        try:
            import PyPDF2
            with open(pdf_file, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                page_count = len(pdf_reader.pages)
                logging.info(f"Counted {page_count} pages using PyPDF2")
                return page_count
        except Exception as pypdf_error:
            logging.warning(f"Error counting pages with PyPDF2: {str(pypdf_error)}")
            
        # Then try ImageMagick
        try:
            cmd = f'magick identify -format "%n\n" "{pdf_file}"'
            result = self.run_imagemagick(cmd)
            
            # Try to parse the output - should be just a number
            if result.stdout.strip():
                try:
                    page_count = int(result.stdout.strip())
                    logging.info(f"Counted {page_count} pages using ImageMagick format method")
                    return page_count
                except ValueError:
                    pass
            
            # If that fails, try counting .pdf[ in the output
            cmd = f'magick identify "{pdf_file}"'
            result = self.run_imagemagick(cmd)
            page_count = result.stdout.count(".pdf[")
            
            # If that also fails, count the number of lines in the output
            if page_count == 0:
                page_count = len(result.stdout.strip().split('\n'))
                
            if page_count > 0:
                logging.info(f"Counted {page_count} pages using ImageMagick")
                return page_count
        except Exception as im_error:
            logging.warning(f"Error counting pages with ImageMagick: {str(im_error)}")
        
        # Finally try Ghostscript
        try:
            # Get page count using Ghostscript
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                tmp_path = tmp.name
                
            cmd = f'gswin64c -q -dNODISPLAY -c "({pdf_file}) (r) file runpdfbegin pdfpagecount = quit"'
            result = self.run_ghostscript(cmd)
            
            if result.stdout.strip():
                try:
                    page_count = int(result.stdout.strip())
                    logging.info(f"Counted {page_count} pages using Ghostscript")
                    return page_count
                except ValueError:
                    pass
        except Exception as gs_error:
            logging.warning(f"Error counting pages with Ghostscript: {str(gs_error)}")
            
        # If all methods fail, raise an exception
        logging.error("All page counting methods failed")
        raise RuntimeError("Could not determine page count in PDF file using any available method")
    def setup_split_tab(self):
        """Setup the Split PDF Tab"""
        
        # Header label
        self.split_header = QLabel("Split PDF")
        self.split_header.setObjectName("split_header")
        self.split_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.split_tab_layout.addWidget(self.split_header)
        
        # Description
        desc = QLabel("Extract pages from your PDF files")
        desc.setStyleSheet("font-size: 10pt; color: #424242; margin-bottom: 5px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.split_tab_layout.addWidget(desc)
        
        # Main content with panels
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)  # Reduce spacing between panels
        
        # Left panel - PDF selection and preview
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        left_panel.setStyleSheet("background-color: white; border-radius: 6px; border: 1px solid #e0e0e0; padding: 8px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)  # Reduce margins
        left_layout.setSpacing(5)  # Reduce spacing
        
        # Left panel header
        left_header = QLabel("Select PDF")
        left_header.setStyleSheet("font-weight: bold; font-size: 11pt; color: #1e88e5; margin-bottom: 5px;")
        left_layout.addWidget(left_header)
        
        # PDF selection area with better styling
        pdf_selection = QHBoxLayout()
        pdf_selection.setSpacing(5)
        
        # File selection label and button
        self.split_pdf_path = QLabel("No PDF selected")
        self.split_pdf_path.setStyleSheet("""
            background-color: #f5f5f7; 
            padding: 5px; 
            border: 1px solid #bbbbbb; 
            border-radius: 4px;
            color: #555555;
            font-size: 9pt;
        """)
        self.split_pdf_path.setMinimumWidth(150)  # Reduce width
        self.split_pdf_path.setWordWrap(True)
        pdf_selection.addWidget(self.split_pdf_path, 1)
        
        self.btn_select_pdf_to_split = QPushButton("Select PDF")
        self.btn_select_pdf_to_split.setObjectName("btn_select_pdf_to_split")
        self.btn_select_pdf_to_split.clicked.connect(self.select_pdf_to_split)
        self.btn_select_pdf_to_split.setStyleSheet("color: white; background-color: #2196f3; font-weight: bold;")
        self.btn_select_pdf_to_split.setFixedHeight(28)  # Smaller height
        self.btn_select_pdf_to_split.setMinimumWidth(80)  # Reduce width
        pdf_selection.addWidget(self.btn_select_pdf_to_split)
        
        left_layout.addLayout(pdf_selection)
        
        # PDF info with better styling
        self.split_pdf_info = QLabel("PDF Information: No PDF selected")
        self.split_pdf_info.setStyleSheet("""
            background-color: #e3f2fd; 
            padding: 8px; 
            border-radius: 4px; 
            margin: 5px 0; 
            color: #1565c0;
            font-size: 9pt;
        """)
        self.split_pdf_info.setMinimumHeight(60)  # Reduce height
        self.split_pdf_info.setWordWrap(True)
        left_layout.addWidget(self.split_pdf_info)
        
        # PDF preview placeholder (future enhancement)
        preview_frame = QFrame()
        preview_frame.setStyleSheet("background-color: #f5f5f7; border-radius: 4px; padding: 5px;")
        preview_frame.setMinimumHeight(100)  # Reduce height
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        preview_layout.setSpacing(3)  # Reduce spacing
        
        preview_header = QLabel("Preview")
        preview_header.setStyleSheet("font-weight: bold; color: #424242;")
        preview_layout.addWidget(preview_header)
        
        preview_text = QLabel("PDF preview will be shown in future versions")
        preview_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_text.setStyleSheet("color: #757575; font-style: italic; font-size: 9pt;")
        preview_layout.addWidget(preview_text)
        
        left_layout.addWidget(preview_frame)
        
        # Add stretch to push everything up
        left_layout.addStretch()
        
        # Right panel - Extraction options
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        right_panel.setStyleSheet("background-color: white; border-radius: 6px; border: 1px solid #e0e0e0; padding: 8px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)  # Reduce margins
        right_layout.setSpacing(5)  # Reduce spacing
        
        # Right panel header
        right_header = QLabel("Extraction Options")
        right_header.setStyleSheet("font-weight: bold; font-size: 11pt; color: #1e88e5; padding:0px; margin-bottom: 5px;")
        right_layout.addWidget(right_header)
        
        # Create extract_options layout
        extract_options = QVBoxLayout()
        right_layout.addLayout(extract_options)
        
        # Page range section with better styling
        page_range_group = QFrame()
        page_range_group.setStyleSheet("background-color: #f5f5f7; border-radius: 4px; padding: 2px;")
        page_range_layout = QVBoxLayout(page_range_group)
        page_range_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        page_range_layout.setSpacing(3)  # Reduce spacing
        
        page_range_header = QLabel("Page Range")
        page_range_header.setStyleSheet("font-weight: bold; color: #424242;")
        page_range_layout.addWidget(page_range_header)
        
        # Instructions with better formatting
        instructions = QLabel("Specify pages to extract:")
        instructions.setStyleSheet("color: #424242; margin-top: 3px;padding:0px; font-size: 9pt;")
        instructions.setWordWrap(True)
        page_range_layout.addWidget(instructions)
        
        # Page range input with better guidance
        page_range_input_layout = QHBoxLayout()
        
        # Create help label with more detailed instructions
        page_range_help = QLabel(
            "Enter page numbers or ranges to extract:\n"
            "• Single page: \"5\"\n"
            "• Page range: \"1-5\"\n"
            "• Mixed selection: \"1,3,5-8,10\""
        )
        page_range_help.setStyleSheet("background-color: #e3f2fd; color: #1565c0; padding: 3px; border-radius: 4px; margin-top: 5px;")
        page_range_help.setWordWrap(True)
        page_range_layout.addWidget(page_range_help)
        
        page_range_input_layout.addWidget(QLabel("Pages to extract:"))
        self.page_range_input = QLineEdit()
        self.page_range_input.setPlaceholderText("e.g., 1,3,5-8,10")
        page_range_input_layout.addWidget(self.page_range_input)
        
        page_range_layout.addLayout(page_range_input_layout)
        
        
        # Quick selection buttons with better styling
        quick_buttons_label = QLabel("Quick Selection:")
        quick_buttons_label.setStyleSheet("font-weight: bold; margin-top: 3px; font-size: 9pt;")
        page_range_layout.addWidget(quick_buttons_label)
        
        quick_buttons = QHBoxLayout()
        quick_buttons.setSpacing(5)
        
        all_pages_btn = QPushButton("All")
        all_pages_btn.clicked.connect(lambda: self.set_page_range("all"))
        all_pages_btn.setStyleSheet("""
            background-color: #03a9f4; 
            color: white; 
            font-weight: bold;
            border-radius: 3px;
            padding: 3px;
            font-size: 9pt;
        """)
        all_pages_btn.setFixedHeight(24)  # Smaller height
        quick_buttons.addWidget(all_pages_btn)
        
        even_pages_btn = QPushButton("Even")
        even_pages_btn.clicked.connect(lambda: self.set_page_range("even"))
        even_pages_btn.setStyleSheet("""
            background-color: #03a9f4; 
            color: white; 
            font-weight: bold;
            border-radius: 3px;
            padding: 3px;
            font-size: 9pt;
        """)
        even_pages_btn.setFixedHeight(24)  # Smaller height
        quick_buttons.addWidget(even_pages_btn)
        
        odd_pages_btn = QPushButton("Odd")
        odd_pages_btn.clicked.connect(lambda: self.set_page_range("odd"))
        odd_pages_btn.setStyleSheet("""
            background-color: #03a9f4; 
            color: white; 
            font-weight: bold;
            border-radius: 3px;
            padding: 3px;
            font-size: 9pt;
        """)
        odd_pages_btn.setFixedHeight(24)  # Smaller height
        quick_buttons.addWidget(odd_pages_btn)
        
        page_range_layout.addLayout(quick_buttons)
        
        right_layout.addWidget(page_range_group)
        
        # Output options with better styling
        output_group = QFrame()
        output_group.setStyleSheet("background-color: #f5f5f7; border-radius: 2px; padding: 2px; margin-top: 5px;")
        output_layout = QVBoxLayout(output_group)
        output_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        output_layout.setSpacing(3)  # Reduce spacing
        
        output_header = QLabel("Output Options")
        output_header.setStyleSheet("font-weight: bold; padding:0px; color: #424242;")
        output_layout.addWidget(output_header)
        
        # Output radio buttons with better styling
        self.single_output_file = QRadioButton("Extract to a single PDF file")
        self.single_output_file.setChecked(True)
        self.single_output_file.setStyleSheet("margin-top: 3px; font-size: 9pt;")
        output_layout.addWidget(self.single_output_file)
        
        self.multiple_output_files = QRadioButton("Extract each page to a separate PDF")
        self.multiple_output_files.setStyleSheet("margin-top: 3px; font-size: 9pt;")
        output_layout.addWidget(self.multiple_output_files)
        
        right_layout.addWidget(output_group)
        
        # Extract button with better styling
        self.btn_extract_pages = QPushButton("Extract Pages")
        self.btn_extract_pages.setObjectName("btn_extract_pages")
        self.btn_extract_pages.clicked.connect(self.extract_pages)
        self.btn_extract_pages.setFixedHeight(32)  # Smaller height
        self.btn_extract_pages.setStyleSheet("""
            QPushButton {
                color: white; 
                background-color: #4caf50; 
                font-weight: bold; 
                font-size: 10pt;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
            QPushButton:disabled {
                background-color: #bdbdbd;
                color: #757575;
            }
        """)
        self.btn_extract_pages.setEnabled(False)
        right_layout.addWidget(self.btn_extract_pages)
        
        # Help tip - more compact 
        help_tip = QLabel("Page numbers start at 1. Page '2' will extract the second page.")
        help_tip.setStyleSheet("background-color: #fff3e0; color: #e65100; padding: 5px; border-radius: 4px; margin-top: 5px; font-size: 9pt;")
        help_tip.setWordWrap(True)
        right_layout.addWidget(help_tip)
        
        # Add stretch to push everything up
        right_layout.addStretch()
        
        # Add panels to content layout
        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(right_panel, 1)
        
        # Add content layout to tab
        self.split_tab_layout.addLayout(content_layout)
        
        # Add bottom stretch to push everything up
        self.split_tab_layout.addStretch()
    def set_page_range(self, range_type):
        """Set page range selection based on quick options"""
        pdf_file = self.split_pdf_path.text()
        
        if not pdf_file or pdf_file == "No PDF selected":
            QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
            return
        
        try:
            # Import PyPDF2 here to ensure it's available
            import PyPDF2
            
            # Get total pages
            with open(pdf_file, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                total_pages = len(pdf_reader.pages)
            
            # Set range based on type
            if range_type == "all":
                self.page_range_input.setText(f"1-{total_pages}")
            elif range_type == "even":
                even_pages = ",".join(str(i) for i in range(2, total_pages + 1, 2))
                self.page_range_input.setText(even_pages)
            elif range_type == "odd":
                odd_pages = ",".join(str(i) for i in range(1, total_pages + 1, 2))
                self.page_range_input.setText(odd_pages)
            
            self.status_label.setText(f"Set page range to {self.page_range_input.text()}")
            
        except Exception as e:
            logging.error(f"Error setting page range: {str(e)}")
            QMessageBox.warning(self, "Error", f"Could not set page range: {str(e)}")

    def extract_single_page_with_pypdf2(self, input_pdf, output_pdf, page_number):
        """Extract a single page from a PDF file using PyPDF2"""
        try:
            # Import PyPDF2
            import PyPDF2
            
            # Open the input PDF
            with open(input_pdf, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Make sure the page number is valid
                if page_number < 1 or page_number > len(pdf_reader.pages):
                    return False, f"Page number {page_number} is out of range. The PDF has {len(pdf_reader.pages)} pages."
                
                # Create a PDF writer
                pdf_writer = PyPDF2.PdfWriter()
                
                # Add the requested page (convert from 1-based to 0-based indexing)
                pdf_writer.add_page(pdf_reader.pages[page_number - 1])
                
                # Write to the output file
                with open(output_pdf, 'wb') as output:
                    pdf_writer.write(output)
                    
                return True, f"Successfully extracted page {page_number}"
                
        except ImportError:
            return False, "PyPDF2 module is not installed. Please install it using 'pip install PyPDF2'"
        except Exception as e:
            return False, f"Error extracting page: {str(e)}"

    def update_merge_summary(self):
        """Update the merge summary display"""
        count = self.pdf_listbox.count()
        if count == 0:
            self.merge_summary.setText("No PDF files selected yet")
            self.btn_merge_pdfs.setEnabled(False)
        elif count == 1:
            self.merge_summary.setText("1 PDF file selected. Add at least one more file to merge.")
            self.btn_merge_pdfs.setEnabled(False)
        else:
            self.merge_summary.setText(f"{count} PDF files ready to merge")
            self.btn_merge_pdfs.setEnabled(True)
            
    def add_pdf(self):
        """Add a PDF to the merge list"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            "",
            "PDF Files (*.pdf)"
        )
        
        if files:
            for file in files:
                self.pdf_listbox.addItem(file)
            
            self.update_merge_summary()
            
    def remove_pdf(self):
        """Remove the selected PDF from the merge list"""
        current_row = self.pdf_listbox.currentRow()
        if current_row >= 0:
            self.pdf_listbox.takeItem(current_row)
            self.update_merge_summary()
            self.status_label.setText(f"Removed PDF from merge list")
            
    def move_pdf_up(self):
        """Move the selected PDF up in the list"""
        current_row = self.pdf_listbox.currentRow()
        if current_row > 0:
            item = self.pdf_listbox.takeItem(current_row)
            self.pdf_listbox.insertItem(current_row - 1, item)
            self.pdf_listbox.setCurrentRow(current_row - 1)
            self.status_label.setText("Moved PDF up in the list")
            
    def move_pdf_down(self):
        """Move the selected PDF down in the list"""
        current_row = self.pdf_listbox.currentRow()
        if current_row >= 0 and current_row < self.pdf_listbox.count() - 1:
            item = self.pdf_listbox.takeItem(current_row)
            self.pdf_listbox.insertItem(current_row + 1, item)
            self.pdf_listbox.setCurrentRow(current_row + 1)
            self.status_label.setText("Moved PDF down in the list")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageToPdfConverter()
    window.show()
    sys.exit(app.exec())