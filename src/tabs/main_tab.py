from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, 
    QSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar, 
    QListWidget, QFrame, QVBoxLayout, QHBoxLayout, QWidget, 
    QTabWidget, QScrollArea, QListWidgetItem, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

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
