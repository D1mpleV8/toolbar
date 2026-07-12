import os
import sys
import unittest
import time
from PyQt6.QtWidgets import QApplication

# Dynamic path injection
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from pctoolbox import config
from pctoolbox.threads.backend_sensors import BackendSensorsThread

# Ensure application exists
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestBackendSensors(unittest.TestCase):

    def test_low_level_telemetry_polling(self):
        """Test BackendSensorsThread polls successfully and maps correct keys."""
        thread = BackendSensorsThread(interval=0.2)
        results = []

        def on_telemetry(snapshot):
            results.append(snapshot)
            thread.stop()

        thread.telemetry_received.connect(on_telemetry)
        thread.start()
        thread.wait(2000)
        app.processEvents()

        thread.stop()
        thread.wait()
        app.processEvents()

        self.assertTrue(len(results) > 0)

        # Verify correctness of low-level hardware structures
        m = results[0]
        self.assertIn("cpu_perc", m)
        self.assertIn("cpu_temp", m)
        self.assertIn("gpu_perc", m)
        self.assertIn("gpu_temp", m)
        self.assertIn("ram_total", m)
        self.assertIn("ram_used", m)
        self.assertIn("ram_perc", m)
        self.assertIn("ssd_total", m)
        self.assertIn("ssd_used", m)
        self.assertIn("ssd_perc", m)

        # Assert correct conversions of bytes to Gigabytes
        self.assertTrue(m["ram_total"] > 0.0)
        self.assertTrue(m["ssd_total"] > 0.0)

if __name__ == "__main__":
    unittest.main()
