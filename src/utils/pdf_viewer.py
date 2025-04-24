import os
import sys
import logging
import subprocess
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QDialogButtonBox, QMessageBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage, QResizeEvent
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import PyPDF2
from PIL import Image
import io

# Check if pdf2image is available
try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False
    logging.warning("pdf2image not installed. PDF preview quality may be limited.")

# Function to find portable Poppler
def find_portable_poppler():
    """
    Find portable Poppler installation
    Returns the path to the poppler bin directory if found, otherwise None
    """
    # Get the base directory - assume it's 2 levels up from this file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Possible locations for portable Poppler - prioritizing the poppler_portable_64/Library/bin structure
    possible_dirs = [
        os.path.join(base_dir, "poppler_portable_64", "Library", "bin"),  # Standard Poppler Windows release structure
        os.path.join(base_dir, "poppler_portable_64", "bin"),
        os.path.join(base_dir, "poppler_portable", "Library", "bin"),
        os.path.join(base_dir, "poppler_portable", "bin"),
        os.path.join(base_dir, "poppler", "bin")
    ]
    
    # Check app data directories as well
    appdata = os.environ.get('APPDATA', '')
    localappdata = os.environ.get('LOCALAPPDATA', '')
    programfiles = os.environ.get('PROGRAMFILES', '')
    
    if appdata:
        possible_dirs.append(os.path.join(appdata, "PDF Manager", "poppler_portable_64", "Library", "bin"))
    if localappdata:
        possible_dirs.append(os.path.join(localappdata, "PDF Manager", "poppler_portable_64", "Library", "bin"))
    if programfiles:
        possible_dirs.append(os.path.join(programfiles, "PDF Manager", "poppler_portable_64", "Library", "bin"))
    
    # Try to find pdftoppm.exe in these directories
    for dir_path in possible_dirs:
        pdftoppm_path = os.path.join(dir_path, "pdftoppm.exe" if sys.platform == "win32" else "pdftoppm")
        if os.path.isfile(pdftoppm_path):
            logging.info(f"Found portable Poppler at: {dir_path}")
            return dir_path
    
    return None

# Check for poppler (required by pdf2image)
HAS_POPPLER = False
POPPLER_PATH = None

