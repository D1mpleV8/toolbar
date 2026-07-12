import os
import sys
import shutil
import psutil
import secrets
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QProgressBar, QPushButton, QGridLayout)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from pctoolbox import config

class GaugeDialWidget(QWidget):
    """
    Hyper-Modern Circular Gauge Dial (Car Speedometer style).
    Specifies animated sweep needle, with Cyber-Blue (#00F0FF) standard accents,
    shifting dynamically to Electric Red (#FF003C) when usage crosses 80%.
    """
    def __init__(self, title="CPU", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = 0.0 # From 0 to 100
        self.temp_value = 42 # In degrees Celsius
        self.setMinimumSize(180, 180)

    def set_value(self, val, temp=42):
        self.value = max(0.0, min(100.0, val))
        self.temp_value = temp
        self.update() # repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height)

        # Center coordinates
        cx = width / 2.0
        cy = height / 2.0

        # Background Dial Arc
        painter.save()
        painter.translate(cx, cy)

        # Outer Glass Ring
        glass_pen = QPen(QColor("rgba(203, 166, 247, 40)"), 4)
        painter.setPen(glass_pen)
        painter.setBrush(QColor("rgba(30, 30, 46, 120)")) # Translucent Dark Matter
        painter.drawEllipse(QRectF(-side/2.2, -side/2.2, side/1.1, side/1.1))

        # Dynamic color decision based on high thresholds (> 80%)
        is_hot = (self.value >= 80.0 or self.temp_value >= 75)
        accent_color = QColor("#FF003C") if is_hot else QColor("#00F0FF")

        # Draw ticks/track arc
        track_rect = QRectF(-side/2.6, -side/2.6, side/1.3, side/1.3)
        track_pen = QPen(QColor("#1e1e2e"), 8)
        painter.setPen(track_pen)
        painter.drawArc(track_rect, 135 * 16, 270 * 16)

        # Draw Active Value Arc
        active_pen = QPen(accent_color, 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(active_pen)
        sweep_angle = int((self.value / 100.0) * 270)
        painter.drawArc(track_rect, (225 - sweep_angle) * 16, sweep_angle * 16)

        # Draw the Dial Ticks
        painter.setPen(QPen(QColor("#45475a"), 1))
        for i in range(11):
            angle = 135 + i * 27
            painter.save()
            painter.rotate(angle)
            painter.drawLine(int(side/2.6), 0, int(side/2.4), 0)
            painter.restore()

        # Draw Animated Sweep Needle
        needle_angle = 135 + (self.value / 100.0) * 270
        painter.save()
        painter.rotate(needle_angle)

        needle_pen = QPen(accent_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(needle_pen)
        painter.drawLine(0, 0, int(side/2.5), 0)
        painter.restore()

        # Center cap
        painter.setBrush(accent_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(-8, -8, 16, 16))

        # Central text readout (Usage % and Core Temp)
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        painter.drawText(QRectF(-50, -10, 100, 30), Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}%")

        # Display Core Temperature readout
        temp_color = QColor("#FF003C") if self.temp_value >= 75 else QColor("#fab387")
        painter.setPen(temp_color)
        painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        painter.drawText(QRectF(-50, side/6.5, 100, 20), Qt.AlignmentFlag.AlignCenter, f"{self.temp_value}°C")

        # Title
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
        painter.setPen(QColor("#a6adc8"))
        painter.drawText(QRectF(-50, -side/4.5, 100, 20), Qt.AlignmentFlag.AlignCenter, self.title)

        painter.restore()

class DashboardView(QWidget):
    """
    Sleek, hyper-modern, glassmorphic "Dark Matter" Theme Dashboard Tab (#0B0E14).
    Contains side-by-side circular gauges for CPU & GPU loads and core temperatures.
    Mid-section linear bars tracking real dynamic psutil RAM sizes (total 32GB corrected)
    and SSD utilization boundaries.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

        # Configure local auto-telemetry refresher
        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self.poll_local_system_telemetry)
        self.telemetry_timer.start(1000) # Poll every second

    def init_ui(self):
        # Dark Matter Base Theme Styling
        self.setStyleSheet("""
            QWidget {
                background-color: #0B0E14;
            }
            QFrame {
                background-color: rgba(15, 20, 28, 180);
                border: 1px solid rgba(0, 240, 255, 60);
                border-radius: 10px;
            }
            QLabel {
                color: #cdd6f4;
                border: none;
                background: transparent;
            }
            QProgressBar {
                border: 1px solid rgba(49, 50, 68, 120);
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                background-color: #11111b;
            }
            QProgressBar::chunk {
                background-color: #00F0FF;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Header Title
        title_lbl = QLabel("🚀 Steam PC Power Dashboard")
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #00F0FF; background: transparent; border: none;")
        layout.addWidget(title_lbl)

        # 1. Top Section: Two circular Dial Speedometer gauges side-by-side
        gauges_frame = QFrame()
        gauges_layout = QHBoxLayout(gauges_frame)
        gauges_layout.setContentsMargins(15, 15, 15, 15)
        gauges_layout.setSpacing(25)

        self.cpu_gauge = GaugeDialWidget(title="CPU LOAD")
        self.gpu_gauge = GaugeDialWidget(title="GPU LOAD")

        gauges_layout.addWidget(self.cpu_gauge)
        gauges_layout.addWidget(self.gpu_gauge)
        layout.addWidget(gauges_frame)

        # 2. Middle Section: Sleek thin progress bars for actual RAM and SSD
        middle_frame = QFrame()
        mid_layout = QVBoxLayout(middle_frame)
        mid_layout.setContentsMargins(15, 12, 15, 12)
        mid_layout.setSpacing(10)

        # Actual RAM Detection Bug Fixed using psutil
        ram_total_gb = psutil.virtual_memory().total / (1024**3)

        self.lbl_ram_title = QLabel(f"Actual Memory Overhead (Total System: {ram_total_gb:.1f} GB)")
        self.lbl_ram_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        mid_layout.addWidget(self.lbl_ram_title)

        self.ram_bar = QProgressBar()
        self.ram_bar.setMaximum(100)
        self.ram_bar.setFixedHeight(12)
        mid_layout.addWidget(self.ram_bar)

        # SSD Progress Bar
        self.lbl_ssd_title = QLabel("System Storage Capacity (C:/ Drive)")
        self.lbl_ssd_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
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
        bottom_layout.setContentsMargins(12, 12, 12, 12)
        bottom_layout.setSpacing(10)

        self.btn_stress = QPushButton("🔥 Run Heavy Stress Test")
        self.btn_stress.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_stress.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 60, 200); /* Electric Red */
                color: #ffffff;
                border: 1px solid #FF003C;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FF003C;
            }
        """)
        bottom_layout.addWidget(self.btn_stress, 0, 0)

        self.btn_overlay = QPushButton("🖥️ Enable FPS OSD Overlay")
        self.btn_overlay.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_overlay.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 240, 255, 40); /* Cyber-Blue */
                color: #00F0FF;
                border: 1px solid #00F0FF;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(0, 240, 255, 100);
            }
        """)
        bottom_layout.addWidget(self.btn_overlay, 0, 1)

        layout.addWidget(bottom_frame)

        # License strip
        self.license_strip = QFrame()
        self.license_strip.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 20, 28, 120);
                border: 1px dashed rgba(203, 166, 247, 100);
                border-radius: 6px;
            }
        """)
        strip_lay = QHBoxLayout(self.license_strip)
        self.lbl_license = QLabel()
        self.lbl_license.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
        strip_lay.addWidget(self.lbl_license)
        layout.addWidget(self.license_strip)

        # Initial Telemetry Poll
        self.poll_local_system_telemetry()

    def poll_local_system_telemetry(self):
        """Refreshes hardware load telemetry gauges on clock triggers."""
        # 1. CPU Usage & simulated CPU Core temp
        cpu_perc = psutil.cpu_percent()
        cpu_temp = int(45 + cpu_perc * 0.4 + secrets.randbelow(4))
        self.cpu_gauge.set_value(cpu_perc, cpu_temp)

        # 2. Simulated GPU Telemetry
        gpu_perc = min(100.0, max(0.0, cpu_perc * 0.9 + 5.0))
        gpu_temp = int(50 + gpu_perc * 0.35 + secrets.randbelow(3))
        self.gpu_gauge.set_value(gpu_perc, gpu_temp)

        # 3. Dynamic Memory/RAM
        mem = psutil.virtual_memory()
        self.ram_bar.setValue(int(mem.percent))
        ram_used_gb = mem.used / (1024**3)
        ram_total_gb = mem.total / (1024**3)
        self.lbl_ram_title.setText(f"System Memory Overhead (Used: {ram_used_gb:.1f} GB / Total: {ram_total_gb:.1f} GB)")

        # 4. Storage/Disk space C:/ drive
        try:
            usage = shutil.disk_usage("/")
            ssd_perc = int((usage.used / usage.total) * 100.0)
            self.ssd_bar.setValue(ssd_perc)
            self.lbl_ssd_title.setText(f"Primary Drive Allocation (Used: {usage.used/(1024**3):.1f} GB / Total: {usage.total/(1024**3):.1f} GB)")
        except Exception:
            self.ssd_bar.setValue(45)

    def refresh_ui(self):
        """Called dynamically upon licensing changes."""
        if config.IS_PRO_VERSION:
            self.lbl_license.setText("Steamworks Authentication: PRO EDITION ENABLED (All Advanced Dials Unlocked)")
            self.lbl_license.setStyleSheet("color: #a6e3a1;")
        else:
            self.lbl_license.setText("Steamworks Authentication: STANDBY (Click top toggle to simulate Pro edition)")
            self.lbl_license.setStyleSheet("color: #f38ba8;")
