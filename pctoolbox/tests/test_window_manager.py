import sys
import unittest
import time
from PyQt6.QtWidgets import QApplication

# Dynamic path injection
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from pctoolbox import config
from pctoolbox.threads.window_manager import WindowManagerThread
from pctoolbox.threads.osd_overlay import OSDOverlayThread

# Ensure application exists
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestWindowManager(unittest.TestCase):

    def test_window_scanning(self):
        """Test window tree scanning executes cleanly and returns structured data."""
        thread = WindowManagerThread()
        results = []

        def on_scanned(windows):
            results.extend(windows)

        thread.windows_scanned.connect(on_scanned)
        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertTrue(len(results) > 0)
        self.assertIn("hwnd", results[0])
        self.assertIn("title", results[0])

    def test_window_manipulation_methods(self):
        """Test static window pinning and transparency wrappers don't throw exceptions."""
        hwnd_id = 99999
        # Test always on top
        self.assertTrue(WindowManagerThread.set_always_on_top(hwnd_id, True))
        self.assertTrue(WindowManagerThread.set_always_on_top(hwnd_id, False))

        # Test opacity
        self.assertTrue(WindowManagerThread.set_window_transparency(hwnd_id, 80))

    def test_osd_locked_when_free(self):
        """Test OSDOverlayThread signals unauthorized on standard license."""
        config.set_pro_version(False)

        thread = OSDOverlayThread()
        results = {"unauthorized": False}

        def on_unauth():
            results["unauthorized"] = True

        thread.unauthorized.connect(on_unauth)
        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertTrue(results["unauthorized"])

    def test_osd_telemetry_changes_when_pro(self):
        """Test OSDOverlayThread gathers and transmits live hardware telemetry in Pro mode."""
        config.set_pro_version(True)

        thread = OSDOverlayThread(update_interval=0.1)
        results = []

        def on_telemetry(metrics):
            results.append(metrics)
            if len(results) >= 2:
                thread.stop()

        thread.telemetry_changed.connect(on_telemetry)
        thread.start()
        thread.wait(3000)
        app.processEvents()

        thread.stop()
        thread.wait()
        app.processEvents()

        self.assertTrue(len(results) > 0)
        self.assertIn("fps", results[0])
        self.assertIn("cpu_temp", results[0])

if __name__ == "__main__":
    unittest.main()
