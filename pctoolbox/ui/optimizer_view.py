from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QPushButton, QProgressBar, QTextEdit, QFrame)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from pctoolbox import config
from pctoolbox.threads.optimizer import OptimizerThread

class OptimizerView(QWidget):
    """
    Advanced Game & RAM Optimizer.
    This view displays an elegant Lock Screen / Overlay if config.IS_PRO_VERSION is False.
    All operations are handled safely on an isolated background thread.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.opt_thread = None
        self.init_ui()

    def init_ui(self):
        # We will wrap everything inside a master layout
        self.master_layout = QVBoxLayout(self)
        self.master_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Main View (The actual control panel)
        self.main_widget = QWidget()
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("⚡ Advanced Game & RAM Optimizer")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #cba6f7;")
        layout.addWidget(title)

        desc = QLabel("Reclaim Standby memory, configure GPU priority, and schedule Ultra Gaming thread States.")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #a6adc8;")
        layout.addWidget(desc)

        # Advanced Settings Options
        self.chk_ram = QCheckBox("Flush OS standby memory, file caches & junk buffers")
        self.chk_ram.setChecked(True)
        self.chk_ram.setFont(QFont("Segoe UI", 10))
        self.chk_ram.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(self.chk_ram)

        self.chk_gpu = QCheckBox("Enable GPU Hardware-Accelerated Scheduling Overrides")
        self.chk_gpu.setChecked(True)
        self.chk_gpu.setFont(QFont("Segoe UI", 10))
        self.chk_gpu.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(self.chk_gpu)

        self.chk_sched = QCheckBox("Set CPU & Thread Priorities to Extreme Performance Mode")
        self.chk_sched.setChecked(False)
        self.chk_sched.setFont(QFont("Segoe UI", 10))
        self.chk_sched.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(self.chk_sched)

        # Control Row
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Optimize System Now")
        self.btn_start.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #fab387;
                color: #11111b;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
            }
        """)
        self.btn_start.clicked.connect(self.start_optimization)
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
        self.btn_cancel.clicked.connect(self.cancel_optimization)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Progress and Status
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
                background-color: #fab387;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Status: Idle")
        self.status_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.status_label.setStyleSheet("color: #f5e0dc;")
        layout.addWidget(self.status_label)

        # Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 9))
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #11111b;
                border: 1px solid #313244;
                color: #fab387;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.console)

        self.master_layout.addWidget(self.main_widget)

        # 2. Lock Overlay (Displayed on top if standard license)
        self.lock_overlay = QFrame()
        self.lock_overlay.setStyleSheet("background-color: rgba(24, 24, 37, 230);")

        overlay_layout = QVBoxLayout(self.lock_overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.setSpacing(10)

        # Large lock graphic / icon
        self.lock_icon_lbl = QLabel()
        self.lock_icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lock_pix = QPixmap(config.get_asset_path("lock.png"))
        if not lock_pix.isNull():
            self.lock_icon_lbl.setPixmap(lock_pix.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.lock_icon_lbl.setText("🔒")
            self.lock_icon_lbl.setFont(QFont("Segoe UI", 32))
        overlay_layout.addWidget(self.lock_icon_lbl)

        lock_title = QLabel("Advanced Game Optimizer is Locked")
        lock_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lock_title.setStyleSheet("color: #f38ba8;")
        lock_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_title)

        lock_desc = QLabel("Upgrade to Steam Pro Version to configure kernel scheduler priorities and optimize RAM limits.")
        lock_desc.setFont(QFont("Segoe UI", 10))
        lock_desc.setStyleSheet("color: #a6adc8;")
        lock_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_desc)

        self.master_layout.addWidget(self.lock_overlay)

        # Ensure correct view state on startup
        self.refresh_ui()

    def start_optimization(self):
        # Safe Thread Execution
        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(0)
        self.console.clear()
        self.console.append("[Game Optimizer] Dispatching isolated RAM optimization thread...")

        self.opt_thread = OptimizerThread(
            optimize_ram=self.chk_ram.isChecked(),
            prioritize_gpu=self.chk_gpu.isChecked(),
            clean_ram=self.chk_sched.isChecked()
        )
        self.opt_thread.progress.connect(self.progress_bar.setValue)
        self.opt_thread.status.connect(self.on_status)
        self.opt_thread.finished_summary.connect(self.on_finished)
        self.opt_thread.unauthorized.connect(self.on_unauthorized)
        self.opt_thread.finished.connect(self.on_thread_terminated)
        self.opt_thread.start()

    def cancel_optimization(self):
        if self.opt_thread and self.opt_thread.isRunning():
            self.console.append("[Game Optimizer] Abort signal sent by user.")
            self.opt_thread.stop()

    def on_status(self, text: str):
        self.status_label.setText(f"Status: {text}")
        self.console.append(f"[Game Optimizer] {text}")

    def on_finished(self, summary: str):
        self.console.append(f"\n[Game Optimizer] Complete: {summary}")
        self.status_label.setText("Status: Optimization Complete!")

    def on_unauthorized(self):
        self.console.append("[Game Optimizer] Error: Thread authorization validation failed.")
        self.status_label.setText("Status: Authorization Failed.")

    def on_thread_terminated(self):
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.opt_thread = None

    def refresh_ui(self):
        """Called to dynamically toggle interface and options when license updates."""
        if config.IS_PRO_VERSION:
            self.lock_overlay.hide()
            self.main_widget.show()
        else:
            self.main_widget.hide()
            self.lock_overlay.show()