if HAS_PDF2IMAGE:
    # First, try to find portable Poppler
    POPPLER_PATH = find_portable_poppler()
    
    if POPPLER_PATH:
        HAS_POPPLER = True
        logging.info(f"Using portable Poppler from: {POPPLER_PATH}")
    else:
        # Try system installed versions
        try:
            # Try to run pdftoppm (part of poppler) to check if it's available
            subprocess.run(["pdftoppm", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            HAS_POPPLER = True
            logging.info("System Poppler (pdftoppm) is available for PDF previews")
        except (subprocess.SubprocessError, FileNotFoundError):
            logging.warning("Poppler not found. PDF preview quality will be limited.")

class PDFViewerDialog(QDialog):
    def __init__(self, parent=None, pdf_path=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.current_page = 0
        self.total_pages = 0
        self.images = []  # Store page images
        self.current_pixmap = None  # Store the current pixmap for rescaling
        
        self.setup_ui()
        
        if pdf_path and os.path.exists(pdf_path):
            self.load_pdf(pdf_path)
    
    def setup_ui(self):
        self.setWindowTitle("PDF Preview")
        self.resize(900, 700)  # Start with a larger default size
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # File info
        self.file_info = QLabel("No file selected")
        toolbar.addWidget(self.file_info)
        
        # Spacer
        toolbar.addStretch()
        
        # Fit button
        self.fit_btn = QPushButton("Fit to Window")
        self.fit_btn.clicked.connect(self.fit_to_window)
        toolbar.addWidget(self.fit_btn)
        
        # Print button
        self.print_btn = QPushButton("Print...")
        self.print_btn.clicked.connect(self.print_pdf)
        toolbar.addWidget(self.print_btn)
        
        # Open in external viewer button
        self.external_btn = QPushButton("Open in System Viewer")
        self.external_btn.clicked.connect(self.open_external)
        toolbar.addWidget(self.external_btn)
        
        main_layout.addLayout(toolbar)
        
        # Scroll area for PDF preview
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # PDF preview container to allow proper sizing
        self.preview_container = QLabel()
        self.preview_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        
        # PDF preview image
        self.preview_label = QLabel("Loading PDF preview...")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(500, 400)
        self.preview_label.setStyleSheet("background-color: #f0f0f0;")
        
        # Add preview label to scroll area
        self.scroll_area.setWidget(self.preview_label)
        main_layout.addWidget(self.scroll_area, 1)  # Give it stretch factor for resizing
        
        # Page navigation buttons
        nav_layout = QHBoxLayout()
        
        # Previous page button
        self.prev_btn = QPushButton("Previous Page")
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_btn)
        
        # Page indicator
        self.page_label = QLabel("Page 0 of 0")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.page_label)
        
        # Next page button
        self.next_btn = QPushButton("Next Page")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(nav_layout)
        
        # Button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)
    
    def load_pdf(self, pdf_path):
        """Load a PDF file and display the first page preview"""
        try:
            self.pdf_path = pdf_path
            
            # Update file info
            file_size = os.path.getsize(pdf_path) / 1024  # KB
            if file_size > 1024:
                file_size = file_size / 1024  # MB
                size_str = f"{file_size:.2f} MB"
            else:
                size_str = f"{file_size:.2f} KB"
                
            # Display file info
            file_name = os.path.basename(pdf_path)
            self.file_info.setText(f"File: {file_name} ({size_str})")
            
            # Use PyPDF2 to get number of pages
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                self.total_pages = len(reader.pages)
                
                # Check if PDF has pages
                if self.total_pages > 0:
                    self.current_page = 0
                    
                    # Load first page immediately
                    self.render_page(self.current_page)
                    
                    # Update window title to include page count
                    self.setWindowTitle(f"PDF Preview - {file_name} ({self.total_pages} pages)")
                    
                    # Update page navigation 
                    self.update_navigation()
                else:
                    self.preview_label.setText("PDF has no pages")
            
        except Exception as e:
            logging.error(f"Error loading PDF: {str(e)}")
            self.preview_label.setText(f"Could not load PDF: {str(e)}")
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize events to scale the PDF properly"""
        super().resizeEvent(event)
        if self.current_pixmap:
            self.scale_pixmap_to_fit()
    
    def fit_to_window(self):
        """Scale the current page to fit the window"""
        if self.current_pixmap:
            self.scale_pixmap_to_fit()
    
    def scale_pixmap_to_fit(self):
        """Scale the current pixmap to fit the scroll area while maintaining aspect ratio"""
        if not self.current_pixmap:
            return
            
        # Get available size in the scroll area
        available_width = self.scroll_area.width() - 20  # Subtract some padding
        available_height = self.scroll_area.height() - 20
        
        # Scale the pixmap to fit the available space while maintaining aspect ratio
        scaled_pixmap = self.current_pixmap.scaled(
            available_width, 
            available_height,
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Update the preview label with the scaled pixmap
        self.preview_label.setPixmap(scaled_pixmap)
        self.preview_label.setMinimumSize(1, 1)  # Allow label to shrink
        
        # Log scaling details
        logging.debug(f"Scaled pixmap from {self.current_pixmap.width()}x{self.current_pixmap.height()} " +
                    f"to {scaled_pixmap.width()}x{scaled_pixmap.height()}")
    
    def update_navigation(self):
        """Update navigation buttons and page display"""
        self.page_label.setText(f"Page {self.current_page + 1} of {self.total_pages}")
        
        # Enable/disable navigation buttons based on current page
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < self.total_pages - 1)
    
    def next_page(self):
        """Navigate to the next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.render_page(self.current_page)
            self.update_navigation()
    
    def previous_page(self):
        """Navigate to the previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.render_page(self.current_page)
            self.update_navigation()
    
    def render_page(self, page_number):
        """Render the specified page"""
        try:
            # Try using pikepdf for better rendering
            try:
                import pikepdf
                import tempfile
                
                with pikepdf.open(self.pdf_path) as pdf:
                    # Make sure we're in bounds
                    if page_number >= len(pdf.pages):
                        return
                    
                    # Get requested page
                    page = pdf.pages[page_number]
                    
                    # Convert to image using a temporary file approach
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        temp_path = tmp_file.name
                    
                    # Save the page as a PDF
                    pdf_instance = pikepdf.Pdf.new()
                    pdf_instance.pages.append(page)
                    pdf_instance.save(temp_path.replace('.png', '.pdf'))
                    
                    # Use Pillow to convert PDF to image
                    from PIL import Image
                    
                    try:
                        # Try using PyMuPDF if available
                        import fitz
                        
                        # Try PyMuPDF for best quality
                        doc = fitz.open(temp_path.replace('.png', '.pdf'))
                        pix = doc[0].get_pixmap(alpha=False)
                        img_data = pix.tobytes("png")
                        
                        # Create QImage and QPixmap
                        img = QImage.fromData(img_data)
                        self.current_pixmap = QPixmap.fromImage(img)
                        
                    except (ImportError, Exception):
                        # Fall back to PIL
                        # Use PIL to render PDF to image
                        img = Image.open(temp_path.replace('.png', '.pdf'))
                        if hasattr(img, 'seek') and callable(getattr(img, 'seek')):
                            img.seek(0)
                        
                        # Convert PIL image to QPixmap
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='PNG')
                        img_byte_arr.seek(0)
                        
                        # Create QImage and QPixmap
                        qimg = QImage.fromData(img_byte_arr.getvalue())
                        self.current_pixmap = QPixmap.fromImage(qimg)
                    
                    # Scale to fit the window
                    self.scale_pixmap_to_fit()
                    
                    # Clean up temp files
                    try:
                        os.unlink(temp_path)
                        os.unlink(temp_path.replace('.png', '.pdf'))
                    except:
                        pass
                
            except Exception as pikepdf_error:
                # Fallback to alternative rendering
                logging.warning(f"pikepdf rendering failed: {str(pikepdf_error)}")
                
                # Try direct rendering with PyPDF2 and PIL if possible
                try:
                    import io
                    from PIL import Image
                    import tempfile
                    
                    # Create a temporary PDF file with just the selected page
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                        temp_path = tmp_file.name
                    
                    # Open the PDF and extract the single page
                    with open(self.pdf_path, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        
                        # Make sure page number is valid
                        if page_number >= len(reader.pages):
                            return
                        
                        # Extract page to a new PDF
                        writer = PyPDF2.PdfWriter()
                        writer.add_page(reader.pages[page_number])
                        
                        with open(temp_path, 'wb') as f:
                            writer.write(f)
                    
                    # Use pdf2image if available and dependencies are present
                    if HAS_PDF2IMAGE and HAS_POPPLER:
                        try:
                            # Use portable poppler if available
                            if POPPLER_PATH:
                                images = convert_from_path(temp_path, first_page=1, last_page=1, 
                                                          poppler_path=POPPLER_PATH)
                            else:
                                images = convert_from_path(temp_path, first_page=1, last_page=1)
                            
                            if images:
                                # Convert PIL image to QPixmap
                                img_byte_arr = io.BytesIO()
                                images[0].save(img_byte_arr, format='PNG')
                                img_byte_arr.seek(0)
                                
                                # Create QImage and QPixmap
                                img = QImage.fromData(img_byte_arr.getvalue())
                                self.current_pixmap = QPixmap.fromImage(img)
                                
                                # Scale to fit the window
                                self.scale_pixmap_to_fit()
                            else:
                                raise Exception("No images generated")
                        except Exception as pdf2image_error:
                            # Specific error for missing dependencies
                            if "PDFInfoNotInstalledError" in str(pdf2image_error) or "not installed" in str(pdf2image_error):
                                self.preview_label.setText(
                                    "PDF Preview Available\n\n"
                                    "To see PDF previews, please install Poppler.\n"
                                    "See README.md for installation instructions or\n"
                                    "open the PDF in your system viewer."
                                )
                            else:
                                logging.error(f"pdf2image error: {str(pdf2image_error)}")
                                self.preview_label.setText(
                                    "PDF Preview Available\n\n"
                                    "Click 'Open in System Viewer' for full quality view."
                                )
                    else:
                        # Inform user about missing pdf2image dependency or its requirements
                        missing_component = "pdf2image" if not HAS_PDF2IMAGE else "Poppler"
                        self.preview_label.setText(
                            "PDF Preview Available\n\n"
                            f"Install '{missing_component}' for better previews or\n"
                            "Open in System Viewer for full viewing."
                        )
                    
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                    
                except Exception as fallback_error:
                    logging.warning(f"PDF rendering failed: {str(fallback_error)}")
                    self.preview_label.setText(
                        "PDF Preview Available\n\n"
                        "Open in System Viewer for better quality"
                    )
                
        except Exception as e:
            logging.error(f"Error rendering PDF preview: {str(e)}")
            self.preview_label.setText(
                "PDF preview not available.\n\n"
                "Click 'Open in System Viewer' to view the PDF."
            )
    
    def print_pdf(self):
        """Print the PDF using system dialog"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            QMessageBox.warning(self, "Warning", "No PDF available to print.")
            return
        
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if sys.platform == 'win32':
                    printer_name = printer.printerName()
                    os.system(f'print /d:"{printer_name}" "{self.pdf_path}"')
                else:
                    # For macOS and Linux
                    printer_name = printer.printerName()
                    os.system(f'lpr -P "{printer_name}" "{self.pdf_path}"')
                
                QMessageBox.information(self, "Print", f"Document sent to printer {printer.printerName()}")
        
        except Exception as e:
            logging.error(f"Error printing PDF: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error printing PDF: {str(e)}")
    
    def open_external(self):
        """Open the PDF in the system's default viewer"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            QMessageBox.warning(self, "Warning", "No PDF available to open.")
            return
            
        try:
            # Use absolute path to avoid relative path issues
            abs_path = os.path.abspath(self.pdf_path)
            logging.info(f"Opening PDF in system viewer: {abs_path}")
            
            if sys.platform == 'win32':
                # On Windows, shell=True allows for better handling of file associations
                # and doesn't capture the console
                subprocess.Popen(f'cmd /c start "" "{abs_path}"', shell=True)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', abs_path])
            else:  # Linux
                subprocess.run(['xdg-open', abs_path])
                
            # Log that external viewer was called
            logging.info(f"External viewer launched for: {abs_path}")
        except Exception as e:
            logging.error(f"Error opening external viewer: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error opening system viewer: {str(e)}")


def show_pdf_viewer(parent, pdf_path):
    """Convenience function to show the PDF viewer dialog"""
    if not pdf_path or not os.path.exists(pdf_path):
        QMessageBox.warning(parent, "Warning", "No PDF file selected to preview.")
        return
    
    try:
        dialog = PDFViewerDialog(parent, pdf_path)
        dialog.exec()
    except Exception as e:
        logging.error(f"Error showing PDF viewer: {str(e)}")
        QMessageBox.critical(parent, "Error", f"Error showing PDF preview: {str(e)}")
        
        # Fall back to system viewer
        try:
            if sys.platform == 'win32':
                os.startfile(pdf_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', pdf_path])
            else:  # Linux
                subprocess.run(['xdg-open', pdf_path])
        except Exception as fallback_error:
            logging.error(f"Error with fallback preview: {str(fallback_error)}") 