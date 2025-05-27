

def apply_modern_style(self):
    """Apply a modern style to the entire application"""
    # Main style for the app
    self.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #f8f9fa;
            color: #212529;
            font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
            font-size: 9pt;
        }
        
        QTabWidget::pane {
            border: 1px solid #dee2e6;
            border-radius: 12px;
            background-color: white;
            padding: 8px;
        }
        
        QTabBar::tab {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f8f9fa, stop: 1 #e9ecef);
            color: #6c757d;
            border: 1px solid #dee2e6;
            border-bottom: none;
            padding: 8px 16px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            min-width: 100px;
            font-weight: 600;
            font-size: 9pt;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 white, stop: 1 #f8f9fa);
            color: #0d6efd;
            border-bottom: 2px solid #0d6efd;
            font-weight: 700;
        }
        
        QTabBar::tab:hover:!selected {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #ffffff, stop: 1 #f1f3f4);
            color: #495057;
            border-color: #adb5bd;
        }
        
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0d6efd, stop: 1 #0b5ed7);
            color: white;
            border: 1px solid #0b5ed7;
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: 600;
            font-size: 9pt;
            min-height: 16px;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0b5ed7, stop: 1 #0a58ca);
            border: 1px solid #0a58ca;
        }
        
        QPushButton:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0a58ca, stop: 1 #084298);
            border: 1px solid #084298;
        }
        
        QPushButton:disabled {
            background: #6c757d;
            color: #adb5bd;
            border: 1px solid #6c757d;
        }
        
        /* Specific button styles with modern colors */
        QPushButton[objectName="btn_convert"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #198754, stop: 1 #157347);
            border: 1px solid #157347;
        }
        
        QPushButton[objectName="btn_convert"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #157347, stop: 1 #146c43);
            border: 1px solid #146c43;
        }
        
        QPushButton[objectName="btn_compress"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #6f42c1, stop: 1 #59359a);
            border: 1px solid #59359a;
        }
        
        QPushButton[objectName="btn_compress"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #59359a, stop: 1 #4c2d83);
            border: 1px solid #4c2d83;
        }
        
        QPushButton[objectName="btn_extract_pages"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #198754, stop: 1 #157347);
            border: 1px solid #157347;
        }
        
        QPushButton[objectName="btn_extract_pages"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #157347, stop: 1 #146c43);
            border: 1px solid #146c43;
        }
        
        QPushButton[objectName="btn_merge_pdfs"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #fd7e14, stop: 1 #e8681c);
            border: 1px solid #e8681c;
        }
        
        QPushButton[objectName="btn_merge_pdfs"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #e8681c, stop: 1 #dc5f26);
            border: 1px solid #dc5f26;
        }
        
        QPushButton[objectName="btn_delete"], QPushButton[objectName="btn_remove_pdf"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #dc3545, stop: 1 #bb2d3b);
            border: 1px solid #bb2d3b;
        }
        
        QPushButton[objectName="btn_delete"]:hover, QPushButton[objectName="btn_remove_pdf"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #bb2d3b, stop: 1 #a02834);
            border: 1px solid #a02834;
        }
        
        QPushButton[objectName="btn_preview_pdf"], QPushButton[objectName="btn_print_pdf"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0dcaf0, stop: 1 #31d2f2);
            border: 1px solid #0dcaf0;
            color: #212529;
        }
        
        QPushButton[objectName="btn_preview_pdf"]:hover, QPushButton[objectName="btn_print_pdf"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #31d2f2, stop: 1 #52ddf3);
            border: 1px solid #0dcaf0;
            color: #212529;
        }
        
        /* Selection button styles - modern blue gradient */
        QPushButton#btn_select, QPushButton#btn_select_pdf, QPushButton#btn_select_pdf_to_split, QPushButton#btn_add_pdf {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0d6efd, stop: 1 #0b5ed7);
            border: 1px solid #0b5ed7;
        }
        
        QPushButton#btn_select:hover, QPushButton#btn_select_pdf:hover, 
        QPushButton#btn_select_pdf_to_split:hover, QPushButton#btn_add_pdf:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0b5ed7, stop: 1 #0a58ca);
            border: 1px solid #0a58ca;
        }
        
        /* Navigation button styles - modern gray gradient */
        QPushButton#btn_prev, QPushButton#btn_next, QPushButton#btn_up, QPushButton#btn_down,
        QPushButton#btn_move_pdf_up, QPushButton#btn_move_pdf_down {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #6c757d, stop: 1 #5c636a);
            border: 1px solid #5c636a;
            padding: 4px 8px;
        }
        
        QPushButton#btn_prev:hover, QPushButton#btn_next:hover, QPushButton#btn_up:hover, QPushButton#btn_down:hover,
        QPushButton#btn_move_pdf_up:hover, QPushButton#btn_move_pdf_down:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #5c636a, stop: 1 #495057);
            border: 1px solid #495057;
        }
        
        /* Quick selection button styles with modern info color */
        QPushButton[text="All Pages"], QPushButton[text="Even Pages"], QPushButton[text="Odd Pages"],
        QPushButton[text="All"], QPushButton[text="Even"], QPushButton[text="Odd"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0dcaf0, stop: 1 #31d2f2);
            border: 1px solid #0dcaf0;
            color: #212529;
            padding: 4px 8px;
        }
        
        QPushButton[text="All Pages"]:hover, QPushButton[text="Even Pages"]:hover, QPushButton[text="Odd Pages"]:hover,
        QPushButton[text="All"]:hover, QPushButton[text="Even"]:hover, QPushButton[text="Odd"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #31d2f2, stop: 1 #52ddf3);
            border: 1px solid #0dcaf0;
            color: #212529;
        }
        
        QLabel {
            color: #495057;
            font-size: 9pt;
        }
        
        QLabel[objectName="statusLabel"] {
            color: #0d6efd;
            font-weight: 600;
            padding: 6px 12px;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                      stop: 0 rgba(13, 110, 253, 0.1), 
                                      stop: 1 rgba(13, 110, 253, 0.05));
            border: 1px solid rgba(13, 110, 253, 0.2);
            border-radius: 6px;
        }
        
        QProgressBar {
            border: 1px solid #dee2e6;
            border-radius: 6px;
            background-color: #f8f9fa;
            text-align: center;
            height: 20px;
            font-weight: 600;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                      stop: 0 #0d6efd, stop: 1 #6610f2);
            border-radius: 5px;
            margin: 1px;
        }
        
        QSpinBox, QComboBox, QLineEdit {
            border: 1px solid #ced4da;
            border-radius: 6px;
            padding: 6px 10px;
            background-color: white;
            font-size: 9pt;
            selection-background-color: #0d6efd;
            selection-color: white;
        }
        
        QSpinBox:hover, QComboBox:hover, QLineEdit:hover {
            border: 1px solid #86b7fe;
        }
        
        QSpinBox:focus, QComboBox:focus, QLineEdit:focus {
            border: 1px solid #86b7fe;
            outline: none;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #ced4da;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            background-color: #f8f9fa;
        }
        
        QComboBox::drop-down:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #e9ecef, stop: 1 #f8f9fa);
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid #495057;
            width: 0px;
            height: 0px;
        }
        
        QListWidget {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            background-color: white;
            font-size: 9pt;
            padding: 4px;
            alternate-background-color: #f8f9fa;
        }
        
        QListWidget::item {
            padding: 8px 12px;
            border-bottom: 1px solid #f1f3f4;
            border-radius: 4px;
            margin: 1px;
        }
        
        QListWidget::item:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f8f9fa, stop: 1 #e9ecef);
            border: 1px solid #dee2e6;
        }
        
        QListWidget::item:selected {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #cfe2ff, stop: 1 #b6d7ff);
            color: #0d6efd;
            border: 1px solid #86b7fe;
            font-weight: 600;
        }
        
        QCheckBox {
            spacing: 6px;
            font-size: 9pt;
        }
        
        QCheckBox:hover {
            color: #0d6efd;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QCheckBox::indicator:unchecked {
            border: 2px solid #ced4da;
            background-color: white;
            border-radius: 4px;
        }
        
        QCheckBox::indicator:unchecked:hover {
            border: 2px solid #86b7fe;
        }
        
        QCheckBox::indicator:checked {
            border: 2px solid #0d6efd;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0d6efd, stop: 1 #0b5ed7);
            border-radius: 4px;
        }
        
        QCheckBox::indicator:checked:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0b5ed7, stop: 1 #0a58ca);
        }
        
        QFrame[frameShape="4"] {
            color: #dee2e6;
            margin: 10px 0px;
        }
        
        /* Modern header styles with better typography */
        QLabel[objectName="main_header"], QLabel[objectName="convert_header"], 
        QLabel[objectName="tools_header"], QLabel[objectName="merge_header"],
        QLabel[objectName="split_header"] {
            font-size: 16pt;
            font-weight: 700;
            color: #0d6efd;
            padding: 8px 0px;
            letter-spacing: 0.5px;
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
