import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QPushButton, QLabel, QFrame, QSystemTrayIcon, QMenu)
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction, QKeySequence, QShortcut
from PyQt6.QtCore import Qt
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

class MainWindow(QMainWindow):
    """
    Sleek, feature-rich main window for the Steam PC Toolbox application.
    Integrates all standard/free and advanced views with full support for:
    - Production-ready non-hardcoded absolute asset paths (PyInstaller / sys._MEIPASS).
    - Modern Multi-Threading via isolated background worker threads.
    - Global/Local Hotkey Simulation (F9 key binding) to toggle macros.
    - Full System Tray integration (minimize to tray on close, run in background).
    - Alt+Space Floating Quick Launcher search integration.
    - Pro VS Free feature toggle simulation button.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steam PC Toolbox v1.0.0 Pro-Edition Suite")
        self.resize(920, 640)
        self._is_closing_for_real = False  # Track if we are fully quitting or just closing window

        # Set Window Icon
        app_icon_path = config.get_asset_path("app_icon.png")
        icon = QIcon(app_icon_path)
        if not icon.isNull():
            self.setWindowIcon(icon)

        # Apply Modern Dark Futuristic stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #11111b;
            }
            QTabWidget::pane {
                border: 1px solid #313244;
                background-color: #181825;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #1e1e2e;
                color: #a6adc8;
                border: 1px solid #313244;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 10px 18px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #181825;
                color: #cba6f7;
                border: 1px solid #cba6f7;
                border-bottom: none;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #313244;
                color: #ffffff;
            }
        """)

        # Main Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Header Row
        header_layout = QHBoxLayout()
        header_title = QLabel("STEAM PC TOOLBOX")
        header_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_title.setStyleSheet("color: #ffffff; letter-spacing: 1px;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        # License Toggler & Indicator
        self.license_btn = QPushButton()
        self.license_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.license_btn.clicked.connect(self.toggle_license_state)
        header_layout.addWidget(self.license_btn)

        main_layout.addLayout(header_layout)

        # Tab Views
        self.tabs = QTabWidget()

        # Instantiate views
        self.view_dashboard = DashboardView()
        self.view_cleaner = CleanerView()
        self.view_optimizer = OptimizerView()
        self.view_macro = MacroView()
        self.view_network = NetworkView()
        self.view_organizer = OrganizerView()
        self.view_deep_cleaner = DeepCleanerView()
        self.view_window_manager = WindowManagerView()
        self.view_privacy_shield = PrivacyShieldView()
        self.view_performance = PerformanceBenchmarkView()
        self.view_profile_sync = ProfileSyncView()

        # Add tabs
        self.tabs.addTab(self.view_dashboard, "Dashboard")
        self.tabs.addTab(self.view_cleaner, "System Cleaner")
        self.tabs.addTab(self.view_deep_cleaner, "Deep Cleaner")
        self.tabs.addTab(self.view_window_manager, "Window Manager")
        self.tabs.addTab(self.view_performance, "Performance & Stress")
        self.tabs.addTab(self.view_privacy_shield, "Privacy Shield")
        self.tabs.addTab(self.view_profile_sync, "Profile & Sync")
        self.tabs.addTab(self.view_optimizer, "Game Optimizer (Pro)")
        self.tabs.addTab(self.view_macro, "CV Automation (Pro)")
        self.tabs.addTab(self.view_network, "Network & Connectivity")
        self.tabs.addTab(self.view_organizer, "Smart Organizer")

        main_layout.addWidget(self.tabs)

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

        # Connect Dashboard buttons to their tab view transitions
        self.view_dashboard.btn_stress.clicked.connect(lambda: self.tabs.setCurrentWidget(self.view_performance))
        self.view_dashboard.btn_overlay.clicked.connect(lambda: self.tabs.setCurrentWidget(self.view_window_manager))

        # Initialize System Tray
        self.setup_system_tray()

    def toggle_quick_launcher(self):
        """Shows or hides the floating launcher window."""
        if self.quick_launcher.isVisible():
            self.quick_launcher.hide()
        else:
            # Centering the floating widget relative to the main window
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
            self.license_btn.setText("PRO MODE ENABLED (Demo Toggle)")
            self.license_btn.setStyleSheet("""
                QPushButton {
                    background-color: #a6e3a1;
                    color: #11111b;
                    border: 1px solid #a6e3a1;
                    border-radius: 4px;
                    padding: 5px 12px;
                }
                QPushButton:hover {
                    background-color: #11111b;
                    color: #a6e3a1;
                }
            """)
        else:
            self.license_btn.setText("FREE MODE (Demo Click to Upgrade)")
            self.license_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f38ba8;
                    color: #11111b;
                    border: 1px solid #f38ba8;
                    border-radius: 4px;
                    padding: 5px 12px;
                }
                QPushButton:hover {
                    background-color: #11111b;
                    color: #f38ba8;
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
            # Fallback
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
        self.tabs.setCurrentWidget(self.view_cleaner)
        self.view_cleaner.start_cleanup()

    def quit_application(self):
        self._is_closing_for_real = True
        self.tray_icon.hide()
        self.close()

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
