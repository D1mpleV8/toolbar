import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QFrame, QCheckBox)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from pctoolbox import config
from pctoolbox.threads.privacy_registry import PrivacyRegistryThread
from pctoolbox.threads.tracker_blocker import TrackerBlockerThread

class PrivacyShieldView(QWidget):
    """
    Sleek Privacy Shield tab view.
    Fulfills standard OS telemetry/ad tweaks,
    and gates hosts-file global trackers blocker on standard free version.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.reg_threads = []
        self.blocker_thread = None
        self.init_ui()

    def init_ui(self):
        # Two-Column Master Layout (Left: standard telemetry blocks, Right: Pro Hosts Blocker)
        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(15, 15, 15, 15)
        master_layout.setSpacing(15)

        # Left Column: Standard Free Toggles
        left_pane = QFrame()
        left_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)

        free_title = QLabel("🛡️ OS Privacy Telemetry Tweaks")
        free_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        free_title.setStyleSheet("color: #89b4fa; border: none;")
        left_layout.addWidget(free_title)

        desc = QLabel("Safely modify local group policies and registry parameters to disable invasive telemetry, ads, and background reporting.")
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #a6adc8; border: none;")
        desc.setWordWrap(True)
        left_layout.addWidget(desc)

        # Checklist Toggles
        self.chk_telemetry = QCheckBox("Block Windows Diagnostic Telemetry reporting")
        self.chk_telemetry.setFont(QFont("Segoe UI", 9))
        self.chk_telemetry.setStyleSheet("color: #cdd6f4; border: none;")
        self.chk_telemetry.stateChanged.connect(lambda state: self.toggle_registry_setting("Windows Telemetry", state))
        left_layout.addWidget(self.chk_telemetry)

        self.chk_cortana = QCheckBox("Disable Cortana & web-assisted Search links")
        self.chk_cortana.setFont(QFont("Segoe UI", 9))
        self.chk_cortana.setStyleSheet("color: #cdd6f4; border: none;")
        self.chk_cortana.stateChanged.connect(lambda state: self.toggle_registry_setting("Cortana Search Link", state))
        left_layout.addWidget(self.chk_cortana)

        self.chk_ads = QCheckBox("Remove Lock Screen Advertisements & Spotlight Tips")
        self.chk_ads.setFont(QFont("Segoe UI", 9))
        self.chk_ads.setStyleSheet("color: #cdd6f4; border: none;")
        self.chk_ads.stateChanged.connect(lambda state: self.toggle_registry_setting("Lockscreen Advertisements", state))
        left_layout.addWidget(self.chk_ads)

        left_layout.addStretch()

        # Log console
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
        self.log_console.setMaximumHeight(120)
        left_layout.addWidget(self.log_console)

        master_layout.addWidget(left_pane, 3)

        # Right Column: Premium Hosts Tracker Blocker
        self.right_pane = QFrame()
        self.right_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        self.right_master_layout = QVBoxLayout(self.right_pane)
        self.right_master_layout.setContentsMargins(0, 0, 0, 0)

        # Pro controls widget
        self.pro_control_widget = QWidget()
        pro_layout = QVBoxLayout(self.pro_control_widget)
        pro_layout.setContentsMargins(15, 15, 15, 15)
        pro_layout.setSpacing(12)

        pro_title = QLabel("🛑 Hardware-Level Tracker Blocker")
        pro_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        pro_title.setStyleSheet("color: #fab387; border: none;")
        pro_layout.addWidget(pro_title)

        pro_desc = QLabel("Modifies the local hosts configuration file to block known metrics, advertisements, and tracker domain IPs globally across the entire operating system.")
        pro_desc.setWordWrap(True)
        pro_desc.setFont(QFont("Segoe UI", 9))
        pro_desc.setStyleSheet("color: #a6adc8; border: none;")
        pro_layout.addWidget(pro_desc)

        # Block Info Box
        self.block_status_card = QFrame()
        self.block_status_card.setStyleSheet("QFrame { background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 6px; }")
        stat_card_lay = QVBoxLayout(self.block_status_card)
        self.lbl_block_state = QLabel("Blocker State: Inactive")
        self.lbl_block_state.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.lbl_block_state.setStyleSheet("color: #f38ba8; border: none;")
        stat_card_lay.addWidget(self.lbl_block_state)
        pro_layout.addWidget(self.block_status_card)

        # Toggle button
        self.btn_toggle_blocker = QPushButton("Turn On Global Blocker")
        self.btn_toggle_blocker.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_toggle_blocker.setStyleSheet("""
            QPushButton {
                background-color: #fab387;
                color: #11111b;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
            }
        """)
        self.btn_toggle_blocker.clicked.connect(self.toggle_hosts_tracker_blocker)
        pro_layout.addWidget(self.btn_toggle_blocker)

        self.blocker_console = QTextEdit()
        self.blocker_console.setReadOnly(True)
        self.blocker_console.setFont(QFont("Consolas", 8))
        self.blocker_console.setStyleSheet("""
            QTextEdit {
                background-color: #11111b;
                border: 1px solid #313244;
                color: #fab387;
                border-radius: 6px;
            }
        """)
        pro_layout.addWidget(self.blocker_console)

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

        lock_desc = QLabel("Get Steam Pro version to unlock Hardware-Level IP Tracker Blocking and stop tracking domains globally across your OS.")
        lock_desc.setWordWrap(True)
        lock_desc.setFont(QFont("Segoe UI", 8))
        lock_desc.setStyleSheet("color: #a6adc8; border: none;")
        lock_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_desc)

        self.right_master_layout.addWidget(self.lock_overlay)

        master_layout.addWidget(self.right_pane, 2)

        # Sync visual locking state
        self.refresh_ui()

    def toggle_registry_setting(self, key_name: str, state: int):
        enable = (state == 2 or state == Qt.CheckState.Checked.value)
        self.log_console.append(f"[Registry] Toggling setting '{key_name}' -> enable: {enable}")

        thread = PrivacyRegistryThread(key_name, enable)
        thread.status_msg.connect(lambda txt: self.log_console.append(f"[Registry] {txt}"))
        thread.start()
        self.reg_threads.append(thread)

    def toggle_hosts_tracker_blocker(self):
        if self.blocker_thread and self.blocker_thread.isRunning():
            self.btn_toggle_blocker.setText("Processing change...")
            self.blocker_thread.stop()
        else:
            # Decide to enable or disable
            current_state_str = self.lbl_block_state.text()
            enable = "Active" not in current_state_str

            self.btn_toggle_blocker.setText("Processing...")
            self.blocker_console.append(f"[Blocker] Launching hosts file modification thread (enable={enable})...")

            self.blocker_thread = TrackerBlockerThread(enable)
            self.blocker_thread.status_msg.connect(lambda txt: self.blocker_console.append(f"[Blocker] {txt}"))
            self.blocker_thread.unauthorized.connect(self.on_block_unauthorized)
            self.blocker_thread.block_completed.connect(self.on_block_completed)
            self.blocker_thread.start()

    def on_block_unauthorized(self):
        self.blocker_console.append("⚠️ Pro Licensing Validation Failed! Process halted.")

    def on_block_completed(self, success: bool, msg: str):
        self.blocker_thread = None

        if success:
            if "activated" in msg or "toggled" in msg:
                self.lbl_block_state.setText("Blocker State: Active")
                self.lbl_block_state.setStyleSheet("color: #a6e3a1; border: none;")
                self.btn_toggle_blocker.setText("Turn Off Global Blocker")
            else:
                self.lbl_block_state.setText("Blocker State: Inactive")
                self.lbl_block_state.setStyleSheet("color: #f38ba8; border: none;")
                self.btn_toggle_blocker.setText("Turn On Global Blocker")
        else:
            self.lbl_block_state.setText("Blocker State: Failed")
            self.lbl_block_state.setStyleSheet("color: #f38ba8; border: none;")
            self.btn_toggle_blocker.setText("Turn On Global Blocker")

    def refresh_ui(self):
        if config.IS_PRO_VERSION:
            self.lock_overlay.hide()
            self.pro_control_widget.show()
        else:
            if self.blocker_thread and self.blocker_thread.isRunning():
                self.blocker_thread.stop()
            self.pro_control_widget.hide()
            self.lock_overlay.show()

    def stop_all_workers(self):
        # Stop all registry background threads
        for t in self.reg_threads:
            if t.isRunning():
                t.wait()

        # Stop blocker thread
        if self.blocker_thread and self.blocker_thread.isRunning():
            self.blocker_thread.stop()
            self.blocker_thread.wait()
