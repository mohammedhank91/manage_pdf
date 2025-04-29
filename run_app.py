#!/usr/bin/env python3
import os
import sys
from src.pdf_manage import PdfManager, QApplication
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PdfManager()
    window.show()
    sys.exit(app.exec()) 