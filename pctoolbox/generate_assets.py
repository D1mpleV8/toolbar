import os
import sys
from PyQt6.QtGui import QImage, QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, QRectF

def generate_png_assets():
    # Make sure we use the offscreen platform for generation
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

    # We can import QApplication after setting the platform env
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])

    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # 1. Create App Icon (64x64, circular futuristic gear/gauge icon)
    app_icon_img = QImage(64, 64, QImage.Format.Format_ARGB32)
    app_icon_img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(app_icon_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw futuristic circle background
    painter.setBrush(QColor("#1e1e2e"))
    painter.setPen(QPen(QColor("#cba6f7"), 3))
    painter.drawEllipse(4, 4, 56, 56)
    # Draw gear teeth or central details
    painter.setBrush(QColor("#89b4fa"))
    painter.drawEllipse(20, 20, 24, 24)
    # Draw central letter "T" for Toolbox
    painter.setPen(QPen(QColor("#ffffff"), 2))
    painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
    painter.drawText(QRectF(0, 0, 64, 64), Qt.AlignmentFlag.AlignCenter, "T")
    painter.end()
    app_icon_img.save(os.path.join(assets_dir, "app_icon.png"))
    print("Generated app_icon.png")

    # 2. Create Lock Icon (32x32, sleek flat orange/red lock icon)
    lock_img = QImage(32, 32, QImage.Format.Format_ARGB32)
    lock_img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(lock_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    # Draw lock body
    painter.setBrush(QColor("#f38ba8"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(6, 14, 20, 14, 3, 3)
    # Draw shackle
    shackle_pen = QPen(QColor("#f38ba8"), 3)
    painter.setPen(shackle_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawArc(10, 6, 12, 16, 0, 180 * 16)
    painter.end()
    lock_img.save(os.path.join(assets_dir, "lock.png"))
    print("Generated lock.png")

    # 3. Create Check Icon (32x32, sleek green checkmark)
    check_img = QImage(32, 32, QImage.Format.Format_ARGB32)
    check_img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(check_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    # Draw green circle
    painter.setBrush(QColor("#a6e3a1"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 28, 28)
    # Draw checkmark
    painter.setPen(QPen(QColor("#11111b"), 3))
    painter.drawLine(10, 16, 14, 20)
    painter.drawLine(14, 20, 22, 11)
    painter.end()
    check_img.save(os.path.join(assets_dir, "check.png"))
    print("Generated check.png")

    # 4. Create Tray Icon (32x32, small simplified white/blue gear)
    tray_img = QImage(32, 32, QImage.Format.Format_ARGB32)
    tray_img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(tray_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#1e1e2e"))
    painter.setPen(QPen(QColor("#89b4fa"), 2))
    painter.drawEllipse(4, 4, 24, 24)
    painter.setBrush(QColor("#f5c2e7"))
    painter.drawEllipse(11, 11, 10, 10)
    painter.end()
    tray_img.save(os.path.join(assets_dir, "tray_icon.png"))
    print("Generated tray_icon.png")

if __name__ == "__main__":
    generate_png_assets()
