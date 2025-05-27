from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, 
    QSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar, 
    QListWidget, QFrame, QVBoxLayout, QHBoxLayout, QWidget, 
    QTabWidget, QScrollArea, QListWidgetItem, QGridLayout, QGroupBox, QLineEdit, QRadioButton, QInputDialog,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QUrl
import os
import logging

# Try to import QWebEngineView for PDF preview, with fallback
HAS_WEBENGINE = False
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    HAS_WEBENGINE = True
except ImportError:
    logging.warning("QtWebEngine not available - PDF preview will use fallback mode")

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
    self.btn_select_pdf_to_split.setToolTip("Browse and select a PDF file to extract pages from")
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
    
    # PDF preview with functional viewer
    preview_frame = QFrame()
    preview_frame.setStyleSheet("background-color: #f5f5f7; border-radius: 4px; padding: 5px;")
    preview_frame.setMinimumHeight(200)  # Increase height for better viewing
    preview_layout = QVBoxLayout(preview_frame)
    preview_layout.setContentsMargins(5, 5, 5, 5)
    preview_layout.setSpacing(3)
    
    # Preview header with controls
    preview_header_layout = QHBoxLayout()
    preview_header = QLabel("Preview")
    preview_header.setStyleSheet("font-weight: bold; color: #424242;")
    preview_header_layout.addWidget(preview_header)
    
    if HAS_WEBENGINE:
        # Add zoom controls for web engine
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedSize(25, 25)
        zoom_out_btn.setToolTip("Zoom out")
        zoom_out_btn.clicked.connect(lambda: self.zoom_split_preview(-10))
        preview_header_layout.addWidget(zoom_out_btn)
        
        self.split_zoom_factor = QSpinBox()
        self.split_zoom_factor.setRange(50, 200)
        self.split_zoom_factor.setValue(100)
        self.split_zoom_factor.setSuffix("%")
        self.split_zoom_factor.setSingleStep(10)
        self.split_zoom_factor.setFixedWidth(70)
        self.split_zoom_factor.valueChanged.connect(self.apply_split_zoom)
        self.split_zoom_factor.setToolTip("Zoom level for preview")
        preview_header_layout.addWidget(self.split_zoom_factor)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(25, 25)
        zoom_in_btn.setToolTip("Zoom in")
        zoom_in_btn.clicked.connect(lambda: self.zoom_split_preview(10))
        preview_header_layout.addWidget(zoom_in_btn)
    
    preview_header_layout.addStretch()
    preview_layout.addLayout(preview_header_layout)
    
    if HAS_WEBENGINE:
        # Create web engine view for PDF viewing
        self.split_pdf_preview = QWebEngineView()
        self.split_pdf_preview.setMinimumHeight(150)
        
        # Enable PDF plugins and JavaScript
        settings = self.split_pdf_preview.settings()
        if hasattr(settings, 'setAttribute'):
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        
        # Default message when no PDF is loaded
        self.split_pdf_preview.setHtml("""
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
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        max-width: 80%;
                    }
                    h3 {
                        color: #333;
                        margin-bottom: 10px;
                    }
                    p {
                        color: #666;
                        line-height: 1.4;
                        font-size: 12px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h3>PDF Preview</h3>
                    <p>Select a PDF file to preview pages before extracting.</p>
                </div>
            </body>
            </html>
        """)
        
        preview_layout.addWidget(self.split_pdf_preview)
        
        # Page navigation for split preview
        nav_layout = QHBoxLayout()
        
        self.btn_split_prev_page = QPushButton("◀ Prev")
        self.btn_split_prev_page.setFixedHeight(24)
        self.btn_split_prev_page.clicked.connect(self.split_prev_page)
        self.btn_split_prev_page.setEnabled(False)
        self.btn_split_prev_page.setToolTip("Go to previous page")
        nav_layout.addWidget(self.btn_split_prev_page)
        
        self.split_page_indicator = QLabel("Page: --")
        self.split_page_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.split_page_indicator.setStyleSheet("font-size: 9pt; color: #424242;")
        nav_layout.addWidget(self.split_page_indicator)
        
        self.btn_split_next_page = QPushButton("Next ▶")
        self.btn_split_next_page.setFixedHeight(24)
        self.btn_split_next_page.clicked.connect(self.split_next_page)
        self.btn_split_next_page.setEnabled(False)
        self.btn_split_next_page.setToolTip("Go to next page")
        nav_layout.addWidget(self.btn_split_next_page)
        
        preview_layout.addLayout(nav_layout)
        
        # Initialize split preview variables
        self.split_current_page = 1
        self.split_loaded_pdf = ""
    else:
        # Fallback when QWebEngineView is not available
        fallback_label = QLabel(
            "PDF Preview requires PyQt6-WebEngine.\n\n"
            "Install with: pip install PyQt6-WebEngine\n\n"
            "For now, you can select a PDF and use\n"
            "the page information above."
        )
        fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fallback_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 15px;
                border-radius: 4px;
                color: #666;
                font-size: 10pt;
                line-height: 1.4;
            }
        """)
        preview_layout.addWidget(fallback_label)
    
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
    self.page_range_input.setToolTip("Enter specific pages to extract. Use commas for individual pages, hyphens for ranges (e.g., 1,3,5-8,10)")
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
    all_pages_btn.setToolTip("Select all pages from the PDF document")
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
    even_pages_btn.setToolTip("Select only even-numbered pages (2, 4, 6, etc.)")
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
    odd_pages_btn.setToolTip("Select only odd-numbered pages (1, 3, 5, etc.)")
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
    self.single_output_file.setToolTip("Combine all extracted pages into one PDF file")
    output_layout.addWidget(self.single_output_file)
    
    self.multiple_output_files = QRadioButton("Extract each page to a separate PDF")
    self.multiple_output_files.setStyleSheet("margin-top: 3px; font-size: 9pt;")
    self.multiple_output_files.setToolTip("Create individual PDF files for each extracted page")
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
    self.btn_extract_pages.setToolTip("Extract the specified pages from the selected PDF file")
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


# Split tab preview functions
def load_pdf_in_split_preview(self, pdf_path):
    """Load a PDF file into the split tab preview"""
    if not HAS_WEBENGINE or not hasattr(self, 'split_pdf_preview'):
        return False

    # Don't reload if it's the same PDF
    if hasattr(self, 'split_loaded_pdf') and self.split_loaded_pdf == pdf_path:
        return True

    try:
        # Store current PDF path to avoid reloading
        self.split_loaded_pdf = pdf_path

        # Create a file URL for the PDF
        abs_path = os.path.abspath(pdf_path)
        url = QUrl.fromLocalFile(abs_path)

        # Load the PDF in the preview
        self.split_pdf_preview.setUrl(url)

        # Enable navigation buttons
        self.btn_split_prev_page.setEnabled(True)
        self.btn_split_next_page.setEnabled(True)

        # Update UI
        self.split_current_page = 1
        self.update_split_page_navigation()

        return True

    except Exception as e:
        logging.error(f"Error loading PDF for split preview: {str(e)}")
        # Try the alternative HTML approach
        try:
            abs_path = os.path.abspath(pdf_path).replace('\\', '/')
            file_url = QUrl.fromLocalFile(abs_path).toString()

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>PDF Preview</title>
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
                    <object data="{file_url}" type="application/pdf" width="100%" height="100%">
                        <embed src="{file_url}" type="application/pdf" width="100%" height="100%">
                            <iframe src="{file_url}" width="100%" height="100%">
                                <p>Unable to display PDF. <a href="{file_url}">Click here to open</a>.</p>
                            </iframe>
                        </embed>
                    </object>
                </div>
            </body>
            </html>
            """

            # Load the HTML wrapper
            self.split_pdf_preview.setHtml(html_content, baseUrl=QUrl.fromLocalFile(os.path.dirname(abs_path)))
            return True

        except Exception as alt_error:
            logging.error(f"Error with alternative PDF loading in split preview: {str(alt_error)}")
            return False


