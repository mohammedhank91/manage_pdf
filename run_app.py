#!/usr/bin/env python3
import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import and run the main application
from pdf_manage import PdfManager, QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PdfManager()
    window.show()
    sys.exit(app.exec()) 