from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, 
    QSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar, 
    QListWidget, QFrame, QVBoxLayout, QHBoxLayout, QWidget, 
    QTabWidget, QScrollArea, QListWidgetItem, QGridLayout, QGroupBox, QLineEdit, QRadioButton, QInputDialog
)
from PyQt6.QtCore import Qt

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
