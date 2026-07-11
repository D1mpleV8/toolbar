import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QListWidget, QListWidgetItem, QLabel, QFrame)
from PyQt6.QtGui import QFont, QKeyEvent, QColor
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from pctoolbox import config
from pctoolbox.threads.quick_launcher import QuickLauncherThread

class QuickLauncher(QWidget):
    """
    Sleek, glassmorphic translucent Alt+Space floating quick launch search bar.
    Appears floating on top, frameless, and lets users search files and apps.
    Advanced AI questions (? [prompt]) are elegantly gated by Pro licensing check.
    """
    status_msg = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_thread = None

        # Configure frameless stays-on-top window styling
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint |
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(650, 420)
        self.init_ui()

        # Drag Window logic helpers
        self.drag_position = QPoint()

    def init_ui(self):
        # Master Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        # Glassmorphic Translucent Container Frame
        self.glass_frame = QFrame()
        self.glass_frame.setObjectName("GlassFrame")
        self.glass_frame.setStyleSheet("""
            QFrame#GlassFrame {
                background-color: rgba(30, 30, 46, 220); /* Sleek translucent dark purple/blue */
                border: 2px solid rgba(203, 166, 247, 100); /* Translucent purple border */
                border-radius: 12px;
            }
        """)
        frame_layout = QVBoxLayout(self.glass_frame)
        frame_layout.setContentsMargins(15, 15, 15, 15)
        frame_layout.setSpacing(10)

        # Header Title
        title_bar = QHBoxLayout()
        lbl_title = QLabel("⚡ Quick Launcher")
        lbl_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #cba6f7; background: transparent; border: none;")
        title_bar.addWidget(lbl_title)

        title_bar.addStretch()

        lbl_info = QLabel("Press [Alt+Space] to toggle | Prefix [?] for Pro AI")
        lbl_info.setFont(QFont("Segoe UI", 8))
        lbl_info.setStyleSheet("color: #a6adc8; background: transparent; border: none;")
        title_bar.addWidget(lbl_info)
        frame_layout.addLayout(title_bar)

        # Search Bar Input Field
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search apps, files, or type '? ask ChatGPT'...")
        self.txt_search.setFont(QFont("Segoe UI", 12))
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background-color: rgba(17, 17, 27, 200);
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 10px 15px;
            }
            QLineEdit:focus {
                border: 1px solid #cba6f7;
            }
        """)
        self.txt_search.textChanged.connect(self.trigger_search)
        frame_layout.addWidget(self.txt_search)

        # List Widget for Search Results
        self.results_list = QListWidget()
        self.results_list.setFont(QFont("Segoe UI", 10))
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(17, 17, 27, 150);
                border: 1px solid #313244;
                border-radius: 6px;
                color: #cdd6f4;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: rgba(137, 180, 250, 50);
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
            }
        """)
        self.results_list.itemActivated.connect(self.on_item_activated)
        frame_layout.addWidget(self.results_list)

        # Status & Telemetry Bar
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setFont(QFont("Segoe UI", 8))
        self.lbl_status.setStyleSheet("color: #a6adc8; background: transparent; border: none;")
        frame_layout.addWidget(self.lbl_status)

        layout.addWidget(self.glass_frame)

    def trigger_search(self):
        query = self.txt_search.text().strip()
        if not query:
            self.results_list.clear()
            self.lbl_status.setText("Ready")
            return

        # Cancel active searches safely
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.disconnect()
            self.search_thread.terminate()

        self.search_thread = QuickLauncherThread(query=query)
        self.search_thread.search_completed.connect(self.on_search_results)
        self.search_thread.status_changed.connect(self.lbl_status.setText)
        self.search_thread.start()

    def on_search_results(self, results):
        self.results_list.clear()
        if not results:
            item = QListWidgetItem("No matching local files or applications found.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.results_list.addItem(item)
            return

        for r in results:
            name = r["name"]
            category = r["type"]
            path = r["path"]

            # Stylize display item
            item_text = f"[{category}] {name}"
            list_item = QListWidgetItem(item_text)

            # Save raw data attributes internally
            list_item.setData(Qt.ItemDataRole.UserRole, path)
            list_item.setData(Qt.ItemDataRole.UserRole + 1, category)

            # Highlight Pro Locked features elegantly with distinct styling
            if category == "PRO LOCKED":
                list_item.setForeground(QColor("#f38ba8"))
                list_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                list_item.setText(f"🔒 PRO LOCKED FEATURE - Prefix ? (ChatGPT Query) requires Steam Pro version!")
            elif category == "ChatGPT Response":
                list_item.setForeground(QColor("#a6e3a1"))

            self.results_list.addItem(list_item)

        # Auto-select the first result to support direct keyboard Enter execution
        self.results_list.setCurrentRow(0)

    def on_item_activated(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        category = item.data(Qt.ItemDataRole.UserRole + 1)

        if path == "PRO_LOCKED":
            self.lbl_status.setText("Status: Upgrade to PC Toolbox Pro on Steam to unlock AI Queries!")
            return

        if not path:
            return

        # Simulate execution of target action
        self.lbl_status.setText(f"Executing: {path}")
        self.status_msg.emit(f"Activated: {path}")

        # In a real app we'd trigger os.startfile(path) or deep-link navigation.
        # Hide launcher upon successful selection
        self.hide()

    # Make the frameless window draggable
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    # Handle close / escape hotkeys natively
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            cur_item = self.results_list.currentItem()
            if cur_item:
                self.on_item_activated(cur_item)
        else:
            super().keyPressEvent(event)
