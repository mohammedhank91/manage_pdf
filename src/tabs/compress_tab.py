from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, 
    QSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar, 
    QListWidget, QFrame, QVBoxLayout, QHBoxLayout, QWidget, 
    QTabWidget, QScrollArea, QListWidgetItem, QGridLayout, QGroupBox, QLineEdit, QRadioButton, QInputDialog,
    QSizePolicy
)
from PyQt6.QtCore import Qt

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
    
    # Set stretch factors for equal distribution
    steps_widget = QWidget()
    steps_widget.setLayout(steps_layout)
    steps_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    # Step 1: Select PDF
    select_pdf_panel = QFrame()
    select_pdf_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
    select_pdf_panel.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #e0e0e0; padding: 15px;")
    select_pdf_panel.setMinimumHeight(260)  # Minimum height
    select_pdf_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Allow expansion
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
    self.btn_select_pdf.setToolTip("Browse and select a PDF file from your computer to compress")
    select_pdf_layout.addWidget(self.btn_select_pdf)
    
    # Add step 1 panel to horizontal layout
    steps_layout.addWidget(select_pdf_panel)
    
    # Step 2: Compress PDF
    compression_panel = QFrame()
    compression_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
    compression_panel.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #e0e0e0; padding: 15px;")
    compression_panel.setMinimumHeight(260)  # Minimum height
    compression_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Allow expansion
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
    self.compression_profile.setToolTip("Choose compression level: Higher quality preserves details but larger file size")
    compress_options_layout.addWidget(self.compression_profile)

    compression_layout.addLayout(compress_options_layout)
    
    # Compress PDF button
    self.btn_compress = QPushButton("Compress PDF")
    self.btn_compress.setObjectName("btn_compress")
    self.btn_compress.clicked.connect(self.compress_pdf)
    self.btn_compress.setFixedHeight(50)
    self.btn_compress.setStyleSheet("color: white; background-color: #9c27b0; font-weight: bold;")
    self.btn_compress.setEnabled(False)  # Disabled until PDF is created or selected
    self.btn_compress.setToolTip("Compress the selected PDF file using the chosen quality settings")
    compression_layout.addWidget(self.btn_compress)
    
    # Add step 2 panel to horizontal layout
    steps_layout.addWidget(compression_panel)
    
    # Step 3: Use PDF
    actions_panel = QFrame()
    actions_panel.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
    actions_panel.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #e0e0e0; padding: 15px;")
    actions_panel.setMinimumHeight(260)  # Minimum height
    actions_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Allow expansion
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
    self.btn_preview_pdf.setToolTip("Preview the compressed PDF file before saving or printing")
    pdf_actions.addWidget(self.btn_preview_pdf)
    
    # Print PDF button
    self.btn_print_pdf = QPushButton("Print PDF")
    self.btn_print_pdf.setObjectName("btn_print_pdf")
    self.btn_print_pdf.clicked.connect(self.print_pdf)
    self.btn_print_pdf.setFixedHeight(50)
    self.btn_print_pdf.setStyleSheet("color: white; background-color: #03a9f4; font-weight: bold;")
    self.btn_print_pdf.setEnabled(False)
    self.btn_print_pdf.setToolTip("Send the compressed PDF file directly to your printer")
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
