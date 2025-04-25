# run_app.py
#!/usr/bin/env python3
import sys
import os


def get_base_path():
    if getattr(sys, "frozen", False):
        # one-file mode
        if hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS
        # one-dir mode
        return os.path.dirname(sys.executable)
    # normal execution
    return os.path.dirname(os.path.abspath(__file__))


# locate bundled src folder
_base = get_base_path()
_src = os.path.join(_base, "src")
if not os.path.isdir(_src):
    raise RuntimeError(f"Could not find bundled src/ directory at {_src}")
# make imports work
sys.path.insert(0, _src)

from PyQt6.QtWidgets import QApplication
from pdf_manage import PdfManager


def main():
    app = QApplication(sys.argv)
    window = PdfManager()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()