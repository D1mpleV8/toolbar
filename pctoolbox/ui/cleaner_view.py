from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QPushButton, QProgressBar, QTextEdit)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from pctoolbox.threads.cleaner import CleanerThread

class CleanerView(QWidget):
    """
    Standard / Free Utility tab allowing complete system cleaning tasks.
    Operates on a non-blocking background thread CleanerThread.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clean_thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title / Description
        title = QLabel("🧹 System Speedup Cleaner")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #cba6f7;")
        layout.addWidget(title)

        desc = QLabel("Safely clean junk files, purge caches, and rotate logs to boost system speed.")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #a6adc8;")
        layout.addWidget(desc)

        # Config Options
        self.chk_temp = QCheckBox("Clean Temporary Files & Prefetch")
        self.chk_temp.setChecked(True)
        self.chk_temp.setFont(QFont("Segoe UI", 10))
        self.chk_temp.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(self.chk_temp)

        self.chk_cache = QCheckBox("Clear Application & Browser Cache")
        self.chk_cache.setChecked(True)
        self.chk_cache.setFont(QFont("Segoe UI", 10))
        self.chk_cache.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(self.chk_cache)

        self.chk_logs = QCheckBox("Archive & Optimize System Log Files")
        self.chk_logs.setChecked(False)
        self.chk_logs.setFont(QFont("Segoe UI", 10))
        self.chk_logs.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(self.chk_logs)

        # Control Row
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Run Cleaner")
        self.btn_start.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #11111b;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
            }
        """)
        self.btn_start.clicked.connect(self.start_cleanup)
        btn_layout.addWidget(self.btn_start)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #f38ba8;
                color: #11111b;
            }
        """)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_cleanup)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Status and Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #45475a;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                background-color: #181825;
            }
            QProgressBar::chunk {
                background-color: #89b4fa;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Status: Idle")
        self.status_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.status_label.setStyleSheet("color: #f5e0dc;")
        layout.addWidget(self.status_label)

        # Console / Terminal Output
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 9))
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #11111b;
                border: 1px solid #313244;
                color: #a6e3a1;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.console)

    def start_cleanup(self):
        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(0)
        self.console.clear()
        self.console.append("[System Cleaner] Initializing process thread...")

        self.clean_thread = CleanerThread(
            clean_temp=self.chk_temp.isChecked(),
            clean_cache=self.chk_cache.isChecked(),
            clean_logs=self.chk_logs.isChecked()
        )
        self.clean_thread.progress.connect(self.progress_bar.setValue)
        self.clean_thread.status.connect(self.on_status_received)
        self.clean_thread.finished_summary.connect(self.on_finished)
        self.clean_thread.finished.connect(self.on_thread_terminated)
        self.clean_thread.start()

    def cancel_cleanup(self):
        if self.clean_thread and self.clean_thread.isRunning():
            self.console.append("[System Cleaner] Abort signal dispatched by user.")
            self.clean_thread.stop()

    def on_status_received(self, text: str):
        self.status_label.setText(f"Status: {text}")
        self.console.append(f"[System Cleaner] {text}")

    def on_finished(self, summary: str):
        self.console.append(f"\n[System Cleaner] Complete: {summary}")
        self.status_label.setText("Status: Finished!")

    def on_thread_terminated(self):
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.clean_thread = None
