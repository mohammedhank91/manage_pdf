import sys
import os
import logging
import types

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QCheckBox,
    QSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar,
    QListWidget, QVBoxLayout, QWidget, QTabWidget
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from src.utils.style import apply_modern_style
from src.utils.convert import convert_to_pdf
from src.utils.merge import merge_pdfs, update_merge_summary, add_pdf, remove_pdf, move_pdf_up, move_pdf_down
from src.utils.edit_pdf import setup_pdf_editor
from src.utils.compress import select_pdf, preview_pdf, print_pdf, compress_pdf
from src.utils.convert import update_conversion_ui, save_conversion_settings, load_conversion_settings
from src.utils.drag_drop import setupDragDrop, dragEnterEvent, dropEvent
from src.utils.magick import find_imagick, run_imagemagick
from src.utils.split import extract_pages, parse_page_range, extract_single_page_with_pypdf2, select_pdf_to_split, count_pages, extract_pages_with_pypdf2, set_page_range
from src.utils.cleanup import force_cleanup_temp_files

# Import tab setup functions
from src.tabs.main_tab import setup_main_tab
from src.tabs.convert_tab import setup_convert_tab
from src.tabs.compress_tab import setup_tools_tab
from src.tabs.merge_tab import setup_merge_tab
from src.tabs.split_tab import setup_split_tab, load_pdf_in_split_preview, update_split_page_navigation, split_prev_page, split_next_page, zoom_split_preview, apply_split_zoom
from src.tabs.preview_tab import setup_preview_tab, select_pdf_for_preview, load_pdf_in_preview, update_page_navigation
from src.tabs.preview_tab import prev_page_preview, next_page_preview, zoom_in_preview, zoom_out_preview, apply_zoom_preview, print_current_pdf, open_in_system_viewer

# Import utility functions
from src.utils.developer import add_developer_credit
from src.utils.check_dependencies import check_dependencies
from src.utils.image_tool import select_images, prev_image, next_image, update_picture_box, rotate_image
from src.utils.image_tool import on_listbox_select, move_up, move_down, delete_image, reset_inputs, wheelEvent


class PdfManager(QMainWindow):
    def __init__(self):
        """Initialize the Image to PDF converter."""
        # Call parent constructor
        super().__init__()

        # Clean up any leftover temporary files from previous runs
        try:
            cleanup_count = force_cleanup_temp_files()
            if cleanup_count > 0:
                logging.info(f"Cleaned up {cleanup_count} leftover temporary files at startup")
        except Exception as e:
            logging.error(f"Error during startup cleanup: {str(e)}")

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
        self.find_imagick = types.MethodType(find_imagick, self)
        self.run_imagemagick = types.MethodType(run_imagemagick, self)

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
        self.preview_tab = QWidget()  # New preview tab

        # Add tabs to widget
        self.tab_widget.addTab(self.main_tab, "Main")
        self.tab_widget.addTab(self.convert_tab, "Convert")
        self.tab_widget.addTab(self.tools_tab, "Compress PDF")
        self.tab_widget.addTab(self.merge_tab, "Merge PDFs")
        self.tab_widget.addTab(self.split_tab, "Split PDF")
        self.tab_widget.addTab(self.preview_tab, "PDF Viewer")  # New preview tab

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
        self.setup_pdf_editor = types.MethodType(setup_pdf_editor, self)

        # PDF preview tab methods
        self.select_pdf_for_preview = types.MethodType(select_pdf_for_preview, self)
        self.load_pdf_in_preview = types.MethodType(load_pdf_in_preview, self)
        self.update_page_navigation = types.MethodType(update_page_navigation, self)
        self.prev_page_preview = types.MethodType(prev_page_preview, self)
        self.next_page_preview = types.MethodType(next_page_preview, self)
        self.zoom_in_preview = types.MethodType(zoom_in_preview, self)
        self.zoom_out_preview = types.MethodType(zoom_out_preview, self)
        self.apply_zoom_preview = types.MethodType(apply_zoom_preview, self)
        self.print_current_pdf = types.MethodType(print_current_pdf, self)
        self.open_in_system_viewer = types.MethodType(open_in_system_viewer, self)

        # Split tab preview methods
        self.load_pdf_in_split_preview = types.MethodType(load_pdf_in_split_preview, self)
        self.update_split_page_navigation = types.MethodType(update_split_page_navigation, self)
        self.split_prev_page = types.MethodType(split_prev_page, self)
        self.split_next_page = types.MethodType(split_next_page, self)
        self.zoom_split_preview = types.MethodType(zoom_split_preview, self)
        self.apply_split_zoom = types.MethodType(apply_split_zoom, self)

        # Set up each tab with widgets
        setup_main_tab(self)
        setup_convert_tab(self)
        setup_tools_tab(self)
        setup_merge_tab(self)
        setup_split_tab(self)
        setup_preview_tab(self)  # Setup the new preview tab

        # Add developer credit
        add_developer_credit(self)

        # Check dependencies on startup
        check_dependencies(self)

    def _app_base(self):
        """Return the base directory of the application."""
        return self.base_path

    def load_external_pdf_in_viewer(self, pdf_path):
        """Method to load a PDF from another tab into the PDF Viewer tab"""
        if not pdf_path or not os.path.exists(pdf_path):
            return False

        # Store the PDF path
        self.latest_pdf = pdf_path

        # Switch to the PDF Viewer tab
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "PDF Viewer":
                self.tab_widget.setCurrentIndex(i)
                break

        # Enable buttons
        if hasattr(self, 'btn_print_preview'):
            self.btn_print_preview.setEnabled(True)
        if hasattr(self, 'btn_open_system'):
            self.btn_open_system.setEnabled(True)
        if hasattr(self, 'big_system_btn'):
            self.big_system_btn.setEnabled(True)

        # Update PDF info
        file_size = os.path.getsize(pdf_path) / 1024  # KB
        if file_size > 1024:
            file_size = file_size / 1024  # MB
            size_str = f"{file_size:.2f} MB"
        else:
            size_str = f"{file_size:.2f} KB"

        if hasattr(self, 'preview_pdf_info'):
            self.preview_pdf_info.setText(f"PDF: {os.path.basename(pdf_path)} ({size_str})")
        if hasattr(self, 'preview_status'):
            self.preview_status.setText(f"Previewing: {os.path.basename(pdf_path)}")

        # Load the PDF in the viewer
        try:
            return self.load_pdf_in_preview(pdf_path)
        except Exception as e:
            logging.error(f"Error loading external PDF: {str(e)}")
            return False

    def closeEvent(self, event):
        """Handle application close event - clean up temporary files"""
        try:
            cleanup_count = force_cleanup_temp_files()
            if cleanup_count > 0:
                logging.info(f"Cleaned up {cleanup_count} temporary files at application exit")
        except Exception as e:
            logging.error(f"Error during exit cleanup: {str(e)}")
        
        # Accept the close event to proceed with application exit
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PdfManager()
    window.show()
    sys.exit(app.exec())
