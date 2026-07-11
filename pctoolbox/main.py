import os
import sys
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
