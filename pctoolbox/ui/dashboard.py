import os
import sys
import shutil
import psutil
import secrets
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QProgressBar, QPushButton, QGridLayout)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QBrush, QPolygonF, QRadialGradient, QLinearGradient
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from pctoolbox import config
from pctoolbox.threads.backend_sensors import BackendSensorsThread

class GaugeDialWidget(QWidget):
    """
    Masterpiece Circular Gauge Dial (Car Speedometer style).
    Specifies animated sweep needle, premium outer glowing arc, smooth inner track,
    and massive, elegant metric text directly in the center.
    Utilizes Cyber-Blue (#00F0FF) standard glows shifting dynamically
    to Electric Red (#FF003C) when telemetry crosses 80%.
    """
    def __init__(self, title="CPU", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = 0.0 # Usage percentage (0 to 100)
        self.temp_value = "N/A" # Celsius temp reading or "N/A"
        self.setMinimumSize(220, 220)

    def set_value(self, val, temp="N/A"):
        self.value = max(0.0, min(100.0, float(val) if val != "N/A" else 0.0))
        self.temp_value = temp
        self.update() # Triggers premium QPainter repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height)

        # Center coordinates
        cx = width / 2.0
        cy = height / 2.0

        painter.save()
        painter.translate(cx, cy)

        # Color palette setup
        is_numeric_temp = isinstance(self.temp_value, (int, float))
        is_hot = (self.value >= 80.0 or (is_numeric_temp and self.temp_value >= 75))
        accent_color = QColor("#FF003C") if is_hot else QColor("#00F0FF")
        glow_color = QColor("rgba(255, 0, 60, 40)") if is_hot else QColor("rgba(0, 240, 255, 40)")

        # 1. Draw Glassmorphic Translucent Container Background
        painter.setPen(Qt.PenStyle.NoPen)
        grad = QRadialGradient(0, 0, side/2.1)
        grad.setColorAt(0.0, QColor("rgba(22, 27, 34, 150)"))
        grad.setColorAt(1.0, QColor("rgba(11, 14, 20, 220)"))
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QRectF(-side/2.1, -side/2.1, side/1.05, side/1.1))

        # Thin outer glass rim border (#2A3241)
        rim_pen = QPen(QColor("#2A3241"), 1.5)
        painter.setPen(rim_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(-side/2.1, -side/2.1, side/1.05, side/1.1))

        # 2. Draw outer glowing arc (aesthetic performance indicator)
        track_rect = QRectF(-side/2.8, -side/2.8, side/1.4, side/1.35)

        # Glow layer
        glow_pen = QPen(glow_color, 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(glow_pen)
        painter.drawArc(track_rect, 135 * 16, 270 * 16)

        # Smooth inner track
        track_pen = QPen(QColor("#161B22"), 8)
        painter.setPen(track_pen)
        painter.drawArc(track_rect, 135 * 16, 270 * 16)

        # Active glowing meter
        active_pen = QPen(accent_color, 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(active_pen)
        sweep_angle = int((self.value / 100.0) * 270)
        painter.drawArc(track_rect, (225 - sweep_angle) * 16, sweep_angle * 16)

        # 3. Draw Cyberdial Tick marks
        painter.setPen(QPen(QColor("rgba(0, 240, 255, 30)"), 1))
        for i in range(19):
            angle = 135 + i * 15
            painter.save()
            painter.rotate(angle)
            if i % 3 == 0:
                painter.setPen(QPen(accent_color, 1.5))
                painter.drawLine(int(side/2.8), 0, int(side/2.55), 0)
            else:
                painter.drawLine(int(side/2.8), 0, int(side/2.7), 0)
            painter.restore()

        # 4. Draw Animated Sweep Needle
        needle_angle = 135 + (self.value / 100.0) * 270
        painter.save()
        painter.rotate(needle_angle)

        needle_pen = QPen(accent_color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(needle_pen)
        painter.drawLine(0, 0, int(side/2.9), 0)
        painter.restore()

        # Center cap
        painter.setBrush(accent_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(-6, -6, 12, 16))

        # 5. Massive, Elegant Center Telemetry Text
        # Core usage %
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 26, QFont.Weight.Light)) # Large thin modern font
        painter.drawText(QRectF(-75, -25, 150, 40), Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}")

        # Small elegant % label
        painter.setPen(QColor("rgba(255, 255, 255, 120)"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(QRectF(30, -15, 20, 20), Qt.AlignmentFlag.AlignLeft, "%")

        # Core temperature reading directly underneath
        temp_disp = f"{self.temp_value}°C" if is_numeric_temp else "N/A"
        temp_color = QColor("#FF003C") if (is_numeric_temp and self.temp_value >= 75) else QColor("#fab387")
        painter.setPen(temp_color)
        painter.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        painter.drawText(QRectF(-50, 18, 100, 20), Qt.AlignmentFlag.AlignCenter, temp_disp)

        # Upper Title Label
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(QColor("rgba(0, 240, 255, 150)"))
        painter.drawText(QRectF(-60, -side/3.8, 120, 20), Qt.AlignmentFlag.AlignCenter, self.title)

        painter.restore()

class DashboardView(QWidget):
    """
    Sleek, hyper-modern, glassmorphic "Dark Matter" Theme Dashboard Tab (#0B0E14).
    Driven by real-time hardware signals using the BackendSensorsThread.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

        # Instantiate low-level real sensors thread
        self.sensors_thread = BackendSensorsThread()
        self.sensors_thread.telemetry_received.connect(self.update_telemetry_widgets)
        self.sensors_thread.start()

    def init_ui(self):
        # Dark Matter Base Theme Styling
        self.setStyleSheet("""
            QWidget {
                background-color: #0B0E14;
            }
            QFrame {
                background-color: #161B22; /* Frosted Glass darker tone */
                border: 1px solid #2A3241; /* Glass border */
                border-radius: 12px;
            }
            QLabel {
                color: #cdd6f4;
                border: none;
                background: transparent;
            }
            QProgressBar {
                border: 1px solid #2A3241;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                background-color: #0B0E14;
            }
            QProgressBar::chunk {
                background-color: #00F0FF; /* Cyber-Blue */
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header Title
        title_lbl = QLabel("🚀 PC TOOLBOX DASHBOARD")
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #00F0FF; background: transparent; border: none; letter-spacing: 1px;")
        layout.addWidget(title_lbl)

        # 1. Top Section: Two circular Dial Speedometer gauges side-by-side
        gauges_frame = QFrame()
        gauges_layout = QHBoxLayout(gauges_frame)
        gauges_layout.setContentsMargins(20, 20, 20, 20)
        gauges_layout.setSpacing(30)

        self.cpu_gauge = GaugeDialWidget(title="CPU STATUS")
        self.gpu_gauge = GaugeDialWidget(title="GPU STATUS")

        gauges_layout.addWidget(self.cpu_gauge)
        gauges_layout.addWidget(self.gpu_gauge)
        layout.addWidget(gauges_frame)

        # 2. Middle Section: Sleek thin progress bars for actual RAM and SSD
        middle_frame = QFrame()
        mid_layout = QVBoxLayout(middle_frame)
        mid_layout.setContentsMargins(20, 15, 20, 15)
        mid_layout.setSpacing(12)

        self.lbl_ram_title = QLabel("System Memory Overhead (Used: -- GB / Total: -- GB)")
        self.lbl_ram_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.lbl_ram_title.setStyleSheet("color: #a6adc8;")
        mid_layout.addWidget(self.lbl_ram_title)

        self.ram_bar = QProgressBar()
        self.ram_bar.setMaximum(100)
        self.ram_bar.setFixedHeight(12)
        mid_layout.addWidget(self.ram_bar)

        # SSD Progress Bar
        self.lbl_ssd_title = QLabel("System Storage Capacity (C:/ Drive)")
        self.lbl_ssd_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.lbl_ssd_title.setStyleSheet("color: #a6adc8;")
        mid_layout.addWidget(self.lbl_ssd_title)

        self.ssd_bar = QProgressBar()
        self.ssd_bar.setMaximum(100)
        self.ssd_bar.setFixedHeight(12)
        self.ssd_bar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: #cba6f7;
            }
        """)
        mid_layout.addWidget(self.ssd_bar)

        layout.addWidget(middle_frame)

        # 3. Bottom Section: Action buttons
        bottom_frame = QFrame()
        bottom_layout = QGridLayout(bottom_frame)
        bottom_layout.setContentsMargins(15, 15, 15, 15)
        bottom_layout.setSpacing(15)

        self.btn_stress = QPushButton("🔥 Run CPU Stress Test")
        self.btn_stress.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_stress.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 60, 40); /* Electric Red glass */
                color: #FF003C;
                border: 1px solid #FF003C;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #FF003C;
                color: #ffffff;
            }
        """)
        bottom_layout.addWidget(self.btn_stress, 0, 0)

        self.btn_overlay = QPushButton("🖥️ Enable OSD Monitor")
        self.btn_overlay.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_overlay.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 240, 255, 40); /* Cyber-Blue glass */
                color: #00F0FF;
                border: 1px solid #00F0FF;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #00F0FF;
                color: #11111b;
            }
        """)
        bottom_layout.addWidget(self.btn_overlay, 0, 1)

        layout.addWidget(bottom_frame)

        # License strip
        self.license_strip = QFrame()
        self.license_strip.setStyleSheet("""
            QFrame {
                background-color: rgba(22, 27, 34, 120);
                border: 1px dashed rgba(203, 166, 247, 100);
                border-radius: 8px;
            }
        """)
        strip_lay = QHBoxLayout(self.license_strip)
        self.lbl_license = QLabel()
        self.lbl_license.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
        strip_lay.addWidget(self.lbl_license)
        layout.addWidget(self.license_strip)

    def update_telemetry_widgets(self, m: dict):
        """Thread-safe UI callback that receives real low-level sensor values."""
        # 1. Update Speedometers with REAL metrics
        self.cpu_gauge.set_value(m.get("cpu_perc", 0.0), m.get("cpu_temp", "N/A"))
        self.gpu_gauge.set_value(m.get("gpu_perc", 0.0), m.get("gpu_temp", "N/A"))

        # 2. Update RAM bar
        ram_perc = m.get("ram_perc", 0.0)
        self.ram_bar.setValue(int(ram_perc))
        self.lbl_ram_title.setText(f"System Memory Overhead (Used: {m.get('ram_used', 0.0):.1f} GB / Total: {m.get('ram_total', 16.0):.1f} GB)")

        # 3. Update SSD bar
        ssd_perc = m.get("ssd_perc", 0.0)
        self.ssd_bar.setValue(int(ssd_perc))
        self.lbl_ssd_title.setText(f"Primary Drive Allocation (Used: {m.get('ssd_used', 0.0):.1f} GB / Total: {m.get('ssd_total', 250.0):.1f} GB)")

    def refresh_ui(self):
        """Called dynamically upon licensing changes."""
        if config.IS_PRO_VERSION:
            self.lbl_license.setText("Steamworks Authentication: PRO EDITION ENABLED (All Advanced Dials Unlocked)")
            self.lbl_license.setStyleSheet("color: #a6e3a1;")
        else:
            self.lbl_license.setText("Steamworks Authentication: STANDBY (Click top toggle to simulate Pro edition)")
            self.lbl_license.setStyleSheet("color: #f38ba8;")

    def stop_all_workers(self):
        if self.sensors_thread and self.sensors_thread.isRunning():
            self.sensors_thread.stop()
            self.sensors_thread.wait()
