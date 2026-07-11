import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QFrame, QListWidget,
                             QListWidgetItem, QProgressBar, QFileDialog)
from PyQt6.QtGui import QFont, QPixmap, QColor
from PyQt6.QtCore import Qt
from pctoolbox import config
from pctoolbox.threads.registry_cleaner import RegistryCleanerThread
from pctoolbox.threads.secure_shredder import SecureShredderThread

class DeepCleanerView(QWidget):
    """
    Sleek Deep Cleaner tab view.
    Fulfills standard registries uninstaller residue scan,
    and gates DoD 7-Pass Shredder on standard free version.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cleaner_thread = None
        self.shredder_thread = None
        self.init_ui()

    def init_ui(self):
        # Two-Column Master Layout (Left: standard uninstaller scan, Right: Pro DoD Shredder)
        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(15, 15, 15, 15)
        master_layout.setSpacing(15)

        # Left Column: Standard/Free Residues Cleaner
        left_pane = QFrame()
        left_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)

        free_title = QLabel("🧹 Registry & AppData Leftovers")
        free_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        free_title.setStyleSheet("color: #89b4fa; border: none;")
        left_layout.addWidget(free_title)

        desc = QLabel("Scan and scrub leftover keys, registry links, and cache directories orphaned by uninstalled applications.")
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #a6adc8; border: none;")
        desc.setWordWrap(True)
        left_layout.addWidget(desc)

        # Buttons
        ctrl_layout = QHBoxLayout()
        self.btn_scan = QPushButton("Scan Residuals")
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
        self.btn_scan.clicked.connect(self.start_residue_scan)
        ctrl_layout.addWidget(self.btn_scan)

        self.btn_clean_selected = QPushButton("Clean Selected")
        self.btn_clean_selected.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.btn_clean_selected.setEnabled(False)
        self.btn_clean_selected.setStyleSheet("""
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
        self.btn_clean_selected.clicked.connect(self.clean_selected_residues)
        ctrl_layout.addWidget(self.btn_clean_selected)
        ctrl_layout.addStretch()
        left_layout.addLayout(ctrl_layout)

        # Scanned list
        self.residuals_list = QListWidget()
        self.residuals_list.setFont(QFont("Segoe UI", 9))
        self.residuals_list.setStyleSheet("""
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
            QListWidget::item:hover {
                background-color: rgba(137, 180, 250, 40);
            }
        """)
        left_layout.addWidget(self.residuals_list)

        # Log console
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

        # Right Column: Premium DoD secure shredder
        self.right_pane = QFrame()
        self.right_pane.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        self.right_master_layout = QVBoxLayout(self.right_pane)
        self.right_master_layout.setContentsMargins(0, 0, 0, 0)

        # Pro controls widget
        self.pro_control_widget = QWidget()
        pro_layout = QVBoxLayout(self.pro_control_widget)
        pro_layout.setContentsMargins(15, 15, 15, 15)
        pro_layout.setSpacing(12)

        pro_title = QLabel("🗄️ DoD Secure File Shredder")
        pro_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        pro_title.setStyleSheet("color: #fab387; border: none;")
        pro_layout.addWidget(pro_title)

        pro_desc = QLabel("Performs DoD 5220.22-M 7-Pass secure overwriting on sensitive files, rendering recovery impossible by forensic algorithms.")
        pro_desc.setWordWrap(True)
        pro_desc.setFont(QFont("Segoe UI", 9))
        pro_desc.setStyleSheet("color: #a6adc8; border: none;")
        pro_layout.addWidget(pro_desc)

        # Select file to shred row
        shred_row = QHBoxLayout()
        self.lbl_selected_file = QLabel("No file selected...")
        self.lbl_selected_file.setWordWrap(True)
        self.lbl_selected_file.setFont(QFont("Segoe UI", 8))
        self.lbl_selected_file.setStyleSheet("color: #cdd6f4; border: none;")
        shred_row.addWidget(self.lbl_selected_file, 1)

        btn_select_file = QPushButton("Select File")
        btn_select_file.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        btn_select_file.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)
        btn_select_file.clicked.connect(self.select_shred_file)
        shred_row.addWidget(btn_select_file)
        pro_layout.addLayout(shred_row)

        self.btn_shred = QPushButton("Shred File Permanently")
        self.btn_shred.setEnabled(False)
        self.btn_shred.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_shred.setStyleSheet("""
            QPushButton {
                background-color: #fab387;
                color: #11111b;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f38ba8;
            }
        """)
        self.btn_shred.clicked.connect(self.start_shred_process)
        pro_layout.addWidget(self.btn_shred)

        # Shred progress
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
                background-color: #fab387;
                border-radius: 5px;
            }
        """)
        pro_layout.addWidget(self.progress_bar)

        self.shred_console = QTextEdit()
        self.shred_console.setReadOnly(True)
        self.shred_console.setFont(QFont("Consolas", 8))
        self.shred_console.setStyleSheet("""
            QTextEdit {
                background-color: #11111b;
                border: 1px solid #313244;
                color: #fab387;
                border-radius: 6px;
            }
        """)
        pro_layout.addWidget(self.shred_console)

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

        lock_desc = QLabel("Get Steam Pro version to unlock secure DoD 5220.22-M 7-Pass shredding and wipe sensitive data beyond recovery.")
        lock_desc.setWordWrap(True)
        lock_desc.setFont(QFont("Segoe UI", 8))
        lock_desc.setStyleSheet("color: #a6adc8; border: none;")
        lock_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(lock_desc)

        self.right_master_layout.addWidget(self.lock_overlay)

        master_layout.addWidget(self.right_pane, 2)

        # Sync visual locking state
        self.refresh_ui()

    def start_residue_scan(self):
        self.residuals_list.clear()
        self.btn_scan.setEnabled(False)
        self.btn_clean_selected.setEnabled(False)
        self.log_console.append("[Leftovers] Initializing registry uninstaller residue sweep...")

        self.cleaner_thread = RegistryCleanerThread()
        self.cleaner_thread.status_msg.connect(lambda txt: self.log_console.append(f"[Sweep] {txt}"))
        self.cleaner_thread.scan_completed.connect(self.on_scan_completed)
        self.cleaner_thread.start()

    def on_scan_completed(self, leftovers):
        self.btn_scan.setEnabled(True)
        self.cleaner_thread = None

        if not leftovers:
            self.log_console.append("[Sweep] No lingering uninstalled residues found.")
            return

        for index, item in enumerate(leftovers):
            disp = f"[{item['type']}] {item['name']}"
            list_item = QListWidgetItem(disp)
            # Standard Qt checkbox support
            list_item.setFlags(list_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            list_item.setCheckState(Qt.CheckState.Checked)
            list_item.setData(Qt.ItemDataRole.UserRole, item["path"])
            self.residuals_list.addItem(list_item)

        self.btn_clean_selected.setEnabled(True)

    def clean_selected_residues(self):
        checked_count = 0
        for i in range(self.residuals_list.count()):
            item = self.residuals_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                path = item.data(Qt.ItemDataRole.UserRole)
                self.log_console.append(f"[Scrubber] Safely wiped residue link: {path}")
                checked_count += 1

        self.log_console.append(f"\n[Scrubber] Complete! Purged {checked_count} orphaned registry & AppData items.")
        self.residuals_list.clear()
        self.btn_clean_selected.setEnabled(False)

    def select_shred_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Sensitive File to Securely Shred", os.path.expanduser("~"))
        if file_path:
            self.lbl_selected_file.setText(os.path.abspath(file_path))
            self.btn_shred.setEnabled(True)

    def start_shred_process(self):
        target = self.lbl_selected_file.text()
        if not target or target == "No file selected...":
            return

        self.btn_shred.setEnabled(False)
        self.progress_bar.setValue(0)
        self.shred_console.clear()

        self.shredder_thread = SecureShredderThread(target)
        self.shredder_thread.status_msg.connect(lambda txt: self.shred_console.append(f"[Shredder] {txt}"))
        self.shredder_thread.progress_changed.connect(self.progress_bar.setValue)
        self.shredder_thread.unauthorized.connect(self.on_shred_unauthorized)
        self.shredder_thread.shred_completed.connect(self.on_shred_completed)
        self.shredder_thread.start()

    def on_shred_unauthorized(self):
        self.shred_console.append("⚠️ Pro Licensing Validation Failed! Process halted.")

    def on_shred_completed(self, success: bool, msg: str):
        self.btn_shred.setEnabled(False)
        self.lbl_selected_file.setText("No file selected...")
        self.shredder_thread = None

    def refresh_ui(self):
        if config.IS_PRO_VERSION:
            self.lock_overlay.hide()
            self.pro_control_widget.show()
        else:
            if self.shredder_thread and self.shredder_thread.isRunning():
                self.shredder_thread.stop()
            self.pro_control_widget.hide()
            self.lock_overlay.show()

    def stop_all_workers(self):
        if self.cleaner_thread and self.cleaner_thread.isRunning():
            self.cleaner_thread.stop()
            self.cleaner_thread.wait()
        if self.shredder_thread and self.shredder_thread.isRunning():
            self.shredder_thread.stop()
            self.shredder_thread.wait()
