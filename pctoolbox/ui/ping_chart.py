import collections
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPolygonF
from PyQt6.QtCore import Qt, QPointF

class PingChartWidget(QWidget):
    """
    Sleek, high-performance real-time scrolling latency line chart.
    Uses pure QPainter drawing for beautiful presentation without external charting libraries.
    """
    def __init__(self, parent=None, max_points: int = 50):
        super().__init__(parent)
        self.max_points = max_points
        self.data = collections.deque([0.0] * self.max_points, maxlen=self.max_points)
        self.setMinimumHeight(150)
        self.setStyleSheet("background-color: #11111b; border: 1px solid #313244; border-radius: 8px;")

    def add_ping_point(self, value: float):
        # -1.0 or less means timeout / packet loss
        if value < 0:
            self.data.append(-1.0)
        else:
            self.data.append(value)
        self.update() # Triggers repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Fill background
        painter.fillRect(self.rect(), QColor("#11111b"))

        # Draw grid lines (horizontal reference lines)
        grid_pen = QPen(QColor("#1e1e2e"), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)

        # Horizontal lines for 50ms, 100ms, 150ms
        max_val_limit = 150.0
        for ms_marker in [50.0, 100.0, 150.0]:
            y_pos = height - int((ms_marker / max_val_limit) * (height - 20)) - 10
            painter.drawLine(0, y_pos, width, y_pos)

            # Label
            painter.setPen(QColor("#45475a"))
            painter.setFont(QFont("Consolas", 8))
            painter.drawText(5, y_pos - 2, f"{int(ms_marker)} ms")
            painter.setPen(grid_pen)

        # Draw ping history
        if len(self.data) < 2:
            painter.end()
            return

        # Find visual coords
        points = []
        x_step = width / (self.max_points - 1)

        for i, val in enumerate(self.data):
            x = i * x_step
            if val < 0: # Packet Loss
                # Draw at the absolute top/bottom or interpolate?
                # Let's map packet loss to maximum height (visual spike)
                y = 10
            else:
                # Map latency to graph range (0 to 150 ms capped)
                val_clamped = min(val, max_val_limit)
                y = height - int((val_clamped / max_val_limit) * (height - 30)) - 15
            points.append(QPointF(x, y))

        # Fill color under the curve (area chart)
        area_polygon = QPolygonF()
        area_polygon.append(QPointF(0, height))
        for p in points:
            area_polygon.append(p)
        area_polygon.append(QPointF(width, height))

        painter.setBrush(QColor("rgba(137, 180, 250, 40)")) # Semi-transparent light blue
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(area_polygon)

        # Draw the main line
        line_pen = QPen(QColor("#89b4fa"), 2, Qt.PenStyle.SolidLine)
        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Draw segments, highlighting packet loss/timeout with red color
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            val_current = self.data[i+1]
            if val_current < 0 or self.data[i] < 0:
                painter.setPen(QPen(QColor("#f38ba8"), 2, Qt.PenStyle.SolidLine)) # Red for packet loss
            elif val_current > 100.0:
                painter.setPen(QPen(QColor("#fab387"), 2, Qt.PenStyle.SolidLine)) # Orange for high ping
            else:
                painter.setPen(line_pen)
            painter.drawLine(p1, p2)

        # Draw current ping label
        latest_ping = self.data[-1]
        painter.setPen(QColor("#cdd6f4"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        if latest_ping < 0:
            ping_str = "LOSS / TIMEOUT"
            painter.setPen(QColor("#f38ba8"))
        else:
            ping_str = f"Current Ping: {latest_ping:.1f} ms"
            if latest_ping < 40.0:
                painter.setPen(QColor("#a6e3a1"))
            elif latest_ping < 100.0:
                painter.setPen(QColor("#f9e2af"))
            else:
                painter.setPen(QColor("#fab387"))

        painter.drawText(width - 160, 25, ping_str)
        painter.end()
