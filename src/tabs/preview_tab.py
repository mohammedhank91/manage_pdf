import os
import sys
import logging
import subprocess
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QSpinBox, QComboBox, QDialog
)
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

# Try to import QWebEngineView, but have a fallback if not available
HAS_WEBENGINE = False
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    HAS_WEBENGINE = True
except ImportError:
    logging.warning("QtWebEngine not available - using fallback for PDF viewer")


def setup_preview_tab(self):
    """Setup the PDF Preview tab with interactive viewer"""

    # Main layout for the tab
    preview_layout = QVBoxLayout()

    # Top controls layout
    controls_layout = QHBoxLayout()

    # Select PDF button
    self.btn_select_pdf_preview = QPushButton("Select PDF")
    self.btn_select_pdf_preview.setIcon(QIcon.fromTheme("document-open"))
    self.btn_select_pdf_preview.clicked.connect(self.select_pdf_for_preview)
    self.btn_select_pdf_preview.setToolTip("Browse and select a PDF file to preview")
    controls_layout.addWidget(self.btn_select_pdf_preview)

    # Label to show current PDF
    self.preview_pdf_info = QLabel("No PDF selected")
    controls_layout.addWidget(self.preview_pdf_info, 1)  # Give it stretch

    # Add print button
    self.btn_print_preview = QPushButton("Print")
    self.btn_print_preview.setIcon(QIcon.fromTheme("document-print"))
    self.btn_print_preview.clicked.connect(self.print_current_pdf)
    self.btn_print_preview.setEnabled(False)
    self.btn_print_preview.setToolTip("Print the currently previewed PDF document")
    controls_layout.addWidget(self.btn_print_preview)

    # Open in system viewer button (always available as fallback)
    self.btn_open_system = QPushButton("Open in System Viewer")
    self.btn_open_system.clicked.connect(self.open_in_system_viewer)
    self.btn_open_system.setEnabled(False)
    self.btn_open_system.setToolTip("Open the PDF file in your default system PDF viewer")
    controls_layout.addWidget(self.btn_open_system)

    # Add controls to the main layout
    preview_layout.addLayout(controls_layout)

    if HAS_WEBENGINE:
        # Add zoom controls if web engine is available
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("Zoom:")
        zoom_layout.addWidget(zoom_label)

        # Zoom out button
        self.btn_zoom_out = QPushButton("-")
        self.btn_zoom_out.setFixedWidth(30)
        self.btn_zoom_out.clicked.connect(self.zoom_out_preview)
        self.btn_zoom_out.setToolTip("Zoom out to see more of the page")
        zoom_layout.addWidget(self.btn_zoom_out)

        # Zoom factor
        self.zoom_factor_preview = QSpinBox()
        self.zoom_factor_preview.setRange(50, 200)
        self.zoom_factor_preview.setValue(100)
        self.zoom_factor_preview.setSuffix("%")
        self.zoom_factor_preview.setSingleStep(10)
        self.zoom_factor_preview.valueChanged.connect(self.apply_zoom_preview)
        self.zoom_factor_preview.setToolTip("Set zoom level for PDF preview (50% to 200%)")
        zoom_layout.addWidget(self.zoom_factor_preview)

        # Zoom in button
        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setFixedWidth(30)
        self.btn_zoom_in.clicked.connect(self.zoom_in_preview)
        self.btn_zoom_in.setToolTip("Zoom in for a closer view of the page")
        zoom_layout.addWidget(self.btn_zoom_in)

        controls_layout.addLayout(zoom_layout)

        # Create web engine view for PDF viewing
        self.pdf_web_view = QWebEngineView()
        self.pdf_web_view.setMinimumHeight(400)

        # Enable PDF plugins and JavaScript
        settings = self.pdf_web_view.settings()
        if hasattr(settings, 'setAttribute'):
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)

        # Default message when no PDF is loaded
        self.pdf_web_view.setHtml("""
            <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f5f5f5;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        text-align: center;
                    }
                    .container {
                        background-color: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                        max-width: 80%;
                    }
                    h2 {
                        color: #333;
                        margin-bottom: 20px;
                    }
                    p {
                        color: #666;
                        line-height: 1.6;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>PDF Viewer</h2>
                    <p>Select a PDF file to preview it here.</p>
                    <p>Use the controls above to navigate and adjust the view.</p>
                </div>
            </body>
            </html>
        """)

        # Add the web view to the layout
        preview_layout.addWidget(self.pdf_web_view, 1)  # Give it stretch factor

        # Status bar at the bottom
        status_layout = QHBoxLayout()
        self.preview_status = QLabel("Ready to preview PDFs")
        status_layout.addWidget(self.preview_status)

        # Page navigation (for multi-page PDFs)
        page_nav_layout = QHBoxLayout()

        # Previous page button
        self.btn_prev_page = QPushButton("◀ Previous")
        self.btn_prev_page.clicked.connect(self.prev_page_preview)
        self.btn_prev_page.setEnabled(False)
        self.btn_prev_page.setToolTip("Go to the previous page in the PDF")
        page_nav_layout.addWidget(self.btn_prev_page)

        # Page indicator
        self.page_indicator = QLabel("Page: --")
        page_nav_layout.addWidget(self.page_indicator)

        # Next page button
        self.btn_next_page = QPushButton("Next ▶")
        self.btn_next_page.clicked.connect(self.next_page_preview)
        self.btn_next_page.setEnabled(False)
        self.btn_next_page.setToolTip("Go to the next page in the PDF")
        page_nav_layout.addWidget(self.btn_next_page)

        status_layout.addLayout(page_nav_layout)
        preview_layout.addLayout(status_layout)
    else:
        # Fallback view when QWebEngineView is not available
        fallback_layout = QVBoxLayout()

        # Show message that web view is not available
        fallback_label = QLabel(
            "Advanced PDF viewing requires PyQt6-WebEngine to be installed.\n\n"
            "Please install it with:\n"
            "pip install PyQt6-WebEngine\n\n"
            "You can still use the system PDF viewer by clicking 'Open in System Viewer'"
        )
        fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fallback_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 20px;
                border-radius: 8px;
                font-size: 14px;
                margin: 50px;
                line-height: 1.5;
            }
        """)
        fallback_layout.addWidget(fallback_label)

        # Add a big button to open in system viewer
        big_system_btn = QPushButton("Open PDF in System Viewer")
        big_system_btn.setStyleSheet("""
            QPushButton {
                padding: 15px;
                font-size: 16px;
                margin: 20px 100px;
            }
        """)
        big_system_btn.clicked.connect(self.open_in_system_viewer)
        big_system_btn.setEnabled(False)
        self.big_system_btn = big_system_btn
        fallback_layout.addWidget(big_system_btn)

        preview_layout.addLayout(fallback_layout)

        # Simple status
        self.preview_status = QLabel("PDF Viewer Ready (Limited Functionality)")
        preview_layout.addWidget(self.preview_status)

    # Set the layout to the tab
    self.preview_tab.setLayout(preview_layout)

    # Store a flag to prevent duplicate loading
    self.current_loaded_pdf = ""


def select_pdf_for_preview(self):
    """Select a PDF file to preview"""
    pdf_file, _ = QFileDialog.getOpenFileName(
        self,
        "Select PDF File to Preview",
        "",
        "PDF Files (*.pdf)"
    )

    if pdf_file and os.path.exists(pdf_file):
        self.latest_pdf = pdf_file

        # Enable print and system viewer buttons
        self.btn_print_preview.setEnabled(True)
        self.btn_open_system.setEnabled(True)

        # If we have a big system button (fallback UI), enable it
        if hasattr(self, 'big_system_btn'):
            self.big_system_btn.setEnabled(True)

        # Update PDF info display
        file_size = os.path.getsize(pdf_file) / 1024  # KB
        if file_size > 1024:
            file_size = file_size / 1024  # MB
            size_str = f"{file_size:.2f} MB"
        else:
            size_str = f"{file_size:.2f} KB"

        self.preview_pdf_info.setText(f"PDF: {os.path.basename(pdf_file)} ({size_str})")
        self.preview_status.setText(f"Selected: {os.path.basename(pdf_file)}")

        # If web engine is available, load the PDF
        if HAS_WEBENGINE:
            self.load_pdf_in_preview(pdf_file)


def load_pdf_in_preview(self, pdf_path):
    """Load a PDF file into the web view"""
    if not HAS_WEBENGINE:
        return False

    # Don't reload if it's the same PDF
    if hasattr(self, 'current_loaded_pdf') and self.current_loaded_pdf == pdf_path:
        return True

    try:
        # Store current PDF path to avoid reloading
        self.current_loaded_pdf = pdf_path

        # Create a file URL that explicitly specifies it's a PDF
        abs_path = os.path.abspath(pdf_path)
        url = QUrl.fromLocalFile(abs_path)

        # Try using direct PDF viewing
        self.pdf_web_view.setUrl(url)

        # Enable navigation buttons
        self.btn_prev_page.setEnabled(True)
        self.btn_next_page.setEnabled(True)

        # Update UI
        self.current_page = 1
        self.update_page_navigation()
        self.preview_status.setText(f"Previewing: {os.path.basename(pdf_path)}")

        return True

    except Exception as e:
        logging.error(f"Error loading PDF for preview: {str(e)}")
        # Try the alternative HTML approach
        try:
            abs_path = os.path.abspath(pdf_path).replace('\\', '/')
            file_url = QUrl.fromLocalFile(abs_path).toString()

            # Use an HTML wrapper with the PDF embedded in an iframe or object tag
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>PDF Viewer</title>
                <style>
                    body, html {{
                        margin: 0;
                        padding: 0;
                        height: 100%;
                        overflow: hidden;
                    }}
                    #pdf-container {{
                        width: 100%;
                        height: 100%;
                        overflow: auto;
                    }}
                    object, embed, iframe {{
                        width: 100%;
                        height: 100%;
                        border: none;
                    }}
                </style>
            </head>
            <body>
                <div id="pdf-container">
                    <!-- Try multiple embedding methods for better compatibility -->
                    <object data="{file_url}" type="application/pdf" width="100%" height="100%">
                        <embed src="{file_url}" type="application/pdf" width="100%" height="100%">
                            <iframe src="{file_url}" width="100%" height="100%">
                                <p>This browser does not support PDF embedding. Please <a href="{file_url}">click here to download the PDF</a>.</p>
                            </iframe>
                        </embed>
                    </object>
                </div>
            </body>
            </html>
            """

            # Load the HTML wrapper
            self.pdf_web_view.setHtml(html_content, baseUrl=QUrl.fromLocalFile(os.path.dirname(abs_path)))
            return True

        except Exception as alt_error:
            logging.error(f"Error with alternative PDF loading: {str(alt_error)}")
            QMessageBox.critical(self, "Error",
                                 "Could not load PDF using multiple methods. Please try opening with the system viewer.")
            return False


