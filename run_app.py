#!/usr/bin/env python3
import os
import sys
# Import and run the main application
from src.pdf_manage import PdfManager, QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PdfManager()
    window.show()
    sys.exit(app.exec()) 