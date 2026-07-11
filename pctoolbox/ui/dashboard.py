from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from pctoolbox import config

class DashboardView(QWidget):
    """
    Sleek, futuristic performance style speedometer / telemetry metrics tab.
    Provides system speedometers, licensing details and real-time statistics.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title / Subtitle Banner
        title_label = QLabel("🚀 PC Toolbox Dashboard")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #cba6f7;")
        layout.addWidget(title_label)

        desc_label = QLabel("Ultimate system utility suite. Built for extreme gaming performance and automation.")
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setStyleSheet("color: #a6adc8;")
        layout.addWidget(desc_label)

        # Telemetry / Performance Grid Frame
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 12px;
            }
        """)
        metrics_layout = QHBoxLayout(metrics_frame)
        metrics_layout.setContentsMargins(15, 15, 15, 15)

        # Metric 1: CPU Health Speedometer
        cpu_layout = QVBoxLayout()
        cpu_title = QLabel("System Health")
        cpu_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        cpu_title.setStyleSheet("color: #89b4fa; border: none;")
        cpu_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cpu_value = QLabel("98%")
        self.cpu_value.setFont(QFont("Consolas", 28, QFont.Weight.Bold))
        self.cpu_value.setStyleSheet("color: #a6e3a1; border: none;")
        self.cpu_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cpu_layout.addWidget(cpu_title)
        cpu_layout.addWidget(self.cpu_value)
        metrics_layout.addLayout(cpu_layout)

        # Divider
        div1 = QFrame()
        div1.setFrameShape(QFrame.Shape.VLine)
        div1.setStyleSheet("background-color: #313244;")
        metrics_layout.addWidget(div1)

        # Metric 2: Memory Allocated
        ram_layout = QVBoxLayout()
        ram_title = QLabel("RAM Allocated")
        ram_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        ram_title.setStyleSheet("color: #89b4fa; border: none;")
        ram_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ram_value = QLabel("4.2 / 16 GB")
        self.ram_value.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.ram_value.setStyleSheet("color: #f5e0dc; border: none;")
        self.ram_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ram_layout.addWidget(ram_title)
        ram_layout.addWidget(self.ram_value)
        metrics_layout.addLayout(ram_layout)

        # Divider
        div2 = QFrame()
        div2.setFrameShape(QFrame.Shape.VLine)
        div2.setStyleSheet("background-color: #313244;")
        metrics_layout.addWidget(div2)

        # Metric 3: Game Optimizations Active
        opt_layout = QVBoxLayout()
        opt_title = QLabel("Optimizations")
        opt_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        opt_title.setStyleSheet("color: #89b4fa; border: none;")
        opt_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.opt_status = QLabel("Ready")
        self.opt_status.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.opt_status.setStyleSheet("color: #f9e2af; border: none;")
        self.opt_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        opt_layout.addWidget(opt_title)
        opt_layout.addWidget(self.opt_status)
        metrics_layout.addLayout(opt_layout)

        layout.addWidget(metrics_frame)

        # Steam / Licensing Status Card
        license_frame = QFrame()
        license_frame.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border: 1px dashed #cba6f7;
                border-radius: 8px;
            }
        """)
        license_layout = QHBoxLayout(license_frame)

        self.license_icon = QLabel()
        self.update_license_icon()
        license_layout.addWidget(self.license_icon)

        self.license_text = QLabel()
        self.license_text.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.update_license_text()
        license_layout.addWidget(self.license_text)
        license_layout.addStretch()

        layout.addWidget(license_frame)
        layout.addStretch()

    def update_license_icon(self):
        icon_path = config.get_asset_path("check.png" if config.IS_PRO_VERSION else "lock.png")
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            self.license_icon.setPixmap(pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.license_icon.setText("🔑" if config.IS_PRO_VERSION else "🔒")

    def update_license_text(self):
        if config.IS_PRO_VERSION:
            self.license_text.setText("Steam License Status: PRO VERSION ACTIVATED (All Advanced Utilities Unlocked)")
            self.license_text.setStyleSheet("color: #a6e3a1;")
        else:
            self.license_text.setText("Steam License Status: FREE VERSION (Advanced CV Macros & Game Optimizer Locked)")
            self.license_text.setStyleSheet("color: #f38ba8;")

    def refresh_ui(self):
        """Called whenever global license state or telemetry changes."""
        self.update_license_icon()
        self.update_license_text()
        if config.IS_PRO_VERSION:
            self.opt_status.setText("Ultra Mode")
            self.opt_status.setStyleSheet("color: #a6e3a1; border: none;")
        else:
            self.opt_status.setText("Standard Mode")
            self.opt_status.setStyleSheet("color: #f9e2af; border: none;")
