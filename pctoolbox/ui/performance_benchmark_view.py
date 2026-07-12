import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QFrame, QProgressBar, QComboBox)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from pctoolbox import config
from pctoolbox.threads.benchmark_stress import BenchmarkStressThread
from pctoolbox.threads.smart_auto_game_optimizer import SmartAutoGameOptimizerThread

class PerformanceBenchmarkView(QWidget):
    """
    Sleek Performance & Benchmark tab view.
    Fulfills standard CPU multi-core stress testing (with a live loading meter),
    and gates background Smart Auto-Game Optimization on standard free version.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stress_thread = None
        self.auto_opt_thread = None
        self.init_ui()

    def init_ui(self):
        # Two-Column Master Layout (Left: CPU stress, Right: Pro Game Auto Optimizer)
        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(15, 15, 15, 15)
        master_layout.setSpacing(15)

        # Left Column: Free CPU Stress Test
        left_pane = QFrame()
        left_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)

        free_title = QLabel("🚀 Multi-Core CPU Stress Test")
        free_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        free_title.setStyleSheet("color: #89b4fa; border: none;")
        left_layout.addWidget(free_title)

        desc = QLabel("Validate hardware stability and thermal ceiling boundaries by spinning mathematical matrices across all core threads.")
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #a6adc8; border: none;")
        desc.setWordWrap(True)
        left_layout.addWidget(desc)

        # Config Stress Duration Row
        config_row = QHBoxLayout()
        lbl_dur = QLabel("Stress Duration:")
        lbl_dur.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        lbl_dur.setStyleSheet("color: #cdd6f4; border: none; background: transparent;")
        config_row.addWidget(lbl_dur)

        self.cmb_duration = QComboBox()
        self.cmb_duration.addItems(["5 Seconds (Quick)", "15 Seconds (Normal)", "30 Seconds (Deep)"])
        self.cmb_duration.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        config_row.addWidget(self.cmb_duration)
        left_layout.addLayout(config_row)

        # Speedometer/Telemetry Card
        self.telemetry_card = QFrame()
        self.telemetry_card.setStyleSheet("QFrame { background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 6px; }")
        telemetry_lay = QHBoxLayout(self.telemetry_card)

        # Load meter
        load_layout = QVBoxLayout()
        lbl_load_tit = QLabel("CPU Workload")
        lbl_load_tit.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_load_tit.setStyleSheet("color: #89b4fa; border: none; background: transparent;")
        lbl_load_tit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_live_load = QLabel("Idle (3%)")
        self.lbl_live_load.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.lbl_live_load.setStyleSheet("color: #a6e3a1; border: none; background: transparent;")
        self.lbl_live_load.setAlignment(Qt.AlignmentFlag.AlignCenter)
        load_layout.addWidget(lbl_load_tit)
        load_layout.addWidget(self.lbl_live_load)
        telemetry_lay.addLayout(load_layout)

        # Separator line
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background-color: #313244;")
        telemetry_lay.addWidget(sep)

        # Thermal meter
        temp_layout = QVBoxLayout()
        lbl_temp_tit = QLabel("CPU Core Temp")
        lbl_temp_tit.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_temp_tit.setStyleSheet("color: #89b4fa; border: none; background: transparent;")
        lbl_temp_tit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_live_temp = QLabel("42°C")
        self.lbl_live_temp.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.lbl_live_temp.setStyleSheet("color: #fab387; border: none; background: transparent;")
        self.lbl_live_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temp_layout.addWidget(lbl_temp_tit)
        temp_layout.addWidget(self.lbl_live_temp)
        telemetry_lay.addLayout(temp_layout)

        left_layout.addWidget(self.telemetry_card)

        # Start/Cancel buttons
        btn_row = QHBoxLayout()
        self.btn_start_stress = QPushButton("Start Stress Test")
        self.btn_start_stress.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_start_stress.setStyleSheet("""
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
        self.btn_start_stress.clicked.connect(self.start_stress_test)
        btn_row.addWidget(self.btn_start_stress)

        self.btn_cancel_stress = QPushButton("Abort")
        self.btn_cancel_stress.setEnabled(False)
        self.btn_cancel_stress.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_cancel_stress.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #f38ba8;
                color: #11111b;
            }
        """)
        self.btn_cancel_stress.clicked.connect(self.cancel_stress_test)
        btn_row.addWidget(self.btn_cancel_stress)
        btn_row.addStretch()
        left_layout.addLayout(btn_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #45475a;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                background-color: #11111b;
            }
            QProgressBar::chunk {
                background-color: #89b4fa;
                border-radius: 5px;
            }
        """)
        left_layout.addWidget(self.progress_bar)

        # Activity Logs
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
        self.log_console.setMaximumHeight(100)
        left_layout.addWidget(self.log_console)

        master_layout.addWidget(left_pane, 3)

        # Right Column: Premium Smart Auto Game Optimizer
        self.right_pane = QFrame()
        self.right_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        self.right_master_layout = QVBoxLayout(self.right_pane)
        self.right_master_layout.setContentsMargins(0, 0, 0, 0)

        # Pro controls widget
        self.pro_control_widget = QWidget()
        pro_layout = QVBoxLayout(self.pro_control_widget)
        pro_layout.setContentsMargins(15, 15, 15, 15)
        pro_layout.setSpacing(12)

        pro_title = QLabel("⚡ Smart Auto-Game Optimizer")
        pro_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        pro_title.setStyleSheet("color: #fab387; border: none;")
        pro_layout.addWidget(pro_title)

        pro_desc = QLabel("Actively monitors the background process pipeline. When a full-screen game starts, it auto-elevates CPU priority and suspends memory-hogging tasks (e.g. Chrome), restoring everything seamlessly upon game exit.")
        pro_desc.setWordWrap(True)
        pro_desc.setFont(QFont("Segoe UI", 9))
        pro_desc.setStyleSheet("color: #a6adc8; border: none;")
        pro_layout.addWidget(pro_desc)

        # Live state card
        self.opt_status_card = QFrame()
        self.opt_status_card.setStyleSheet("QFrame { background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 6px; }")
        stat_card_lay = QVBoxLayout(self.opt_status_card)
        self.lbl_opt_state = QLabel("Optimizer State: Idle")
        self.lbl_opt_state.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.lbl_opt_state.setStyleSheet("color: #f38ba8; border: none;")
        stat_card_lay.addWidget(self.lbl_opt_state)
        pro_layout.addWidget(self.opt_status_card)

        # Toggle Button
        self.btn_toggle_opt = QPushButton("Enable Auto-Optimizer")
        self.btn_toggle_opt.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_toggle_opt.setStyleSheet("""
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
        self.btn_toggle_opt.clicked.connect(self.toggle_auto_optimizer)
        pro_layout.addWidget(self.btn_toggle_opt)

        # Output console
        self.opt_console = QTextEdit()
        self.opt_console.setReadOnly(True)
        self.opt_console.setFont(QFont("Consolas", 8))
        self.opt_console.setStyleSheet("""
            QTextEdit {
                background-color: #11111b;
                border: 1px solid #313244;
                color: #fab387;
                border-radius: 6px;
            }
        """)
        pro_layout.addWidget(self.opt_console)

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

        lock_desc = QLabel("Get Steam Pro version to unlock the Smart Auto-Game Optimizer and let the kernel prioritize your high-refresh game sessions.")
        lock_desc.setWordWrap(True)
        lock_desc.setFont(QFont("Segoe UI", 8))
        lock_desc.setStyleSheet("color: #a6adc8; border: none;")
        lock_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_desc)

        self.right_master_layout.addWidget(self.lock_overlay)

        master_layout.addWidget(self.right_pane, 2)

        # Sync visual locking state
        self.refresh_ui()

    def start_stress_test(self):
        duration_sel = self.cmb_duration.currentText()
        if "5" in duration_sel:
            seconds = 5
        elif "15" in duration_sel:
            seconds = 15
        else:
            seconds = 30

        self.btn_start_stress.setEnabled(False)
        self.btn_cancel_stress.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log_console.clear()
        self.log_console.append(f"[Stress] Launching multi-core stress thread sequence ({seconds}s)...")

        self.stress_thread = BenchmarkStressThread(seconds)
        self.stress_thread.progress_changed.connect(self.progress_bar.setValue)
        self.stress_thread.telemetry_updated.connect(self.on_stress_telemetry)
        self.stress_thread.status_msg.connect(lambda txt: self.log_console.append(f"[Stress] {txt}"))
        self.stress_thread.finished_summary.connect(self.on_stress_completed)
        self.stress_thread.finished.connect(self.on_stress_terminated)
        self.stress_thread.start()

    def cancel_stress_test(self):
        if self.stress_thread and self.stress_thread.isRunning():
            self.log_console.append("[Stress] Dispatching cancellation interrupt...")
            self.stress_thread.stop()

    def on_stress_telemetry(self, t: dict):
        load = t.get("load", 0)
        temp = t.get("temp", 0)
        self.lbl_live_load.setText(f"Active ({load}%)")
        self.lbl_live_temp.setText(f"{temp}°C")

        # Color temperature changes to watch thermals spike
        if temp < 55:
            self.lbl_live_temp.setStyleSheet("color: #a6e3a1; border: none; background: transparent;")
        elif temp < 75:
            self.lbl_live_temp.setStyleSheet("color: #f9e2af; border: none; background: transparent;")
        else:
            self.lbl_live_temp.setStyleSheet("color: #f38ba8; border: none; background: transparent;")

    def on_stress_completed(self, summary: str):
        self.log_console.append(f"\n[Stress] Complete: {summary}")

    def on_stress_terminated(self):
        self.btn_start_stress.setEnabled(True)
        self.btn_cancel_stress.setEnabled(False)
        self.lbl_live_load.setText("Idle (3%)")
        self.lbl_live_temp.setStyleSheet("color: #fab387; border: none; background: transparent;")
        self.lbl_live_temp.setText("42°C")
        self.stress_thread = None

    def toggle_auto_optimizer(self):
        if self.auto_opt_thread and self.auto_opt_thread.isRunning():
            self.btn_toggle_opt.setText("Stopping Auto-Optimizer...")
            self.auto_opt_thread.stop()
        else:
            self.btn_toggle_opt.setText("Disable Auto-Optimizer")
            self.lbl_opt_state.setText("Optimizer State: Listening")
            self.lbl_opt_state.setStyleSheet("color: #a6e3a1; border: none;")
            self.opt_console.append("[Optimizer] Initializing process filter pipeline...")

            self.auto_opt_thread = SmartAutoGameOptimizerThread()
            self.auto_opt_thread.status_msg.connect(lambda txt: self.opt_console.append(f"[Optimizer] {txt}"))
            self.auto_opt_thread.unauthorized.connect(self.on_opt_unauthorized)
            self.auto_opt_thread.finished_summary.connect(self.on_opt_finished)
            self.auto_opt_thread.start()

    def on_opt_unauthorized(self):
        self.opt_console.append("⚠️ Pro Licensing Validation Failed! Task halted.")

    def on_opt_finished(self, summary: str):
        self.opt_console.append(f"\n⚡ Auto-Optimizer Disabled: {summary}")
        self.lbl_opt_state.setText("Optimizer State: Idle")
        self.lbl_opt_state.setStyleSheet("color: #f38ba8; border: none;")
        self.btn_toggle_opt.setText("Enable Auto-Optimizer")
        self.auto_opt_thread = None

    def refresh_ui(self):
        if config.IS_PRO_VERSION:
            self.lock_overlay.hide()
            self.pro_control_widget.show()
        else:
            if self.auto_opt_thread and self.auto_opt_thread.isRunning():
                self.auto_opt_thread.stop()
            self.pro_control_widget.hide()
            self.lock_overlay.show()

    def stop_all_workers(self):
        if self.stress_thread and self.stress_thread.isRunning():
            self.stress_thread.stop()
            self.stress_thread.wait()
        if self.auto_opt_thread and self.auto_opt_thread.isRunning():
            self.auto_opt_thread.stop()
            self.auto_opt_thread.wait()
