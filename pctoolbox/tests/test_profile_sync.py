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
from pctoolbox.threads.profile_encryption import ProfileEncryptionThread
from pctoolbox.threads.cloud_sync import CloudSyncThread

# Ensure application exists
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestProfileSync(unittest.TestCase):

    def test_local_profile_encryption_and_decryption(self):
        """Test cryptographic encryption and decryption profile roundtrip on disk."""
        temp_fd, temp_profile_path = tempfile.mkstemp()
        os.close(temp_fd)

        test_data = {
            "test_coordinate_x": 312,
            "test_coordinate_y": 450,
            "theme": "mocha_catppuccin"
        }
        password = "PowerUserMasterPasswordKey"

        try:
            # 1. Test Encryption Export
            enc_thread = ProfileEncryptionThread("ENCRYPT", temp_profile_path, password, test_data)
            enc_results = {"completed": False, "success": False}

            def on_enc_completed(success, msg):
                enc_results["completed"] = True
                enc_results["success"] = success

            enc_thread.op_completed.connect(on_enc_completed)
            enc_thread.start()
            enc_thread.wait(2000)
            app.processEvents()

            self.assertTrue(enc_results["completed"])
            self.assertTrue(enc_results["success"])

            # Verify file is not plain text
            with open(temp_profile_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
                self.assertNotIn("mocha_catppuccin", raw_text)

            # 2. Test Decryption Import
            dec_thread = ProfileEncryptionThread("DECRYPT", temp_profile_path, password)
            dec_results = {"completed": False, "success": False, "data": {}}

            def on_dec_completed(success, msg):
                dec_results["completed"] = True
                dec_results["success"] = success

            def on_profile_loaded(data):
                dec_results["data"] = data

            dec_thread.op_completed.connect(on_dec_completed)
            dec_thread.profile_loaded.connect(on_profile_loaded)
            dec_thread.start()
            dec_thread.wait(2000)
            app.processEvents()

            self.assertTrue(dec_results["completed"])
            self.assertTrue(dec_results["success"])
            self.assertEqual(dec_results["data"]["theme"], "mocha_catppuccin")

        finally:
            if os.path.exists(temp_profile_path):
                os.remove(temp_profile_path)

    def test_cloud_sync_locked_when_free(self):
        """Test that CloudSyncThread fails immediately on Free license."""
        config.set_pro_version(False)

        thread = CloudSyncThread("UPLOAD", "dummy_token")
        results = {"unauthorized": False}

        def on_unauth():
            results["unauthorized"] = True

        thread.unauthorized.connect(on_unauth)
        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertTrue(results["unauthorized"])

    def test_cloud_sync_upload_and_download_when_pro(self):
        """Test cloud backup upload and download simulation when Pro active."""
        config.set_pro_version(True)

        # 1. Test upload
        test_settings = {"active_dns": "Cloudflare", "shred_passes": 7}
        up_thread = CloudSyncThread("UPLOAD", "ghp_mock_token_key_abc", data_to_upload=test_settings)
        up_results = {"completed": False, "success": False, "detail": ""}

        def on_up_completed(success, detail):
            up_results["completed"] = True
            up_results["success"] = success
            up_results["detail"] = detail

        up_thread.sync_completed.connect(on_up_completed)
        up_thread.start()
        up_thread.wait(3000)
        app.processEvents()

        self.assertTrue(up_results["completed"])
        self.assertTrue(up_results["success"])
        # Should return success code and simulated Gist ID
        self.assertIn("SUCCESS", up_results["detail"])

        # 2. Test download
        gist_id = "simulated_gist_id_102432"
        down_thread = CloudSyncThread("DOWNLOAD", "ghp_mock_token_key_abc", gist_id=gist_id)
        down_results = {"completed": False, "success": False, "data": {}}

        def on_down_completed(success, detail):
            down_results["completed"] = True
            down_results["success"] = success

        def on_downloaded(data):
            down_results["data"] = data

        down_thread.sync_completed.connect(on_down_completed)
        down_thread.profile_downloaded.connect(on_downloaded)
        down_thread.start()
        down_thread.wait(3000)
        app.processEvents()

        self.assertTrue(down_results["completed"])
        self.assertTrue(down_results["success"])
        self.assertEqual(down_results["data"]["active_dns"], "Cloudflare")

if __name__ == "__main__":
    unittest.main()
