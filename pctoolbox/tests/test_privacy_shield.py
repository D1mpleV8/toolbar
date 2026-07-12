import os
import sys
import tempfile
import unittest
import time
from PyQt6.QtWidgets import QApplication

# Dynamic path injection
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from pctoolbox import config
from pctoolbox.threads.privacy_registry import PrivacyRegistryThread
from pctoolbox.threads.tracker_blocker import TrackerBlockerThread

# Ensure application exists
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestPrivacyShield(unittest.TestCase):

    def test_registry_telemetry_toggles(self):
        """Test Registry Privacy policy threads complete successfully."""
        thread = PrivacyRegistryThread("Windows Telemetry", True)
        results = {"completed": False, "success": False}

        def on_completed(success, desc):
            results["completed"] = True
            results["success"] = success

        thread.op_completed.connect(on_completed)
        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertTrue(results["completed"])
        self.assertTrue(results["success"])

    def test_tracker_blocker_locked_when_free(self):
        """Test Hosts blocker thread triggers unauthorized on standard license."""
        config.set_pro_version(False)

        thread = TrackerBlockerThread(True)
        results = {"unauthorized": False}

        def on_unauth():
            results["unauthorized"] = True

        thread.unauthorized.connect(on_unauth)
        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertTrue(results["unauthorized"])

    def test_tracker_blocker_file_mod_when_pro(self):
        """Test Hosts blocker file manipulation and restoration loop under Pro license."""
        config.set_pro_version(True)

        # Setup temporary mock hosts file to let the thread actually modify it
        temp_fd, temp_hosts_path = tempfile.mkstemp()
        os.close(temp_fd)

        try:
            # Seed with base standard hosts entries
            with open(temp_hosts_path, "w", encoding="utf-8") as f:
                f.write("127.0.0.1 localhost\n::1 localhost\n")

            thread = TrackerBlockerThread(True)
            # Inject our temporary mock hosts file path directly to bypass read-only OS paths
            thread.hosts_path = temp_hosts_path

            results = {"completed": False, "success": False}

            def on_completed(success, desc):
                results["completed"] = True
                results["success"] = success

            thread.block_completed.connect(on_completed)
            thread.start()
            thread.wait(3000)
            app.processEvents()

            self.assertTrue(results["completed"])
            self.assertTrue(results["success"])

            # Verify the IP block entries are physically present in the temp file
            with open(temp_hosts_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("# --- STEAM PC TOOLBOX PRIVACY SHIELD START ---", content)
                self.assertIn("0.0.0.0 telemetry.microsoft.com", content)

            # Test deactivation / cleanup loop
            deact_thread = TrackerBlockerThread(False)
            deact_thread.hosts_path = temp_hosts_path

            deact_results = {"completed": False, "success": False}

            def on_deact_completed(success, desc):
                deact_results["completed"] = True
                deact_results["success"] = success

            deact_thread.block_completed.connect(on_deact_completed)
            deact_thread.start()
            deact_thread.wait(3000)
            app.processEvents()

            self.assertTrue(deact_results["completed"])
            self.assertTrue(deact_results["success"])

            # Verify block entries were completely removed
            with open(temp_hosts_path, "r", encoding="utf-8") as f:
                deact_content = f.read()
                self.assertNotIn("# --- STEAM PC TOOLBOX PRIVACY SHIELD START ---", deact_content)
                self.assertNotIn("telemetry.microsoft.com", deact_content)

        finally:
            if os.path.exists(temp_hosts_path):
                os.remove(temp_hosts_path)

if __name__ == "__main__":
    unittest.main()
