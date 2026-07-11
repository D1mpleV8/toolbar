from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QFrame, QComboBox)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from pctoolbox import config
from pctoolbox.ui.ping_chart import PingChartWidget
from pctoolbox.threads.ping_monitor import PingMonitorThread
from pctoolbox.threads.dns_switcher import DNSSwitcherThread
from pctoolbox.threads.network_prioritizer import NetworkPrioritizerThread

class NetworkView(QWidget):
    """
    Network & Connectivity module view.
    Fulfills standard network controls (Ping charts, DNS switcher) and locks
    the Advanced Gaming Network Prioritization behind IS_PRO_VERSION.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ping_thread = None
        self.dns_thread = None
        self.prio_thread = None
        self.init_ui()

    def init_ui(self):
        # Master layout split into two panes (Left: Ping & DNS, Right: Pro Prioritization)
        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(15, 15, 15, 15)
        master_layout.setSpacing(15)

        # Left Column: Free Utility Pane
        left_pane = QFrame()
        left_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)

        free_title = QLabel("🌐 Real-time Ping & DNS Manager")
        free_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        free_title.setStyleSheet("color: #89b4fa; border: none;")
        left_layout.addWidget(free_title)

        # Real-time Scrolling Ping Chart
        self.chart = PingChartWidget()
        left_layout.addWidget(self.chart)

        # 1-Click DNS Switcher
        dns_frame = QFrame()
        dns_frame.setStyleSheet("QFrame { background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 6px; }")
        dns_layout = QVBoxLayout(dns_frame)
        dns_layout.setContentsMargins(10, 10, 10, 10)
        dns_layout.setSpacing(8)

        dns_title = QLabel("⚡ 1-Click Fast DNS Switcher")
        dns_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        dns_title.setStyleSheet("color: #cba6f7; border: none;")
        dns_layout.addWidget(dns_title)

        combo_layout = QHBoxLayout()
        dns_label = QLabel("DNS Server:")
        dns_label.setFont(QFont("Segoe UI", 9))
        dns_label.setStyleSheet("color: #cdd6f4; border: none;")
        combo_layout.addWidget(dns_label)

        self.cmb_dns = QComboBox()
        self.cmb_dns.addItems(["Cloudflare", "Google", "DHCP (Automatic)"])
        self.cmb_dns.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        combo_layout.addWidget(self.cmb_dns)
        dns_layout.addLayout(combo_layout)

        self.btn_dns = QPushButton("Apply DNS Server")
        self.btn_dns.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_dns.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #11111b;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
            }
        """)
        self.btn_dns.clicked.connect(self.apply_dns_switch)
        dns_layout.addWidget(self.btn_dns)

        left_layout.addWidget(dns_frame)

        # Status logs
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

        # Right Column: Premium Gaming Optimizer (Pro feature)
        self.right_pane = QFrame()
        self.right_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        self.right_master_layout = QVBoxLayout(self.right_pane)
        self.right_master_layout.setContentsMargins(0, 0, 0, 0)

        # Inner premium control widget
        self.prio_control_widget = QWidget()
        prio_layout = QVBoxLayout(self.prio_control_widget)
        prio_layout.setContentsMargins(15, 15, 15, 15)
        prio_layout.setSpacing(12)

        prio_title = QLabel("🎮 Gaming Network Prioritization")
        prio_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        prio_title.setStyleSheet("color: #fab387; border: none;")
        prio_layout.addWidget(prio_title)

        prio_desc = QLabel("Actively detects when high-intensity games are active and suspends OS telemetry & updates to eliminate latency spikes.")
        prio_desc.setWordWrap(True)
        prio_desc.setFont(QFont("Segoe UI", 9))
        prio_desc.setStyleSheet("color: #a6adc8; border: none;")
        prio_layout.addWidget(prio_desc)

        # Visual status info
        self.prio_status_card = QFrame()
        self.prio_status_card.setStyleSheet("QFrame { background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 6px; }")
        stat_card_lay = QVBoxLayout(self.prio_status_card)

        self.lbl_prio_status = QLabel("State: Disabled")
        self.lbl_prio_status.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.lbl_prio_status.setStyleSheet("color: #f38ba8; border: none;")
        stat_card_lay.addWidget(self.lbl_prio_status)
        prio_layout.addWidget(self.prio_status_card)

        # Trigger buttons
        self.btn_toggle_prio = QPushButton("Enable Smart Prioritization")
        self.btn_toggle_prio.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_toggle_prio.setStyleSheet("""
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
        self.btn_toggle_prio.clicked.connect(self.toggle_smart_prio)
        prio_layout.addWidget(self.btn_toggle_prio)

        # Real-time process priority messages
        self.prio_console = QTextEdit()
        self.prio_console.setReadOnly(True)
        self.prio_console.setFont(QFont("Consolas", 8))
        self.prio_console.setStyleSheet("""
            QTextEdit {
                background-color: #11111b;
                border: 1px solid #313244;
                color: #fab387;
                border-radius: 6px;
            }
        """)
        prio_layout.addWidget(self.prio_console)

        self.right_master_layout.addWidget(self.prio_control_widget)

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

        lock_desc = QLabel("Get Steam Pro version to unlock Smart Gaming Network Prioritization and prevent background network spikes.")
        lock_desc.setWordWrap(True)
        lock_desc.setFont(QFont("Segoe UI", 8))
        lock_desc.setStyleSheet("color: #a6adc8; border: none;")
        lock_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_desc)

        self.right_master_layout.addWidget(self.lock_overlay)

        master_layout.addWidget(self.right_pane, 2)

        # Startup Ping Monitor
        self.start_ping_monitor()

        # Update initial Lock screen state
        self.refresh_ui()

    def start_ping_monitor(self):
        self.ping_thread = PingMonitorThread()
        self.ping_thread.ping_measured.connect(self.chart.add_ping_point)
        self.ping_thread.status_msg.connect(self.log_free_msg)
        self.ping_thread.start()

    def apply_dns_switch(self):
        self.btn_dns.setEnabled(False)
        self.dns_thread = DNSSwitcherThread(self.cmb_dns.currentText())
        self.dns_thread.status_msg.connect(self.log_free_msg)
        self.dns_thread.switch_completed.connect(self.on_dns_completed)
        self.dns_thread.start()

    def on_dns_completed(self, success: bool, msg: str):
        self.btn_dns.setEnabled(True)
        self.dns_thread = None

    def toggle_smart_prio(self):
        if self.prio_thread and self.prio_thread.isRunning():
            self.btn_toggle_prio.setText("Stopping network lock...")
            self.prio_thread.stop()
        else:
            self.btn_toggle_prio.setText("Disable Smart Prioritization")
            self.lbl_prio_status.setText("State: Actively Scanning")
            self.lbl_prio_status.setStyleSheet("color: #a6e3a1; border: none;")

            self.prio_thread = NetworkPrioritizerThread()
            self.prio_thread.status_msg.connect(self.log_prio_msg)
            self.prio_thread.unauthorized.connect(self.on_prio_unauthorized)
            self.prio_thread.finished_summary.connect(self.on_prio_finished)
            self.prio_thread.start()

    def on_prio_unauthorized(self):
        self.prio_console.append("⚠️ Pro Authentication Failed! Task halted.")
        self.lbl_prio_status.setText("State: Unauthorized")
        self.lbl_prio_status.setStyleSheet("color: #f38ba8; border: none;")
        self.btn_toggle_prio.setText("Enable Smart Prioritization")

    def on_prio_finished(self, summary: str):
        self.prio_console.append(f"\n⚡ Smart Priority Disabled: {summary}")
        self.lbl_prio_status.setText("State: Disabled")
        self.lbl_prio_status.setStyleSheet("color: #f38ba8; border: none;")
        self.btn_toggle_prio.setText("Enable Smart Prioritization")
        self.prio_thread = None

    def log_free_msg(self, text: str):
        self.log_console.append(f"[*] {text}")

    def log_prio_msg(self, text: str):
        self.prio_console.append(f"[Prioritizer] {text}")

    def refresh_ui(self):
        """Called whenever licensing changes."""
        if config.IS_PRO_VERSION:
            self.lock_overlay.hide()
            self.prio_control_widget.show()
        else:
            # Force close running thread if we transitioned to Free
            if self.prio_thread and self.prio_thread.isRunning():
                self.prio_thread.stop()
            self.prio_control_widget.hide()
            self.lock_overlay.show()

    def stop_all_workers(self):
        """Invoked when app shuts down or closes."""
        if self.ping_thread and self.ping_thread.isRunning():
            self.ping_thread.stop()
            self.ping_thread.wait()
        if self.dns_thread and self.dns_thread.isRunning():
            self.dns_thread.wait()
        if self.prio_thread and self.prio_thread.isRunning():
            self.prio_thread.stop()
            self.prio_thread.wait()
