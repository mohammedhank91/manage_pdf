#!/usr/bin/env python3
import os
import sys
# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# Import and run the main application
from src.pdf_manage import PdfManager, QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PdfManager()
    window.show()
    sys.exit(app.exec()) 