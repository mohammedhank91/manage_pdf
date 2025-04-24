from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, 
    QSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar, 
    QListWidget, QFrame, QVBoxLayout, QHBoxLayout, QWidget, 
    QTabWidget, QScrollArea, QListWidgetItem, QGridLayout, QGroupBox, QLineEdit, QRadioButton, QInputDialog
)
from PyQt6.QtCore import Qt
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
    self.num_margin.setSingleStep(1)
    self.num_margin.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
    self.num_margin.setStyleSheet("""
        QSpinBox {
            padding: 4px;
            border: 1px solid #100101;
            border-radius: 3px;
        }
        QSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 16px;
            border-left: 1px solid #090707;
            border-top-right-radius: 3px;
        }
        QSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 16px;
            border-left: 1px solid #090707;
            border-bottom-right-radius: 3px;
        }
        QSpinBox::up-arrow {
            width: 8px;
            height: 8px;
            border-bottom: 5px solid #000000;
            border-right: 4px solid transparent;
            border-left: 4px solid transparent;
        }
        QSpinBox::down-arrow {
            width: 8px;
            height: 8px;
            border-top: 5px solid #000000;
            border-right: 4px solid transparent;
            border-left: 4px solid transparent;
        }
    """)
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