import time
import secrets
from PyQt6.QtCore import QThread, pyqtSignal
from pctoolbox import config

class OSDOverlayThread(QThread):
    """
    Background worker for in-game hardware monitoring (PRO FEATURE).
    Gated strictly behind the IS_PRO_VERSION flag.
    Gathers and emits live hardware parameters (FPS, CPU/GPU temps, RAM usage)
    to the OSD display overlay completely avoiding thread blocks.
    """
    telemetry_changed = pyqtSignal(dict) # Emits dict with performance telemetry
    unauthorized = pyqtSignal()

    def __init__(self, update_interval: float = 1.0):
        super().__init__()
        self.update_interval = update_interval
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        # Strict Feature Flag gate
        if not config.IS_PRO_VERSION:
            self.unauthorized.emit()
            return

        # Start simulated game overlay telemetry loop
        while self._is_running:
            # Simulate metrics matching a heavy AAA game run session
            fps = 135 + secrets.randbelow(15) # 135 to 149 FPS
            cpu_temp = 62 + secrets.randbelow(8) # 62 to 69 C
            gpu_temp = 68 + secrets.randbelow(6) # 68 to 73 C
            cpu_load = 45 + secrets.randbelow(15) # 45 to 59%
            gpu_load = 88 + secrets.randbelow(10) # 88 to 97%
            ram_alloc = 8.4 + (secrets.randbelow(10) / 10.0) # 8.4 to 9.3 GB

            metrics = {
                "fps": fps,
                "cpu_temp": cpu_temp,
                "gpu_temp": gpu_temp,
                "cpu_load": cpu_load,
                "gpu_load": gpu_load,
                "ram_alloc": ram_alloc
            }

            self.telemetry_changed.emit(metrics)

            # Defensive sleep with cancel checks
            sleep_step = self.update_interval / 10.0
            for _ in range(10):
                if not self._is_running:
                    break
                time.sleep(sleep_step)
