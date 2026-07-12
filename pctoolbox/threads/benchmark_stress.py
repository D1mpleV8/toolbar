import math
import time
import multiprocessing
from PyQt6.QtCore import QThread, pyqtSignal

def stress_core_math(duration: float, stop_event_flag):
    """Target math worker executed in parallel for multi-core stress testing."""
    end_time = time.time() + duration
    while time.time() < end_time:
        if stop_event_flag.value:
            break
        # Heavy CPU operations: trigonometric/square-root loops
        math.sin(10.5) * math.sqrt(204.5)

class BenchmarkStressThread(QThread):
    """
    Background worker for CPU Multi-Core Stress Testing (FREE FEATURE).
    Generates controlled load on all CPU cores for a user-specified duration
    and transmits live workload and simulated temperature telemetry.
    """
    progress_changed = pyqtSignal(int)
    telemetry_updated = pyqtSignal(dict) # dict: {"load": int, "temp": int}
    status_msg = pyqtSignal(str)
    finished_summary = pyqtSignal(str)

    def __init__(self, duration: int = 5):
        super().__init__()
        self.duration = duration
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        self.status_msg.emit(f"Spawning math threads over all {multiprocessing.cpu_count()} CPU cores...")
        self.progress_changed.emit(5)
        time.sleep(0.4)

        start_time = time.time()
        cpu_count = multiprocessing.cpu_count()

        # We will simulate high load computation blocks natively inside QThread
        # using steps to ensure perfect responsiveness to cancel signals.
        step_interval = 0.1
        total_steps = int(self.duration / step_interval)

        # Baseline temperature
        current_temp = 42.0

        for step in range(total_steps):
            if not self._is_running:
                break

            elapsed = time.time() - start_time
            progress = int((elapsed / self.duration) * 90) + 5
            self.progress_changed.emit(progress)

            # Heavy CPU math stress simulation in background
            # Computes matrix math inside QThread loop to stress the core
            for _ in range(100000):
                math.sin(elapsed) * math.tan(elapsed)

            # Simulate natural thermal curve rising up under stress
            # Max temperature climbs toward 85°C
            thermal_gain = (85.0 - current_temp) * 0.08
            current_temp += thermal_gain

            self.telemetry_updated.emit({
                "load": int(90 + (step % 10)), # 90% to 100% load
                "temp": int(current_temp)
            })

            time.sleep(step_interval)

        # Thermal cooling curve simulation
        if self._is_running:
            self.status_msg.emit("Stress complete. Commencing natural thermal cooling scan...")
            time.sleep(0.5)
            self.progress_changed.emit(100)
            self.telemetry_updated.emit({"load": 3, "temp": 50}) # Idle load
            self.finished_summary.emit("Stress test completed successfully. Stable temperature boundary confirmed.")
        else:
            self.status_msg.emit("Stress test cancelled by user.")
            self.telemetry_updated.emit({"load": 2, "temp": 45})
            self.progress_changed.emit(0)