def open_in_system_viewer(self):
    """Open the selected PDF in the system's default PDF viewer"""
    if not self.latest_pdf or not os.path.exists(self.latest_pdf):
        QMessageBox.warning(self, "Warning", "No PDF file selected to open.")
        return

    try:
        # Use absolute path to avoid relative path issues
        abs_path = os.path.abspath(self.latest_pdf)
        logging.info(f"Opening PDF in system viewer: {abs_path}")

        if sys.platform == 'win32':
            # On Windows, use os.startfile
            os.startfile(abs_path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', abs_path])
        else:  # Linux
            subprocess.run(['xdg-open', abs_path])

        self.preview_status.setText(f"Opened in system viewer: {os.path.basename(self.latest_pdf)}")

    except Exception as e:
        logging.error(f"Error opening external viewer: {str(e)}")
        QMessageBox.critical(self, "Error", f"Error opening system viewer: {str(e)}")


def update_page_navigation(self):
    """Update the page navigation controls based on current state"""
    if not HAS_WEBENGINE:
        return

    # Most of this would be handled by the PDF viewer in the QWebEngineView
    # We simply update the indicator here
    self.page_indicator.setText(f"Page: {self.current_page}")

    # Enable navigation buttons (the actual navigation is handled by the web view)
    self.btn_prev_page.setEnabled(True)
    self.btn_next_page.setEnabled(True)


def prev_page_preview(self):
    """Go to previous page in the PDF preview"""
    if not HAS_WEBENGINE:
        return

    # Execute JavaScript to go to previous page
    # This depends on the PDF.js viewer in QWebEngineView
    self.pdf_web_view.page().runJavaScript("window.scrollBy(0, -window.innerHeight);")

    if self.current_page > 1:
        self.current_page -= 1
        self.update_page_navigation()


def next_page_preview(self):
    """Go to next page in the PDF preview"""
    if not HAS_WEBENGINE:
        return

    # Execute JavaScript to go to next page
    # This depends on the PDF.js viewer in QWebEngineView
    self.pdf_web_view.page().runJavaScript("window.scrollBy(0, window.innerHeight);")

    self.current_page += 1
    self.update_page_navigation()


def zoom_in_preview(self):
    """Zoom in on the PDF preview"""
    if not HAS_WEBENGINE:
        return

    current_zoom = self.zoom_factor_preview.value()
    new_zoom = min(current_zoom + 10, 200)  # Increment but not over 200%
    self.zoom_factor_preview.setValue(new_zoom)


def zoom_out_preview(self):
    """Zoom out on the PDF preview"""
    if not HAS_WEBENGINE:
        return

    current_zoom = self.zoom_factor_preview.value()
    new_zoom = max(current_zoom - 10, 50)  # Decrement but not below 50%
    self.zoom_factor_preview.setValue(new_zoom)


def apply_zoom_preview(self):
    """Apply the current zoom factor to the PDF preview"""
    if not HAS_WEBENGINE:
        return

    zoom_value = self.zoom_factor_preview.value() / 100.0
    # Apply zoom using JavaScript
    self.pdf_web_view.page().runJavaScript(f"document.body.style.zoom = {zoom_value};")


def print_current_pdf(self):
    """Print the current PDF file"""
    if not self.latest_pdf or not os.path.exists(self.latest_pdf):
        QMessageBox.warning(self, "Warning", "No PDF file selected to print.")
        return

    try:
        # Use the print_pdf method from compress.py which is already available
        if hasattr(self, 'print_pdf'):
            self.print_pdf()
        else:
            # Direct implementation in case print_pdf is not available
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, self)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                if sys.platform == 'win32':
                    printer_name = printer.printerName()
                    os.system(f'print /d:"{printer_name}" "{self.latest_pdf}"')
                else:
                    # For macOS and Linux
                    printer_name = printer.printerName()
                    os.system(f'lpr -P "{printer_name}" "{self.latest_pdf}"')

                self.preview_status.setText(f"Document sent to printer {printer.printerName()}")
    except Exception as e:
        logging.error(f"Error printing PDF: {str(e)}")
        QMessageBox.critical(self, "Error", f"Error printing PDF: {str(e)}")
