import os
import sys
import shutil
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
from pctoolbox.threads.smart_organizer import SmartOrganizerThread

# Ensure QApplication exists
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestSmartOrganizer(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for safe watching
        self.test_dir = tempfile.mkdtemp()
        self.logs_received = []
        self.rules_matched = []

    def tearDown(self):
        # Clean up files & folders
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def log_slot(self, msg):
        self.logs_received.append(msg)

    def rule_slot(self, rule):
        self.rules_matched.append(rule)

    def test_smart_organizer_thread_standard_extension_sorting(self):
        """Test standard/free extension-based sorting (Images, Videos, Docs)."""
        config.set_pro_version(False)

        thread = SmartOrganizerThread(watch_dir=self.test_dir)
        thread.log_msg.connect(self.log_slot)
        thread.rule_matched.connect(self.rule_slot)

        thread.start()
        # Allow thread to spin up watchdog observer
        time.sleep(0.5)
        app.processEvents()

        # 1. Create a dummy test image
        test_img = os.path.join(self.test_dir, "vacation.png")
        with open(test_img, "w") as f:
            f.write("mock png data")

        # Wait for watchdog to pick up the creation event
        time.sleep(1.0)
        app.processEvents()

        thread.stop()
        thread.wait()
        app.processEvents()

        # Check destination folders
        images_folder = os.path.join(self.test_dir, "Images")
        self.assertTrue(os.path.exists(images_folder))
        self.assertTrue(os.path.exists(os.path.join(images_folder, "vacation.png")))
        self.assertIn("Images", self.rules_matched)

    def test_smart_organizer_thread_pro_regex_rule(self):
        """Test pro regex filename matching when IS_PRO_VERSION is True."""
        config.set_pro_version(True)

        thread = SmartOrganizerThread(watch_dir=self.test_dir)
        thread.log_msg.connect(self.log_slot)
        thread.rule_matched.connect(self.rule_slot)

        thread.start()
        time.sleep(0.5)
        app.processEvents()

        # 1. Create a dummy file that matches the "screenshot.*" pattern
        screenshot_file = os.path.join(self.test_dir, "screenshot_2024.png")
        with open(screenshot_file, "w") as f:
            f.write("screenshot pixels")

        time.sleep(1.0)
        app.processEvents()

        thread.stop()
        thread.wait()
        app.processEvents()

        # Verify routed to premium Screenshots folder instead of standard Images
        screenshots_folder = os.path.join(self.test_dir, "Screenshots")
        self.assertTrue(os.path.exists(screenshots_folder))
        self.assertTrue(os.path.exists(os.path.join(screenshots_folder, "screenshot_2024.png")))
        self.assertIn("Screenshots", self.rules_matched)

    def test_smart_organizer_thread_pro_deep_scan(self):
        """Test deep content scanning to sort invoices by reading content."""
        config.set_pro_version(True)

        thread = SmartOrganizerThread(watch_dir=self.test_dir)
        thread.log_msg.connect(self.log_slot)
        thread.rule_matched.connect(self.rule_slot)

        thread.start()
        time.sleep(0.5)
        app.processEvents()

        # Create a text document containing the word "Invoice"
        doc_file = os.path.join(self.test_dir, "company_billing_data.txt")
        with open(doc_file, "w", encoding="utf-8") as f:
            f.write("This is a confidential Billing Invoice for consulting services.")

        time.sleep(1.0)
        app.processEvents()

        thread.stop()
        thread.wait()
        app.processEvents()

        # Verify routed to Invoices instead of standard Docs
        invoices_folder = os.path.join(self.test_dir, "Invoices")
        self.assertTrue(os.path.exists(invoices_folder))
        self.assertTrue(os.path.exists(os.path.join(invoices_folder, "company_billing_data.txt")))
        self.assertIn("Invoices", self.rules_matched)

if __name__ == "__main__":
    unittest.main()
