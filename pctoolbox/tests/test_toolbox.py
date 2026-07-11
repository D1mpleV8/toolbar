import os
import sys

# Dynamic path injection
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import unittest
import time
from PyQt6.QtWidgets import QApplication

from pctoolbox import config
from pctoolbox.threads.cleaner import CleanerThread
from pctoolbox.threads.optimizer import OptimizerThread
from pctoolbox.threads.macro import MacroThread

# A single global QApplication instance must exist for QObjects and signals/slots to work
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestPCToolboxCore(unittest.TestCase):

    def setUp(self):
        # Reset licensing state to False before each test
        config.set_pro_version(False)

    def test_config_paths_and_licensing(self):
        """Test config dynamic path resolution and license toggle behavior."""
        # Ensure that get_asset_path resolves an absolute path
        app_icon_path = config.get_asset_path("app_icon.png")
        self.assertTrue(os.path.isabs(app_icon_path))
        self.assertTrue(app_icon_path.endswith("app_icon.png"))

        # Test Default State
        self.assertFalse(config.IS_PRO_VERSION)

        # Test Toggle State
        config.set_pro_version(True)
        self.assertTrue(config.IS_PRO_VERSION)

        config.set_pro_version(False)
        self.assertFalse(config.IS_PRO_VERSION)

    def test_cleaner_thread_free(self):
        """Test that CleanerThread runs and emits correct signals without UI freezing."""
        # Setup thread with standard parameters
        thread = CleanerThread(clean_temp=True, clean_cache=False, clean_logs=False)

        signals_received = {
            "progress": [],
            "status": [],
            "finished": False
        }

        def handle_progress(p):
            signals_received["progress"].append(p)
            # Speed up the test by stopping early or just logging
            if p >= 50:
                thread.stop()

        def handle_status(s):
            signals_received["status"].append(s)

        def handle_finished(summary):
            signals_received["finished"] = True

        thread.progress.connect(handle_progress)
        thread.status.connect(handle_status)
        thread.finished_summary.connect(handle_finished)

        # Start and block-wait (with safety timeout)
        thread.start()
        start_time = time.time()
        while thread.isRunning() and (time.time() - start_time) < 3.0:
            app.processEvents()
            time.sleep(0.05)

        # Stop if still running
        thread.stop()
        thread.wait()
        app.processEvents()

        self.assertTrue(len(signals_received["status"]) > 0)
        self.assertTrue(len(signals_received["progress"]) > 0)

    def test_optimizer_thread_locked_when_free(self):
        """Test that OptimizerThread terminates and signals unauthorized when IS_PRO_VERSION is False."""
        config.set_pro_version(False)

        thread = OptimizerThread(optimize_ram=True)

        signals_received = {
            "unauthorized": False,
            "finished_summary": False
        }

        def handle_unauth():
            signals_received["unauthorized"] = True

        def handle_finished(summary):
            signals_received["finished_summary"] = True

        thread.unauthorized.connect(handle_unauth)
        thread.finished_summary.connect(handle_finished)

        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertTrue(signals_received["unauthorized"])
        self.assertFalse(signals_received["finished_summary"])

    def test_optimizer_thread_unlocked_when_pro(self):
        """Test that OptimizerThread executes successfully when IS_PRO_VERSION is True."""
        config.set_pro_version(True)

        thread = OptimizerThread(optimize_ram=True, prioritize_gpu=False, clean_ram=False)

        signals_received = {
            "progress": [],
            "status": [],
            "finished_summary": False
        }

        def handle_progress(p):
            signals_received["progress"].append(p)
            if p >= 30:
                thread.stop()

        def handle_status(s):
            signals_received["status"].append(s)

        def handle_finished(summary):
            signals_received["finished_summary"] = True

        thread.progress.connect(handle_progress)
        thread.status.connect(handle_status)
        thread.finished_summary.connect(handle_finished)

        thread.start()
        start_time = time.time()
        while thread.isRunning() and (time.time() - start_time) < 3.0:
            app.processEvents()
            time.sleep(0.05)

        thread.stop()
        thread.wait()
        app.processEvents()

        self.assertTrue(len(signals_received["status"]) > 0)

    def test_macro_thread_locked_when_free(self):
        """Test that MacroThread terminates and signals unauthorized when IS_PRO_VERSION is False."""
        config.set_pro_version(False)

        thread = MacroThread()

        signals_received = {
            "unauthorized": False
        }

        def handle_unauth():
            signals_received["unauthorized"] = True

        thread.unauthorized.connect(handle_unauth)

        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertTrue(signals_received["unauthorized"])

if __name__ == "__main__":
    unittest.main()
