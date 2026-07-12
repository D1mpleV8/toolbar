import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QPoint

class OSDOverlayWidget(QWidget):
    """
    RivaTuner style transparent in-game Performance OSD (PRO FEATURE).
    Renders frameless, stays-on-top, click-through overlay showing live telemetry.
    Can be dragged by standard mouse grabs when unlocked.
    """
    def __init__(self):
        super().__init__()

        # Stays on top, frameless, transparent for inputs (click-through overlay)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Enable click-through natively so players can click through OSD directly into game
        # To let users drag the OSD, input transparency can be toggled.
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForInput, True)

        self.resize(250, 160)
        self.drag_position = QPoint()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Translucent glassmorphic container panel (mimics modern gaming overlay)
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(17, 17, 27, 180); /* Translucent dark background */
                border: 1px solid rgba(137, 180, 250, 120); /* Light blue border */
                border-radius: 6px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(6)

        # OSD Header
        self.lbl_title = QLabel("PC TOOLBOX OSD")
        self.lbl_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: #89b4fa; border: none; background: transparent;")
        container_layout.addWidget(self.lbl_title)

        # 1. FPS Label
        self.lbl_fps = QLabel("FPS: --")
        self.lbl_fps.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        self.lbl_fps.setStyleSheet("color: #a6e3a1; border: none; background: transparent;")
        container_layout.addWidget(self.lbl_fps)

        # 2. CPU Telemetry
        self.lbl_cpu = QLabel("CPU: -- °C (--%)")
        self.lbl_cpu.setFont(QFont("Consolas", 10))
        self.lbl_cpu.setStyleSheet("color: #fab387; border: none; background: transparent;")
        container_layout.addWidget(self.lbl_cpu)

        # 3. GPU Telemetry
        self.lbl_gpu = QLabel("GPU: -- °C (--%)")
        self.lbl_gpu.setFont(QFont("Consolas", 10))
        self.lbl_gpu.setStyleSheet("color: #f38ba8; border: none; background: transparent;")
        container_layout.addWidget(self.lbl_gpu)

        # 4. RAM Telemetry
        self.lbl_ram = QLabel("MEM: -- GB")
        self.lbl_ram.setFont(QFont("Consolas", 10))
        self.lbl_ram.setStyleSheet("color: #cba6f7; border: none; background: transparent;")
        container_layout.addWidget(self.lbl_ram)

        layout.addWidget(container)

    def update_telemetry(self, metrics: dict):
        """Updates OSD text with fresh hardware parameters."""
        self.lbl_fps.setText(f"FPS: {metrics.get('fps', 0)}")
        self.lbl_cpu.setText(f"CPU: {metrics.get('cpu_temp', 0)}°C ({metrics.get('cpu_load', 0)}%)")
        self.lbl_gpu.setText(f"GPU: {metrics.get('gpu_temp', 0)}°C ({metrics.get('gpu_load', 0)}%)")
        self.lbl_ram.setText(f"MEM: {metrics.get('ram_alloc', 0.0):.1f} GB")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
