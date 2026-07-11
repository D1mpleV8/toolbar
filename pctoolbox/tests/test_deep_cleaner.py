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
from pctoolbox.threads.registry_cleaner import RegistryCleanerThread
from pctoolbox.threads.secure_shredder import SecureShredderThread

# Ensure application exists
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestDeepCleaner(unittest.TestCase):

    def test_registry_residue_scanner(self):
        """Test scanning registry leftovers completes and emits valid lists."""
        thread = RegistryCleanerThread()
        results = []

        def on_completed(leftovers):
            results.extend(leftovers)

        thread.scan_completed.connect(on_completed)
        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["type"], "AppData Folder")

    def test_secure_shredder_locked_when_free(self):
        """Test SecureShredder emits unauthorized signal on free license."""
        config.set_pro_version(False)

        # Create temporary file to try to shred
        temp_fd, temp_path = tempfile.mkstemp()
        os.close(temp_fd)

        try:
            thread = SecureShredderThread(temp_path)
            results = {"unauthorized": False}

            def on_unauth():
                results["unauthorized"] = True

            thread.unauthorized.connect(on_unauth)
            thread.start()
            thread.wait(2000)
            app.processEvents()

            self.assertTrue(results["unauthorized"])
            # File must still exist because execution was blocked
            self.assertTrue(os.path.exists(temp_path))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_secure_shredder_destruction_when_pro(self):
        """Test SecureShredder overwrites 7 times and destroys the file on Pro license."""
        config.set_pro_version(True)

        # Create dummy file with sensitive contents
        temp_fd, temp_path = tempfile.mkstemp()
        os.close(temp_fd)

        with open(temp_path, "wb") as f:
            f.write(b"super_sensitive_financial_invoice_data_to_be_shredded_7_times")

        try:
            thread = SecureShredderThread(temp_path)
            results = {"completed": False, "success": False}

            def on_completed(success, desc):
                results["completed"] = True
                results["success"] = success

            thread.shred_completed.connect(on_completed)
            thread.start()
            thread.wait(3000)
            app.processEvents()

            self.assertTrue(results["completed"])
            self.assertTrue(results["success"])
            # The target file must be completely deleted/unlinked from disk
            self.assertFalse(os.path.exists(temp_path))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()
