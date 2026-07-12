import os
import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QFrame, QLineEdit, QFileDialog)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from pctoolbox import config
from pctoolbox.threads.profile_encryption import ProfileEncryptionThread
from pctoolbox.threads.cloud_sync import CloudSyncThread

class ProfileSyncView(QWidget):
    """
    Sleek Profile & Sync tab view.
    Fulfills standard local AES encrypted manual backup export/import,
    and gates dynamic Cloud instant sync on standard free version.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.encrypt_thread = None
        self.cloud_thread = None
        self.init_ui()

    def init_ui(self):
        # Two-Column Master Layout (Left: Local backups, Right: Cloud sync)
        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(15, 15, 15, 15)
        master_layout.setSpacing(15)

        # Left Column: Standard Free Encrypted Profiles
        left_pane = QFrame()
        left_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)

        free_title = QLabel("🔐 Encrypted Profile Backups")
        free_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        free_title.setStyleSheet("color: #89b4fa; border: none;")
        left_layout.addWidget(free_title)

        desc = QLabel("Backup and lock macro coordinates, hotkeys, and app preferences into a password-secured local JSON file.")
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #a6adc8; border: none;")
        desc.setWordWrap(True)
        left_layout.addWidget(desc)

        # Password Entry Row
        pass_lbl = QLabel("Backup Key Password:")
        pass_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        pass_lbl.setStyleSheet("color: #cdd6f4; border: none; background: transparent;")
        left_layout.addWidget(pass_lbl)

        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Enter password to lock/unlock profiles...")
        self.txt_password.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        left_layout.addWidget(self.txt_password)

        # Local Actions
        btn_row = QHBoxLayout()
        self.btn_export = QPushButton("Export Profile")
        self.btn_export.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #11111b;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
            }
        """)
        self.btn_export.clicked.connect(self.export_encrypted_profile)
        btn_row.addWidget(self.btn_export)

        self.btn_import = QPushButton("Import Profile")
        self.btn_import.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_import.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #cba6f7;
                color: #11111b;
            }
        """)
        self.btn_import.clicked.connect(self.import_encrypted_profile)
        btn_row.addWidget(self.btn_import)
        btn_row.addStretch()
        left_layout.addLayout(btn_row)

        # Local action logs
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Consolas", 8))
        self.log_console.setStyleSheet("""
            QTextEdit {
                background-color: #11111b;
                border: 1px solid #313244;
                color: #a6e3a1;
                border-radius: 6px;
            }
        """)
        self.log_console.setMaximumHeight(140)
        left_layout.addWidget(self.log_console)

        master_layout.addWidget(left_pane, 3)

        # Right Column: Premium Cloud Sync (Pro feature)
        self.right_pane = QFrame()
        self.right_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        self.right_master_layout = QVBoxLayout(self.right_pane)
        self.right_master_layout.setContentsMargins(0, 0, 0, 0)

        # Pro controls widget
        self.pro_control_widget = QWidget()
        pro_layout = QVBoxLayout(self.pro_control_widget)
        pro_layout.setContentsMargins(15, 15, 15, 15)
        pro_layout.setSpacing(12)

        pro_title = QLabel("☁️ Cloud API Synchronization")
        pro_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        pro_title.setStyleSheet("color: #fab387; border: none;")
        pro_layout.addWidget(pro_title)

        pro_desc = QLabel("Instantly back up and restore configurations via GitHub Gists or Google Drive automatically upon logging into Steam on any machine.")
        pro_desc.setWordWrap(True)
        pro_desc.setFont(QFont("Segoe UI", 9))
        pro_desc.setStyleSheet("color: #a6adc8; border: none;")
        pro_layout.addWidget(pro_desc)

        # Auth Token
        token_lbl = QLabel("GitHub Personal Token:")
        token_lbl.setFont(QFont("Segoe UI", 8))
        token_lbl.setStyleSheet("color: #cdd6f4; border: none;")
        pro_layout.addWidget(token_lbl)

        self.txt_token = QLineEdit()
        self.txt_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_token.setPlaceholderText("ghp_********************************")
        self.txt_token.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        pro_layout.addWidget(self.txt_token)

        # Gist ID
        gist_lbl = QLabel("Cloud Gist Container ID:")
        gist_lbl.setFont(QFont("Segoe UI", 8))
        gist_lbl.setStyleSheet("color: #cdd6f4; border: none;")
        pro_layout.addWidget(gist_lbl)

        self.txt_gist_id = QLineEdit()
        self.txt_gist_id.setPlaceholderText("Existing Gist ID (Optional for Upload)")
        self.txt_gist_id.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        pro_layout.addWidget(self.txt_gist_id)

        # Trigger buttons
        cloud_btn_lay = QHBoxLayout()
        self.btn_cloud_upload = QPushButton("Sync to Cloud")
        self.btn_cloud_upload.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_cloud_upload.setStyleSheet("""
            QPushButton {
                background-color: #fab387;
                color: #11111b;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
            }
        """)
        self.btn_cloud_upload.clicked.connect(self.sync_up_to_cloud)
        cloud_btn_lay.addWidget(self.btn_cloud_upload)

        self.btn_cloud_download = QPushButton("Sync from Cloud")
        self.btn_cloud_download.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_cloud_download.setStyleSheet("""
            QPushButton {
                background-color: #fab387;
                color: #11111b;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #cba6f7;
                color: #11111b;
            }
        """)
        self.btn_cloud_download.clicked.connect(self.sync_down_from_cloud)
        cloud_btn_lay.addWidget(self.btn_cloud_download)
        pro_layout.addLayout(cloud_btn_lay)

        # Cloud log console
        self.cloud_console = QTextEdit()
        self.cloud_console.setReadOnly(True)
        self.cloud_console.setFont(QFont("Consolas", 8))
        self.cloud_console.setStyleSheet("""
            QTextEdit {
                background-color: #11111b;
                border: 1px solid #313244;
                color: #fab387;
                border-radius: 6px;
            }
        """)
        pro_layout.addWidget(self.cloud_console)

        self.right_master_layout.addWidget(self.pro_control_widget)

        # Right Column Overlay (Locked screen for Free users)
        self.lock_overlay = QFrame()
        self.lock_overlay.setStyleSheet("background-color: rgba(24, 24, 37, 235); border-radius: 8px;")
        overlay_layout = QVBoxLayout(self.lock_overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.setSpacing(10)

        self.lock_icon_lbl = QLabel()
        self.lock_icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lock_icon_lbl.setStyleSheet("border: none;")
        lock_pix = QPixmap(config.get_asset_path("lock.png"))
        if not lock_pix.isNull():
            self.lock_icon_lbl.setPixmap(lock_pix.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.lock_icon_lbl.setText("🔒")
            self.lock_icon_lbl.setFont(QFont("Segoe UI", 24))
        overlay_layout.addWidget(self.lock_icon_lbl)

        lock_title = QLabel("Locked feature")
        lock_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lock_title.setStyleSheet("color: #f38ba8; border: none;")
        lock_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_title)

        lock_desc = QLabel("Get Steam Pro version to unlock Instant Cloud API Sync and automatically deploy setups across multiple hardware profiles.")
        lock_desc.setWordWrap(True)
        lock_desc.setFont(QFont("Segoe UI", 8))
        lock_desc.setStyleSheet("color: #a6adc8; border: none;")
        lock_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_desc)

        self.right_master_layout.addWidget(self.lock_overlay)

        master_layout.addWidget(self.right_pane, 2)

        # Sync visual locking state
        self.refresh_ui()

    def export_encrypted_profile(self):
        password = self.txt_password.text().strip()
        if not password:
            self.log_console.append("[Backup] Error: Please enter a password key to lock the profile.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Encrypted Profile", os.path.expanduser("~"), "Encrypted config (*.json)")
        if file_path:
            self.btn_export.setEnabled(False)
            self.log_console.append("[Backup] Gathering current user settings layout...")

            # Compile simulated settings metrics
            user_settings = {
                "global_macros": True,
                "saved_coordinates": [312, 450],
                "active_dns": "Cloudflare",
                "shred_passes": 7,
                "created_epoch": int(time.time())
            }

            self.encrypt_thread = ProfileEncryptionThread("ENCRYPT", file_path, password, user_settings)
            self.encrypt_thread.status_msg.connect(lambda txt: self.log_console.append(f"[Backup] {txt}"))
            self.encrypt_thread.op_completed.connect(self.on_local_completed)
            self.encrypt_thread.start()

    def import_encrypted_profile(self):
        password = self.txt_password.text().strip()
        if not password:
            self.log_console.append("[Backup] Error: Password key required to decrypt the profile.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Open Encrypted Profile", os.path.expanduser("~"), "Encrypted config (*.json)")
        if file_path:
            self.btn_import.setEnabled(False)
            self.log_console.append("[Backup] Initializing decryption parser...")

            self.encrypt_thread = ProfileEncryptionThread("DECRYPT", file_path, password)
            self.encrypt_thread.status_msg.connect(lambda txt: self.log_console.append(f"[Backup] {txt}"))
            self.encrypt_thread.profile_loaded.connect(self.on_profile_loaded)
            self.encrypt_thread.op_completed.connect(self.on_local_completed)
            self.encrypt_thread.start()

    def on_local_completed(self, success: bool, msg: str):
        self.btn_export.setEnabled(True)
        self.btn_import.setEnabled(True)
        self.encrypt_thread = None

    def on_profile_loaded(self, config_dict: dict):
        self.log_console.append(f"\n[Backup] Loaded metrics: {config_dict}")

    def sync_up_to_cloud(self):
        token = self.txt_token.text().strip()
        gist_id = self.txt_gist_id.text().strip()
        if not token:
            self.cloud_console.append("[Cloud] Error: GitHub API Access token required.")
            return

        self.btn_cloud_upload.setEnabled(False)
        self.cloud_console.append("[Cloud] Assembling active config snapshot...")

        user_settings = {
            "global_macros": True,
            "saved_coordinates": [312, 450],
            "active_dns": "Cloudflare",
            "shred_passes": 7,
            "cloud_sync_time": int(time.time())
        }

        self.cloud_thread = CloudSyncThread("UPLOAD", token, gist_id, user_settings)
        self.cloud_thread.status_msg.connect(lambda txt: self.cloud_console.append(f"[Cloud] {txt}"))
        self.cloud_thread.sync_completed.connect(self.on_cloud_completed)
        self.cloud_thread.start()

    def sync_down_from_cloud(self):
        token = self.txt_token.text().strip()
        gist_id = self.txt_gist_id.text().strip()
        if not token:
            self.cloud_console.append("[Cloud] Error: GitHub API Access token required.")
            return
        if not gist_id:
            self.cloud_console.append("[Cloud] Error: Gist container ID required to download.")
            return

        self.btn_cloud_download.setEnabled(False)
        self.cloud_console.append("[Cloud] Connecting to repository stream...")

        self.cloud_thread = CloudSyncThread("DOWNLOAD", token, gist_id)
        self.cloud_thread.status_msg.connect(lambda txt: self.cloud_console.append(f"[Cloud] {txt}"))
        self.cloud_thread.profile_downloaded.connect(self.on_cloud_profile_downloaded)
        self.cloud_thread.sync_completed.connect(self.on_cloud_completed)
        self.cloud_thread.start()

    def on_cloud_completed(self, success: bool, res_detail: str):
        self.btn_cloud_upload.setEnabled(True)
        self.btn_cloud_download.setEnabled(True)
        self.cloud_thread = None

        if success and res_detail.startswith("SUCCESS:"):
            gist_id = res_detail.split(":")[1]
            self.txt_gist_id.setText(gist_id)

    def on_cloud_profile_downloaded(self, profile_dict: dict):
        self.cloud_console.append(f"\n⚡ [Cloud] Configuration pulled: {profile_dict}")

    def refresh_ui(self):
        if config.IS_PRO_VERSION:
            self.lock_overlay.hide()
            self.pro_control_widget.show()
        else:
            if self.cloud_thread and self.cloud_thread.isRunning():
                self.cloud_thread.stop()
            self.pro_control_widget.hide()
            self.lock_overlay.show()

    def stop_all_workers(self):
        if self.encrypt_thread and self.encrypt_thread.isRunning():
            self.encrypt_thread.stop()
            self.encrypt_thread.wait()
        if self.cloud_thread and self.cloud_thread.isRunning():
            self.cloud_thread.stop()
            self.cloud_thread.wait()
