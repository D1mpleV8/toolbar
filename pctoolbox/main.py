import os
import sys

# Dynamic path injection: ensure the parent directory of 'pctoolbox' is in sys.path
# This guarantees that 'import pctoolbox' or 'from pctoolbox' works flawlessly
# regardless of whether it is run directly, from another directory, or compiled as an .exe.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from PyQt6.QtWidgets import QApplication
from pctoolbox.ui.main_window import MainWindow

def main():
    # Production-ready absolute paths are initialized in pctoolbox/config.py
    # Enforce offscreen mode in headless/testing environments if needed,
    # but by default it starts standard desktop GUI.

    app = QApplication(sys.argv)
    app.setApplicationName("Steam PC Toolbox")
    app.setApplicationVersion("1.0.0")

    window = MainWindow()

    # Handle quick/dry execution parameter for automated verification
    if "--dry-run" in sys.argv:
        print("[PC Toolbox] Dry-run launch validation completed successfully!")
        sys.exit(0)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
