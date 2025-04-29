

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
