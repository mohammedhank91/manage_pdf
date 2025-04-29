from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, 
    QSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar, 
    QListWidget, QFrame, QVBoxLayout, QHBoxLayout, QWidget, 
    QTabWidget, QScrollArea, QListWidgetItem, QGridLayout, QGroupBox, QLineEdit, QRadioButton, QInputDialog
)
from PyQt6.QtCore import Qt

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
