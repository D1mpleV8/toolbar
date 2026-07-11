import time
from PyQt6.QtCore import QThread, pyqtSignal
from pctoolbox import config

class MacroThread(QThread):
    """
    Background worker for executing Computer Vision Macros and monitoring hotkeys.
    This advanced feature checks config.IS_PRO_VERSION before executing.
    Runs in an isolated thread to monitor global / local simulated hotkeys (like F9)
    and perform computer-vision/pixel simulation tasks safely without blocking UI.
    """
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    match_found = pyqtSignal(str) # Name of CV match found
    finished_summary = pyqtSignal(str)
    unauthorized = pyqtSignal()

    def __init__(self, template_name: str = "health_bar"):
        super().__init__()
        self.template_name = template_name
        self._is_running = True

    def stop(self):
        """Allows safely stopping/cancelling the macro / CV detection task."""
        self._is_running = False

    def run(self):
        # Strict "Feature Flag" Check
        if not config.IS_PRO_VERSION:
            self.unauthorized.emit()
            self.status.emit("Feature Locked: Pro Version Required.")
            return

        self.status.emit("Computer Vision engine initialized. Listening for [F9] or Start trigger...")
        self.progress.emit(10)
        time.sleep(1.0)

        # Simulation of CV scanning and hotkey macro execution loop
        scan_cycles = 5
        for i in range(1, scan_cycles + 1):
            if not self._is_running:
                break

            self.status.emit(f"Scanning frame {i} for template matching: '{self.template_name}'...")
            self.progress.emit(10 + int((i / scan_cycles) * 80))

            # Simulate a 1-second scanning gap
            time.sleep(1.0)

            # Let's simulate finding a match on cycle 3!
            if i == 3:
                self.match_found.emit(f"Found match: '{self.template_name}' at coordinate (312, 450) with 98.4% confidence.")
                self.status.emit(f"[CV Match] Found '{self.template_name}'! Executing automated mouse & key sequence...")
                time.sleep(1.5)  # Simulate automation duration

        if self._is_running:
            self.status.emit("Computer Vision Macro completed!")
            self.progress.emit(100)
            self.finished_summary.emit(
                f"Successfully completed macro sequence for target '{self.template_name}' with high confidence."
            )
        else:
            self.status.emit("Macro execution cancelled.")
            self.progress.emit(0)
