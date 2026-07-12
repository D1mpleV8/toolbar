from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QFrame, QListWidget,
                             QListWidgetItem, QSlider)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from pctoolbox import config
from pctoolbox.threads.window_manager import WindowManagerThread
from pctoolbox.threads.osd_overlay import OSDOverlayThread
from pctoolbox.ui.osd_overlay import OSDOverlayWidget

class WindowManagerView(QWidget):
    """
    Window Manager & OSD overlay tab.
    Integrates standard window pin always-on-top, transparency controls,
    and premium in-game hardware monitoring (OSD) gated by IS_PRO_VERSION.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scan_thread = None
        self.osd_thread = None
        self.osd_widget = None # Stored floating OSD window reference
        self.init_ui()

    def init_ui(self):
        # Two-Column Master Layout (Left: Window Pin & Alpha, Right: Premium OSD)
        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(15, 15, 15, 15)
        master_layout.setSpacing(15)

        # Left Column: Free Utility Pane
        left_pane = QFrame()
        left_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)

        free_title = QLabel("🖼️ Always-on-Top & Alpha Manager")
        free_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        free_title.setStyleSheet("color: #89b4fa; border: none;")
        left_layout.addWidget(free_title)

        desc = QLabel("Set any running application to stay always pinned on top of others, or customize window opacity dynamically.")
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #a6adc8; border: none;")
        desc.setWordWrap(True)
        left_layout.addWidget(desc)

        # Controls row
        ctrl_layout = QHBoxLayout()
        self.btn_scan = QPushButton("Scan Windows")
        self.btn_scan.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_scan.setStyleSheet("""
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
        self.btn_scan.clicked.connect(self.scan_running_windows)
        ctrl_layout.addWidget(self.btn_scan)

        self.btn_pin = QPushButton("Pin Selected")
        self.btn_pin.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_pin.setEnabled(False)
        self.btn_pin.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #cba6f7;
                color: #11111b;
            }
        """)
        self.btn_pin.clicked.connect(self.pin_selected_window)
        ctrl_layout.addWidget(self.btn_pin)

        self.btn_unpin = QPushButton("Unpin")
        self.btn_unpin.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_unpin.setEnabled(False)
        self.btn_unpin.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #fab387;
                color: #11111b;
            }
        """)
        self.btn_unpin.clicked.connect(self.unpin_selected_window)
        ctrl_layout.addWidget(self.btn_unpin)
        ctrl_layout.addStretch()
        left_layout.addLayout(ctrl_layout)

        # Scanned window list widget
        self.windows_list = QListWidget()
        self.windows_list.setFont(QFont("Segoe UI", 9))
        self.windows_list.setStyleSheet("""
            QListWidget {
                background-color: #11111b;
                border: 1px solid #313244;
                border-radius: 6px;
                color: #cdd6f4;
                padding: 5px;
            }
            QListWidget::item {
                padding: 6px;
            }
            QListWidget::item:selected {
                background-color: rgba(137, 180, 250, 50);
                color: #ffffff;
            }
        """)
        self.windows_list.itemSelectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.windows_list)

        # Opacity Slider panel
        self.opacity_frame = QFrame()
        self.opacity_frame.setEnabled(False)
        self.opacity_frame.setStyleSheet("background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 6px;")
        op_layout = QHBoxLayout(self.opacity_frame)

        lbl_op = QLabel("Opacity:")
        lbl_op.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        lbl_op.setStyleSheet("color: #cdd6f4; border: none; background: transparent;")
        op_layout.addWidget(lbl_op)

        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setRange(20, 100)
        self.slider_opacity.setValue(100)
        self.slider_opacity.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #313244;
                height: 6px;
                background: #11111b;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #89b4fa;
                border: none;
                width: 14px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 7px;
            }
        """)
        self.slider_opacity.valueChanged.connect(self.change_window_opacity)
        op_layout.addWidget(self.slider_opacity)

        self.lbl_opacity_val = QLabel("100%")
        self.lbl_opacity_val.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.lbl_opacity_val.setStyleSheet("color: #89b4fa; border: none; background: transparent;")
        op_layout.addWidget(self.lbl_opacity_val)
        left_layout.addWidget(self.opacity_frame)

        # Logs
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
        self.log_console.setMaximumHeight(80)
        left_layout.addWidget(self.log_console)

        master_layout.addWidget(left_pane, 3)

        # Right Column: Premium OSD Overlay (Pro feature)
        self.right_pane = QFrame()
        self.right_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        self.right_master_layout = QVBoxLayout(self.right_pane)
        self.right_master_layout.setContentsMargins(0, 0, 0, 0)

        # Pro controls widget
        self.pro_control_widget = QWidget()
        pro_layout = QVBoxLayout(self.pro_control_widget)
        pro_layout.setContentsMargins(15, 15, 15, 15)
        pro_layout.setSpacing(12)

        pro_title = QLabel("🖥️ Performance OSD Overlay")
        pro_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        pro_title.setStyleSheet("color: #fab387; border: none;")
        pro_layout.addWidget(pro_title)

        pro_desc = QLabel("Displays FPS, GPU, and CPU telemetry overlays directly on top of DirectX/OpenGL games natively, utilizing highly transparent click-through rendering.")
        pro_desc.setWordWrap(True)
        pro_desc.setFont(QFont("Segoe UI", 9))
        pro_desc.setStyleSheet("color: #a6adc8; border: none;")
        pro_layout.addWidget(pro_desc)

        # Active telemetry state info
        self.osd_status_card = QFrame()
        self.osd_status_card.setStyleSheet("QFrame { background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 6px; }")
        stat_card_lay = QVBoxLayout(self.osd_status_card)
        self.lbl_osd_state = QLabel("OSD State: Inactive")
        self.lbl_osd_state.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.lbl_osd_state.setStyleSheet("color: #f38ba8; border: none;")
        stat_card_lay.addWidget(self.lbl_osd_state)
        pro_layout.addWidget(self.osd_status_card)

        # Toggle Button
        self.btn_toggle_osd = QPushButton("Turn On OSD Overlay")
        self.btn_toggle_osd.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_toggle_osd.setStyleSheet("""
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
        self.btn_toggle_osd.clicked.connect(self.toggle_performance_osd)
        pro_layout.addWidget(self.btn_toggle_osd)

        self.osd_console = QTextEdit()
        self.osd_console.setReadOnly(True)
        self.osd_console.setFont(QFont("Consolas", 8))
        self.osd_console.setStyleSheet("""
            QTextEdit {
                background-color: #11111b;
                border: 1px solid #313244;
                color: #fab387;
                border-radius: 6px;
            }
        """)
        pro_layout.addWidget(self.osd_console)

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

        lock_desc = QLabel("Get Steam Pro version to unlock the advanced real-time Hardware OSD Overlay and monitor system performance while in-game.")
        lock_desc.setWordWrap(True)
        lock_desc.setFont(QFont("Segoe UI", 8))
        lock_desc.setStyleSheet("color: #a6adc8; border: none;")
        lock_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_desc)

        self.right_master_layout.addWidget(self.lock_overlay)

        master_layout.addWidget(self.right_pane, 2)

        # Scan active windows on load
        self.scan_running_windows()

        # Sync visual locking state
        self.refresh_ui()

    def scan_running_windows(self):
        self.windows_list.clear()
        self.btn_scan.setEnabled(False)
        self.log_console.append("[Manager] Polling active window tree...")

        self.scan_thread = WindowManagerThread()
        self.scan_thread.status_msg.connect(lambda txt: self.log_console.append(f"[Scan] {txt}"))
        self.scan_thread.windows_scanned.connect(self.on_windows_scanned)
        self.scan_thread.start()

    def on_windows_scanned(self, windows):
        self.btn_scan.setEnabled(True)
        self.scan_thread = None

        if not windows:
            self.log_console.append("[Manager] No visible windows found.")
            return

        for w in windows:
            display_text = f"[{w['hwnd']}] {w['title']}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, w["hwnd"])
            item.setData(Qt.ItemDataRole.UserRole + 1, w["title"])
            self.windows_list.addItem(item)

    def on_selection_changed(self):
        has_sel = len(self.windows_list.selectedItems()) > 0
        self.btn_pin.setEnabled(has_sel)
        self.btn_unpin.setEnabled(has_sel)
        self.opacity_frame.setEnabled(has_sel)
        if not has_sel:
            self.slider_opacity.setValue(100)
            self.lbl_opacity_val.setText("100%")

    def pin_selected_window(self):
        items = self.windows_list.selectedItems()
        if items:
            hwnd = items[0].data(Qt.ItemDataRole.UserRole)
            title = items[0].data(Qt.ItemDataRole.UserRole + 1)
            success = WindowManagerThread.set_always_on_top(hwnd, True)
            if success:
                self.log_console.append(f"[Manager] Pinned window on top: '{title}' (ID: {hwnd})")
            else:
                self.log_console.append(f"[Manager] Failed to pin window: '{title}'")

    def unpin_selected_window(self):
        items = self.windows_list.selectedItems()
        if items:
            hwnd = items[0].data(Qt.ItemDataRole.UserRole)
            title = items[0].data(Qt.ItemDataRole.UserRole + 1)
            success = WindowManagerThread.set_always_on_top(hwnd, False)
            if success:
                self.log_console.append(f"[Manager] Unpinned window: '{title}' (ID: {hwnd})")

    def change_window_opacity(self, value):
        self.lbl_opacity_val.setText(f"{value}%")
        items = self.windows_list.selectedItems()
        if items:
            hwnd = items[0].data(Qt.ItemDataRole.UserRole)
            WindowManagerThread.set_window_transparency(hwnd, value)

    def toggle_performance_osd(self):
        if self.osd_thread and self.osd_thread.isRunning():
            self.btn_toggle_osd.setText("Turning off OSD...")
            self.osd_thread.stop()
        else:
            self.btn_toggle_osd.setText("Turn Off OSD Overlay")
            self.lbl_osd_state.setText("OSD State: Active")
            self.lbl_osd_state.setStyleSheet("color: #a6e3a1; border: none;")
            self.osd_console.append("[OSD] Launching hardware telemetry monitor...")

            # Spawn floating transparent overlay widget
            self.osd_widget = OSDOverlayWidget()
            # Position centered top of screen natively
            self.osd_widget.move(100, 100)
            self.osd_widget.show()

            self.osd_thread = OSDOverlayThread()
            self.osd_thread.telemetry_changed.connect(self.osd_widget.update_telemetry)
            self.osd_thread.telemetry_changed.connect(self.log_osd_metrics)
            self.osd_thread.unauthorized.connect(self.on_osd_unauthorized)
            self.osd_thread.finished.connect(self.on_osd_terminated)
            self.osd_thread.start()

    def log_osd_metrics(self, m: dict):
        self.osd_console.append(f"[OSD] Live FPS: {m['fps']} | CPU: {m['cpu_temp']}°C | GPU: {m['gpu_temp']}°C")

    def on_osd_unauthorized(self):
        self.osd_console.append("⚠️ Pro Licensing Validation Failed! Overlay locked.")
        self.lbl_osd_state.setText("OSD State: Unauthorized")
        self.lbl_osd_state.setStyleSheet("color: #f38ba8; border: none;")
        self.btn_toggle_osd.setText("Turn On OSD Overlay")
        if self.osd_widget:
            self.osd_widget.close()
            self.osd_widget = None

    def on_osd_terminated(self):
        self.btn_toggle_osd.setText("Turn On OSD Overlay")
        self.lbl_osd_state.setText("OSD State: Inactive")
        self.lbl_osd_state.setStyleSheet("color: #f38ba8; border: none;")
        self.osd_console.append("[OSD] Hardware monitor stopped.")
        self.osd_thread = None
        if self.osd_widget:
            self.osd_widget.close()
            self.osd_widget = None

    def refresh_ui(self):
        if config.IS_PRO_VERSION:
            self.lock_overlay.hide()
            self.pro_control_widget.show()
        else:
            if self.osd_thread and self.osd_thread.isRunning():
                self.osd_thread.stop()
            self.pro_control_widget.hide()
            self.lock_overlay.show()

    def stop_all_workers(self):
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait()
        if self.osd_thread and self.osd_thread.isRunning():
            self.osd_thread.stop()
            self.osd_thread.wait()
        if self.osd_widget:
            self.osd_widget.close()
            self.osd_widget = None