def update_split_page_navigation(self):
    """Update the page navigation controls for split preview"""
    if not HAS_WEBENGINE or not hasattr(self, 'split_current_page'):
        return

    # Update the page indicator
    self.split_page_indicator.setText(f"Page: {self.split_current_page}")

    # Enable navigation buttons
    self.btn_split_prev_page.setEnabled(True)
    self.btn_split_next_page.setEnabled(True)


def split_prev_page(self):
    """Go to previous page in the split preview"""
    if not HAS_WEBENGINE or not hasattr(self, 'split_pdf_preview'):
        return

    # Execute JavaScript to scroll up (simulate previous page)
    self.split_pdf_preview.page().runJavaScript("window.scrollBy(0, -window.innerHeight);")

    if self.split_current_page > 1:
        self.split_current_page -= 1
        self.update_split_page_navigation()


def split_next_page(self):
    """Go to next page in the split preview"""
    if not HAS_WEBENGINE or not hasattr(self, 'split_pdf_preview'):
        return

    # Execute JavaScript to scroll down (simulate next page)
    self.split_pdf_preview.page().runJavaScript("window.scrollBy(0, window.innerHeight);")

    self.split_current_page += 1
    self.update_split_page_navigation()


def zoom_split_preview(self, delta):
    """Zoom the split preview by delta amount"""
    if not HAS_WEBENGINE or not hasattr(self, 'split_zoom_factor'):
        return

    current_zoom = self.split_zoom_factor.value()
    new_zoom = max(50, min(current_zoom + delta, 200))  # Clamp between 50% and 200%
    self.split_zoom_factor.setValue(new_zoom)


def apply_split_zoom(self):
    """Apply the current zoom factor to the split preview"""
    if not HAS_WEBENGINE or not hasattr(self, 'split_pdf_preview'):
        return

    zoom_value = self.split_zoom_factor.value() / 100.0
    # Apply zoom using JavaScript
    self.split_pdf_preview.page().runJavaScript(f"document.body.style.zoom = {zoom_value};")


def run_pytest():
    """Run pytest and capture errors."""
    import pytest
    result = pytest.main(["--maxfail=1", "--disable-warnings", "-q"])
    if result != 0:
        import logging
        logging.error("Pytest encountered errors.")
    return result

if __name__ == "__main__":
    run_pytest()
