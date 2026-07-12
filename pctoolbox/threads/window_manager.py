import sys
import time
import ctypes
from PyQt6.QtCore import QThread, pyqtSignal

class WindowManagerThread(QThread):
    """
    Background worker for discovering and manipulating operating system window configurations.
    Fulfills standard window listing, pinning always-on-top, and alpha transparency overrides.
    Uses defensive ctypes Windows API structures, with clean fallbacks for non-Windows environments.
    """
    windows_scanned = pyqtSignal(list) # List of dict: {"hwnd": int/id, "title": str}
    status_msg = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        self.status_msg.emit("Starting desktop window hierarchy scan...")
        time.sleep(0.3)

        is_windows = sys.platform.startswith("win")
        found_windows = []

        if is_windows:
            try:
                # Setup Windows API callbacks and ctypes bindings
                EnumWindows = ctypes.windll.user32.EnumWindows
                EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
                GetWindowText = ctypes.windll.user32.GetWindowTextW
                GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
                IsWindowVisible = ctypes.windll.user32.IsWindowVisible

                def foreach_window(hwnd, lParam):
                    if not self._is_running:
                        return False

                    if IsWindowVisible(hwnd):
                        length = GetWindowTextLength(hwnd)
                        if length > 0:
                            buff = ctypes.create_unicode_buffer(length + 1)
                            GetWindowText(hwnd, buff, length + 1)
                            title = buff.value
                            # Filter out minor helper windows, background toolbars, and empty titles
                            if title and title not in ["Program Manager", "Start", "Microsoft Text Input Application"]:
                                found_windows.append({"hwnd": hwnd, "title": title})
                    return True

                EnumWindows(EnumWindowsProc(foreach_window), 0)
            except Exception as ctypes_err:
                self.status_msg.emit(f"Ctypes EnumWindows failure: {str(ctypes_err)}")
        else:
            # High-fidelity mock list representing active desktop panels in Unix/testing mode
            self.status_msg.emit("[Cross-Platform Mock] Simulating active system windows list.")
            found_windows = [
                {"hwnd": 102432, "title": "Counter-Strike 2 (DirectX 12)"},
                {"hwnd": 209541, "title": "Steam Client Dashboard"},
                {"hwnd": 302144, "title": "Mozilla Firefox - Epic Settings"},
                {"hwnd": 419202, "title": "Discord App - Gaming Lounge"}
            ]

        self.status_msg.emit(f"Desktop scan completed. Found {len(found_windows)} active windows.")
        self.windows_scanned.emit(found_windows)

    @staticmethod
    def set_always_on_top(hwnd: int, enable: bool) -> bool:
        """
        NATIVELY Pins or unpins a window always-on-top on Windows via SetWindowPos,
        adhering to SWP_NOMOVE (0x0002) and SWP_NOSIZE (0x0001) flags.
        """
        is_windows = sys.platform.startswith("win")
        if is_windows:
            try:
                # HWND_TOPMOST = -1, HWND_NOTOPMOST = -2
                # SWP_NOSIZE = 0x0001, SWP_NOMOVE = 0x0002
                hwnd_insert_after = -1 if enable else -2
                flags = 0x0001 | 0x0002
                # Call SetWindowPos natively to force window on top of game sessions
                ctypes.windll.user32.SetWindowPos(hwnd, hwnd_insert_after, 0, 0, 0, 0, flags)
                return True
            except Exception:
                return False
        return True # Simulate success on non-Windows

    @staticmethod
    def set_window_transparency(hwnd: int, opacity_percentage: int) -> bool:
        """
        Sets opacity (alpha) of target window from 0 to 100%.
        """
        is_windows = sys.platform.startswith("win")
        if is_windows:
            try:
                # GWL_EXSTYLE = -20
                # WS_EX_LAYERED = 0x00080000
                # LWA_ALPHA = 0x00000002
                GetWindowLong = ctypes.windll.user32.GetWindowLongW
                SetWindowLong = ctypes.windll.user32.SetWindowLongW
                SetLayeredWindowAttributes = ctypes.windll.user32.SetLayeredWindowAttributes

                # Retrieve current style
                style = GetWindowLong(hwnd, -20)
                # Check layered flag
                if not (style & 0x00080000):
                    SetWindowLong(hwnd, -20, style | 0x00080000)

                # Convert percent (0-100) to actual byte alpha (0-255)
                alpha_byte = int((opacity_percentage / 100.0) * 255)
                SetLayeredWindowAttributes(hwnd, 0, alpha_byte, 0x00000002)
                return True
            except Exception:
                return False
        return True
