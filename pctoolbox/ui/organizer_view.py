import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QFrame, QLineEdit, QFileDialog)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from pctoolbox import config
from pctoolbox.threads.smart_organizer import SmartOrganizerThread

class OrganizerView(QWidget):
    """
    Sleek Smart Organizer UI tab.
    Offers automatic category routing for standard folders.
    Advanced custom regex filters and deep PDF parsing are locked on Free version.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.organizer_thread = None
        self.default_watch_path = os.path.abspath(os.path.join(os.path.expanduser("~"), "Downloads"))
        self.init_ui()

    def init_ui(self):
        # Two-Column Master Layout (Left: Directory watch + Logs, Right: Rule builder)
        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(15, 15, 15, 15)
        master_layout.setSpacing(15)

        # Left Column: Standard/Free watch configurations
        left_pane = QFrame()
        left_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)

        free_title = QLabel("📁 Dynamic Folder Watcher")
        free_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        free_title.setStyleSheet("color: #89b4fa; border: none;")
        left_layout.addWidget(free_title)

        desc = QLabel("Automates file management by instantly routing new files into specialized subfolders (Images, Videos, Docs).")
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #a6adc8; border: none;")
        desc.setWordWrap(True)
        left_layout.addWidget(desc)

        # Watch directory selection row
        dir_layout = QHBoxLayout()
        self.txt_watch_dir = QLineEdit(self.default_watch_path)
        self.txt_watch_dir.setReadOnly(True)
        self.txt_watch_dir.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        dir_layout.addWidget(self.txt_watch_dir)

        btn_browse = QPushButton("Browse")
        btn_browse.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)
        btn_browse.clicked.connect(self.browse_watch_dir)
        dir_layout.addWidget(btn_browse)
        left_layout.addLayout(dir_layout)

        # Activation controls
        ctrl_layout = QHBoxLayout()
        self.btn_toggle_watcher = QPushButton("Start Watching Folder")
        self.btn_toggle_watcher.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_toggle_watcher.setStyleSheet("""
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
        self.btn_toggle_watcher.clicked.connect(self.toggle_watcher_state)
        ctrl_layout.addWidget(self.btn_toggle_watcher)

        self.lbl_watch_status = QLabel("Status: Idle")
        self.lbl_watch_status.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.lbl_watch_status.setStyleSheet("color: #f5e0dc; border: none;")
        ctrl_layout.addWidget(self.lbl_watch_status)
        ctrl_layout.addStretch()
        left_layout.addLayout(ctrl_layout)

        # File routing activity logs
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
        left_layout.addWidget(self.log_console)

        master_layout.addWidget(left_pane, 3)

        # Right Column: Premium custom rules & Deep Scan
        self.right_pane = QFrame()
        self.right_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        self.right_master_layout = QVBoxLayout(self.right_pane)
        self.right_master_layout.setContentsMargins(0, 0, 0, 0)

        # Pro Rules controls
        self.pro_control_widget = QWidget()
        pro_layout = QVBoxLayout(self.pro_control_widget)
        pro_layout.setContentsMargins(15, 15, 15, 15)
        pro_layout.setSpacing(12)

        pro_title = QLabel("⚡ Advanced Rule Builder")
        pro_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        pro_title.setStyleSheet("color: #fab387; border: none;")
        pro_layout.addWidget(pro_title)

        pro_desc = QLabel("Instruct the watch engine to sort using regular expressions and parse plain text documents looking for invoicing/billing matches.")
        pro_desc.setWordWrap(True)
        pro_desc.setFont(QFont("Segoe UI", 9))
        pro_desc.setStyleSheet("color: #a6adc8; border: none;")
        pro_layout.addWidget(pro_desc)

        # Active rules display list
        rules_lbl = QLabel("Active Pro Rules:")
        rules_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        rules_lbl.setStyleSheet("color: #fab387; border: none;")
        pro_layout.addWidget(rules_lbl)

        self.rules_console = QTextEdit()
        self.rules_console.setReadOnly(True)
        self.rules_console.setFont(QFont("Consolas", 8))
        self.rules_console.setStyleSheet("""
            QTextEdit {
                background-color: #11111b;
                border: 1px solid #313244;
                color: #fab387;
                border-radius: 6px;
            }
        """)
        self.rules_console.append("- Filename Regex Match: 'screenshot.*' -> /Screenshots")
        self.rules_console.append("- Filename Regex Match: 'backup.*' -> /Backups")
        self.rules_console.append("- Filename Regex Match: 'temp.*' -> /Temp_Files")
        self.rules_console.append("- Deep content scan: 'invoice/billing' keywords -> /Invoices")
        pro_layout.addWidget(self.rules_console)

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

        lock_desc = QLabel("Get Steam Pro version to unlock custom regex filename mapping and deep file content keyword scanning.")
        lock_desc.setWordWrap(True)
        lock_desc.setFont(QFont("Segoe UI", 8))
        lock_desc.setStyleSheet("color: #a6adc8; border: none;")
        lock_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_desc)

        self.right_master_layout.addWidget(self.lock_overlay)

        master_layout.addWidget(self.right_pane, 2)

        # Synchronize UI with license state
        self.refresh_ui()

    def browse_watch_dir(self):
        selected_dir = QFileDialog.getExistingDirectory(self, "Select Folder to Watch", self.txt_watch_dir.text())
        if selected_dir:
            self.txt_watch_dir.setText(os.path.abspath(selected_dir))

    def toggle_watcher_state(self):
        if self.organizer_thread and self.organizer_thread.isRunning():
            self.btn_toggle_watcher.setText("Stopping...")
            self.organizer_thread.stop()
        else:
            target_dir = self.txt_watch_dir.text()
            self.btn_toggle_watcher.setText("Stop Watching")

            self.organizer_thread = SmartOrganizerThread(watch_dir=target_dir)
            self.organizer_thread.log_msg.connect(self.log_text)
            self.organizer_thread.status_changed.connect(self.on_status_changed)
            self.organizer_thread.start()

    def log_text(self, text: str):
        self.log_console.append(f"[*] {text}")

    def on_status_changed(self, status: str):
        self.lbl_watch_status.setText(status)
        if "Stopped" in status:
            self.btn_toggle_watcher.setText("Start Watching Folder")
            self.organizer_thread = None

    def refresh_ui(self):
        if config.IS_PRO_VERSION:
            self.lock_overlay.hide()
            self.pro_control_widget.show()
        else:
            self.pro_control_widget.hide()
            self.lock_overlay.show()

    def stop_all_workers(self):
        if self.organizer_thread and self.organizer_thread.isRunning():
            self.organizer_thread.stop()
            self.organizer_thread.wait()
