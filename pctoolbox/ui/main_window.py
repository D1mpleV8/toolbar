import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QPushButton, QLabel, QFrame, QSystemTrayIcon, QMenu, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction, QKeySequence, QShortcut, QColor
from PyQt6.QtCore import Qt, QPoint
from pctoolbox import config
from pctoolbox.ui.dashboard import DashboardView
from pctoolbox.ui.cleaner_view import CleanerView
from pctoolbox.ui.optimizer_view import OptimizerView
from pctoolbox.ui.macro_view import MacroView
from pctoolbox.ui.network_view import NetworkView
from pctoolbox.ui.organizer_view import OrganizerView
from pctoolbox.ui.deep_cleaner_view import DeepCleanerView
from pctoolbox.ui.window_manager_view import WindowManagerView
from pctoolbox.ui.privacy_shield_view import PrivacyShieldView
from pctoolbox.ui.performance_benchmark_view import PerformanceBenchmarkView
from pctoolbox.ui.profile_sync_view import ProfileSyncView
from pctoolbox.ui.quick_launcher import QuickLauncher

class SidebarNavButton(QPushButton):
    """
    Sleek, glowing left navigation bar button.
    Upon hover or active status, shows a glowing Cyber-Blue (#00F0FF) accent bar
    on the left edge, matching modern high-fidelity Steam designs.
    """
    def __init__(self, text, icon_str=None, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.setCheckable(True)
        self.setMinimumHeight(44)

        # Style standard, hover and checked states
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a6adc8;
                border: none;
                text-align: left;
                padding-left: 20px;
                border-left: 4px solid transparent;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: rgba(0, 240, 255, 15);
                border-left: 4px solid rgba(0, 240, 255, 100);
            }
            QPushButton:checked {
                color: #00F0FF;
                font-weight: bold;
                background-color: rgba(0, 240, 255, 30);
                border-left: 4px solid #00F0FF; /* Cyber-Blue Accent Line */
            }
        """)

class MainWindow(QMainWindow):
    """
    Sleek, feature-rich main window for the Steam PC Toolbox application.
    Natively implements a FRAMELESS premium custom shadow interface.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steam PC Toolbox v1.0.0 Pro-Edition Suite")
        self.resize(1000, 680)
        self._is_closing_for_real = False  # Track if we are fully quitting or just closing window

        # 1. ENFORCE FRAMELESS WINDOW DESIGN
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Apply Window Shadow effect dynamically to create breathtaking depth
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setYOffset(0)
        self.shadow_effect.setColor(QColor("rgba(0, 240, 255, 40)")) # Glow shadow

        # Custom dragging helper states
        self.drag_position = QPoint()

        # Set Window Icon
        app_icon_path = config.get_asset_path("app_icon.png")
        icon = QIcon(app_icon_path)
        if not icon.isNull():
            self.setWindowIcon(icon)

        # Master Outer Frame Container
        self.central_frame = QFrame()
        self.central_frame.setObjectName("CentralFrame")
        self.central_frame.setStyleSheet("""
            QFrame#CentralFrame {
                background-color: #0B0E14; /* Deep Obsidian */
                border: 1px solid #2A3241;
                border-radius: 12px;
            }
            QTabWidget::pane {
                border: none;
                background-color: #0B0E14;
            }
            QTabWidget QTabBar {
                height: 0px; /* Hide default tab bar headers to use our sleek left sidebar instead! */
            }
        """)
        self.central_frame.setGraphicsEffect(self.shadow_effect)
        self.setCentralWidget(self.central_frame)

        main_outer_layout = QVBoxLayout(self.central_frame)
        main_outer_layout.setContentsMargins(0, 0, 0, 0)
        main_outer_layout.setSpacing(0)

        # 2. Sleek top navigation bar
        self.top_title_bar = QFrame()
        self.top_title_bar.setFixedHeight(50)
        self.top_title_bar.setStyleSheet("""
            QFrame {
                background-color: #0F141C;
                border: none;
                border-bottom: 1px solid #1E2530;
                border-top-left-radius: 11px;
                border-top-right-radius: 11px;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
                letter-spacing: 1.5px;
            }
        """)

        top_bar_layout = QHBoxLayout(self.top_title_bar)
        top_bar_layout.setContentsMargins(15, 0, 15, 0)

        # Title/Logo
        lbl_app_logo = QLabel("🛡️ STEAM PC TOOLBOX")
        lbl_app_logo.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_app_logo.setStyleSheet("color: #00F0FF;")
        top_bar_layout.addWidget(lbl_app_logo)
        top_bar_layout.addStretch()

        # Premium Toggle state
        self.license_btn = QPushButton()
        self.license_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.license_btn.clicked.connect(self.toggle_license_state)
        top_bar_layout.addWidget(self.license_btn)

        # Separator gap
        top_bar_layout.addSpacing(10)

        # Custom Minimize / Close Buttons
        btn_min = QPushButton("–")
        btn_min.setFont(QFont("Consolas", 12))
        btn_min.setFixedSize(28, 28)
        btn_min.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a6adc8;
                border: 1px solid #2A3241;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(0, 240, 255, 30);
                color: #00F0FF;
            }
        """)
        btn_min.clicked.connect(self.showMinimized)
        top_bar_layout.addWidget(btn_min)

        btn_close = QPushButton("×")
        btn_close.setFont(QFont("Consolas", 14))
        btn_close.setFixedSize(28, 28)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a6adc8;
                border: 1px solid #2A3241;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 60, 30);
                color: #FF003C;
                border: 1px solid #FF003C;
            }
        """)
        btn_close.clicked.connect(self.close)
        top_bar_layout.addWidget(btn_close)

        main_outer_layout.addWidget(self.top_title_bar)

        # Body Layout (Split Left Sidebar & Central tab panel)
        body_container = QWidget()
        body_container.setStyleSheet("background: transparent;")
        body_layout = QHBoxLayout(body_container)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # 3. Clean Left Sidebar for Navigation
        self.left_sidebar = QFrame()
        self.left_sidebar.setFixedWidth(220)
        self.left_sidebar.setStyleSheet("""
            QFrame {
                background-color: #0F141C;
                border: none;
                border-right: 1px solid #1E2530;
                border-bottom-left-radius: 11px;
            }
        """)
        sidebar_layout = QVBoxLayout(self.left_sidebar)
        sidebar_layout.setContentsMargins(0, 15, 0, 15)
        sidebar_layout.setSpacing(5)

        # Nav Buttons list
        self.nav_buttons = []
        self.nav_tabs_map = [] # list of tuples: (button, tab_widget)

        # Tabs Widget definition
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("background: transparent;")

        # Instantiate premium child views
        self.view_dashboard = DashboardView()
        self.view_cleaner = CleanerView()
        self.view_deep_cleaner = DeepCleanerView()
        self.view_window_manager = WindowManagerView()
        self.view_performance = PerformanceBenchmarkView()
        self.view_privacy_shield = PrivacyShieldView()
        self.view_profile_sync = ProfileSyncView()
        self.view_optimizer = OptimizerView()
        self.view_macro = MacroView()
        self.view_network = NetworkView()
        self.view_organizer = OrganizerView()

        # Tab specifications tuple: (Sleek Icon/Title, Widget)
        tab_list = [
            ("📊 Dashboard", self.view_dashboard),
            ("🧹 Quick Cleaner", self.view_cleaner),
            ("⚙️ Deep Cleaner", self.view_deep_cleaner),
            ("🖼️ Window Manager", self.view_window_manager),
            ("🔥 Performance OSD", self.view_performance),
            ("🛡️ Privacy Shield", self.view_privacy_shield),
            ("🔐 Profile & Sync", self.view_profile_sync),
            ("🚀 Game Optimizer", self.view_optimizer),
            ("🤖 CV Auto Macro", self.view_macro),
            ("🌐 Network Manager", self.view_network),
            ("📁 Smart Organizer", self.view_organizer)
        ]

        for index, (title, widget) in enumerate(tab_list):
            self.tabs.addTab(widget, title)

            # Create sleek nav button
            btn = SidebarNavButton(title)
            btn.clicked.connect(lambda checked, idx=index: self.transition_tab(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            self.nav_tabs_map.append((btn, widget))

        # Check/select first dashboard button initially
        self.nav_buttons[0].setChecked(True)

        sidebar_layout.addStretch()
        body_layout.addWidget(self.left_sidebar)
        body_layout.addWidget(self.tabs, 1)

        main_outer_layout.addWidget(body_container)

        # Setup F9 Hotkey/Shortcut
        self.shortcut_f9 = QShortcut(QKeySequence("F9"), self)
        self.shortcut_f9.activated.connect(self.view_macro.toggle_macro_state_f9)

        # Instantiate Floating Glassmorphic Quick Launcher
        self.quick_launcher = QuickLauncher()

        # Setup Alt+Space Hotkey to toggle Quick Launcher visibility
        self.shortcut_alt_space = QShortcut(QKeySequence("Alt+Space"), self)
        self.shortcut_alt_space.activated.connect(self.toggle_quick_launcher)

        # Initialize License State & UI texts
        self.update_license_ui_elements()

        # Initialize System Tray
        self.setup_system_tray()

    def transition_tab(self, index):
        """Swaps active QTabWidget index and toggles checked states on sidebar button groups."""
        self.tabs.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def toggle_quick_launcher(self):
        """Shows or hides the floating launcher window."""
        if self.quick_launcher.isVisible():
            self.quick_launcher.hide()
        else:
            main_geo = self.geometry()
            launcher_width = self.quick_launcher.width()
            launcher_height = self.quick_launcher.height()

            x = main_geo.x() + (main_geo.width() - launcher_width) // 2
            y = main_geo.y() + (main_geo.height() - launcher_height) // 2

            self.quick_launcher.move(x, y)
            self.quick_launcher.show()
            self.quick_launcher.activateWindow()
            self.quick_launcher.txt_search.setFocus()
            self.quick_launcher.txt_search.selectAll()

    def toggle_license_state(self):
        """Simulate Steamworks API toggle of IS_PRO_VERSION"""
        new_state = not config.IS_PRO_VERSION
        config.set_pro_version(new_state)
        self.update_license_ui_elements()

        # Trigger tray message if running
        if self.tray_icon.isVisible():
            status_str = "PRO Edition Activated!" if new_state else "Free Edition Active"
            self.tray_icon.showMessage(
                "PC Toolbox License Update",
                f"License switched to {status_str}.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )

    def update_license_ui_elements(self):
        """Updates main window and all child widgets when license status updates."""
        if config.IS_PRO_VERSION:
            self.license_btn.setText("PRO MODE ENABLED")
            self.license_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 240, 255, 30);
                    color: #00F0FF;
                    border: 1px solid #00F0FF;
                    border-radius: 4px;
                    padding: 5px 12px;
                }
                QPushButton:hover {
                    background-color: #00F0FF;
                    color: #11111b;
                }
            """)
        else:
            self.license_btn.setText("FREE MODE (Demo Toggle)")
            self.license_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 0, 60, 30);
                    color: #FF003C;
                    border: 1px solid #FF003C;
                    border-radius: 4px;
                    padding: 5px 12px;
                }
                QPushButton:hover {
                    background-color: #FF003C;
                    color: #ffffff;
                }
            """)

        # Propagate changes to child views
        self.view_dashboard.refresh_ui()
        self.view_optimizer.refresh_ui()
        self.view_macro.refresh_ui()
        self.view_network.refresh_ui()
        self.view_organizer.refresh_ui()
        self.view_deep_cleaner.refresh_ui()
        self.view_window_manager.refresh_ui()
        self.view_privacy_shield.refresh_ui()
        self.view_performance.refresh_ui()
        self.view_profile_sync.refresh_ui()

    def setup_system_tray(self):
        """Creates the native system tray integration to prevent Taskbar clutter."""
        self.tray_icon = QSystemTrayIcon(self)

        tray_icon_path = config.get_asset_path("tray_icon.png")
        icon = QIcon(tray_icon_path)
        if not icon.isNull():
            self.tray_icon.setIcon(icon)
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("system-run"))

        # Context Menu
        tray_menu = QMenu()

        restore_action = QAction("Restore / Open PC Toolbox", self)
        restore_action.triggered.connect(self.showNormal)
        tray_menu.addAction(restore_action)

        run_cleaner_action = QAction("Quick Clean Up", self)
        run_cleaner_action.triggered.connect(self.trigger_quick_clean)
        tray_menu.addAction(run_cleaner_action)

        tray_menu.addSeparator()

        exit_action = QAction("Exit App", self)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Handle Tray Clicks
        self.tray_icon.activated.connect(self.on_tray_activated)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger: # Single left-click
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.activateWindow()

    def trigger_quick_clean(self):
        self.showNormal()
        self.tabs.setCurrentIndex(1) # system cleaner index
        self.view_cleaner.start_cleanup()

    def quit_application(self):
        self._is_closing_for_real = True
        self.tray_icon.hide()
        self.close()

    # Frameless dragging native calculations
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicked inside our top title bar region
            if event.position().y() <= self.top_title_bar.height():
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if event.position().y() <= self.top_title_bar.height() + 20: # Allow slight drag offset
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()

    def closeEvent(self, event):
        """
        Intercept standard window Close button.
        Instead of terminating, minimize silently to system tray.
        """
        if self._is_closing_for_real:
            # Propagate termination to all threads safely before exiting
            if self.view_cleaner.clean_thread and self.view_cleaner.clean_thread.isRunning():
                self.view_cleaner.clean_thread.stop()
                self.view_cleaner.clean_thread.wait()
            if self.view_optimizer.opt_thread and self.view_optimizer.opt_thread.isRunning():
                self.view_optimizer.opt_thread.stop()
                self.view_optimizer.opt_thread.wait()
            if self.view_macro.macro_thread and self.view_macro.macro_thread.isRunning():
                self.view_macro.macro_thread.stop()
                self.view_macro.macro_thread.wait()

            # Stop network views and monitors
            self.view_network.stop_all_workers()

            # Stop Smart Organizer watcher
            self.view_organizer.stop_all_workers()

            # Stop Deep Cleaner threads
            self.view_deep_cleaner.stop_all_workers()

            # Stop Window Manager & OSD threads
            self.view_window_manager.stop_all_workers()

            # Stop Privacy Shield workers
            self.view_privacy_shield.stop_all_workers()

            # Stop Performance & Stress workers
            self.view_performance.stop_all_workers()

            # Stop Profile & Sync threads
            self.view_profile_sync.stop_all_workers()

            # Stop Quick Launcher threads
            if self.quick_launcher.search_thread and self.quick_launcher.search_thread.isRunning():
                self.quick_launcher.search_thread.disconnect()
                self.quick_launcher.search_thread.terminate()
            self.quick_launcher.close()

            event.accept()
        else:
            event.ignore()
            self.hide()
            if self.tray_icon.isVisible():
                self.tray_icon.showMessage(
                    "PC Toolbox",
                    "Application is running in silent background tray mode. Double-click tray icon to restore.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
