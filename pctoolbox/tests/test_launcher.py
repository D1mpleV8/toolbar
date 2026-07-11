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
from pctoolbox.threads.quick_launcher import QuickLauncherThread

# Ensure application exists
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestQuickLauncher(unittest.TestCase):

    def test_local_app_and_file_indexing(self):
        """Test local app/settings search matches correctly."""
        thread = QuickLauncherThread(query="Steam")

        results = []
        def handle_results(res):
            results.extend(res)

        thread.search_completed.connect(handle_results)
        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["name"], "Steam Client")
        self.assertEqual(results[0]["type"], "App")

    def test_ai_search_locked_when_free(self):
        """Test asking GPT-4 (?) returns a PRO LOCKED card on standard license."""
        config.set_pro_version(False)
        thread = QuickLauncherThread(query="? how to increase FPS")

        results = []
        def handle_results(res):
            results.extend(res)

        thread.search_completed.connect(handle_results)
        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], "PRO LOCKED")
        self.assertEqual(results[0]["path"], "PRO_LOCKED")

    def test_ai_search_unlocked_when_pro(self):
        """Test asking GPT-4 (?) works and returns AI answers when Pro is active."""
        config.set_pro_version(True)
        thread = QuickLauncherThread(query="? clean")

        results = []
        def handle_results(res):
            results.extend(res)

        thread.search_completed.connect(handle_results)
        thread.start()
        thread.wait(3000)
        app.processEvents()

        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0]["type"], "ChatGPT Response")
        self.assertIn("System cleaning removes browser", results[0]["name"])

if __name__ == "__main__":
    unittest.main()
