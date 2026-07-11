from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QProgressBar, QTextEdit, QFrame, QComboBox)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from pctoolbox import config
from pctoolbox.threads.macro import MacroThread

class MacroView(QWidget):
    """
    Advanced Computer Vision Macro automation view.
    Monitors target patterns and simulates automated hotkeys/actions (like F9).
    This advanced feature is locked behind the config.IS_PRO_VERSION feature flag.
    All automation runs off the Main UI thread on MacroThread.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.macro_thread = None
        self.init_ui()

    def init_ui(self):
        self.master_layout = QVBoxLayout(self)
        self.master_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Main UI
        self.main_widget = QWidget()
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("🤖 Computer Vision Automation Macros")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #cba6f7;")
        layout.addWidget(title)

        desc = QLabel("Automate game keys and mouse inputs natively when real-time visual patterns are recognized on-screen.")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #a6adc8;")
        layout.addWidget(desc)

        # Template Selection
        sel_layout = QHBoxLayout()
        sel_lbl = QLabel("CV Detection Template:")
        sel_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        sel_lbl.setStyleSheet("color: #cdd6f4;")
        sel_layout.addWidget(sel_lbl)

        self.cmb_template = QComboBox()
        self.cmb_template.addItems(["HP Bar Trigger (F9 Match)", "Enemy Boss Active", "Low Mana Quick Flask", "Inventory Drop Pattern"])
        self.cmb_template.setFont(QFont("Segoe UI", 9))
        self.cmb_template.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        sel_layout.addWidget(self.cmb_template)
        sel_layout.addStretch()
        layout.addLayout(sel_layout)

        # Actions & Hotkeys Desc
        info_card = QFrame()
        info_card.setStyleSheet("background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 6px;")
        info_layout = QVBoxLayout(info_card)
        info_text = QLabel("💡 Hotkey Configuration:\n- Press F9 to toggle running the Computer Vision Macro engine at any time.\n- Will run silently when application is minimized to the System Tray.")
        info_text.setFont(QFont("Segoe UI", 9))
        info_text.setStyleSheet("color: #cba6f7; border: none;")
        info_layout.addWidget(info_text)
        layout.addWidget(info_card)

        # Start / Cancel Buttons
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start CV Automation (F9)")
        self.btn_start.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #a6e3a1;
            }
        """)
        self.btn_start.clicked.connect(self.start_macro)
        btn_layout.addWidget(self.btn_start)

        self.btn_cancel = QPushButton("Stop")
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
        self.btn_cancel.clicked.connect(self.cancel_macro)
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
                background-color: #89b4fa;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Status: Idle")
        self.status_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.status_label.setStyleSheet("color: #f5e0dc;")
        layout.addWidget(self.status_label)

        # Output console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 9))
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #11111b;
                border: 1px solid #313244;
                color: #89b4fa;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.console)

        self.master_layout.addWidget(self.main_widget)

        # 2. Lock Screen Overlay
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

        lock_title = QLabel("Computer Vision Macros are Locked")
        lock_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lock_title.setStyleSheet("color: #f38ba8;")
        lock_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_title)

        lock_desc = QLabel("Upgrade to Steam Pro Version to run automated pixel triggers, frame listeners, and macro schedules.")
        lock_desc.setFont(QFont("Segoe UI", 10))
        lock_desc.setStyleSheet("color: #a6adc8;")
        lock_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_desc)

        self.master_layout.addWidget(self.lock_overlay)

        # Update initial lock/unlock visibility
        self.refresh_ui()

    def start_macro(self):
        # Prevent starting if already active
        if self.macro_thread and self.macro_thread.isRunning():
            return

        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(0)
        self.console.clear()
        self.console.append("[CV Macro Engine] Initiating real-time detection worker thread...")

        self.macro_thread = MacroThread(template_name=self.cmb_template.currentText())
        self.macro_thread.progress.connect(self.progress_bar.setValue)
        self.macro_thread.status.connect(self.on_status)
        self.macro_thread.match_found.connect(self.on_match)
        self.macro_thread.finished_summary.connect(self.on_finished)
        self.macro_thread.unauthorized.connect(self.on_unauthorized)
        self.macro_thread.finished.connect(self.on_thread_terminated)
        self.macro_thread.start()

    def cancel_macro(self):
        if self.macro_thread and self.macro_thread.isRunning():
            self.console.append("[CV Macro Engine] Stopping detection loops...")
            self.macro_thread.stop()

    def toggle_macro_state_f9(self):
        """Called externally (e.g., from MainWindow when global F9 hotkey is pressed)"""
        if not config.IS_PRO_VERSION:
            return

        if self.macro_thread and self.macro_thread.isRunning():
            self.console.append("[CV Macro Engine] F9 pressed: stopping current macro loop.")
            self.cancel_macro()
        else:
            self.console.append("[CV Macro Engine] F9 pressed: launching macro sequence.")
            self.start_macro()

    def on_status(self, text: str):
        self.status_label.setText(f"Status: {text}")
        self.console.append(f"[CV Macro Engine] {text}")

    def on_match(self, match_info: str):
        self.console.append(f"\n✨ [CV Match] {match_info}")

    def on_finished(self, summary: str):
        self.console.append(f"\n[CV Macro Engine] Complete: {summary}")
        self.status_label.setText("Status: Finished!")

    def on_unauthorized(self):
        self.console.append("[CV Macro Engine] Error: Execution unauthorized (Pro required).")
        self.status_label.setText("Status: Authorization Failed.")

    def on_thread_terminated(self):
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.macro_thread = None

    def refresh_ui(self):
        """Called to dynamically toggle interface lock cover and options when license updates."""
        if config.IS_PRO_VERSION:
            self.lock_overlay.hide()
            self.main_widget.show()
        else:
            self.main_widget.hide()
            self.lock_overlay.show()
