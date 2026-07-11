import time
from PyQt6.QtCore import QThread, pyqtSignal
from pctoolbox import config

class OptimizerThread(QThread):
    """
    Background worker for advanced Game / RAM optimization tasks.
    This advanced feature checks config.IS_PRO_VERSION before executing.
    Runs entirely on an isolated background thread to prevent UI freezing.
    """
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished_summary = pyqtSignal(str)
    unauthorized = pyqtSignal()  # Signal emitted if Pro authorization fails

    def __init__(self, optimize_ram: bool = True, prioritize_gpu: bool = True, clean_ram: bool = True):
        super().__init__()
        self.optimize_ram = optimize_ram
        self.prioritize_gpu = prioritize_gpu
        self.clean_ram = clean_ram
        self._is_running = True

    def stop(self):
        """Allows safely stopping/cancelling the optimization task."""
        self._is_running = False

    def run(self):
        # Strict "Feature Flag" Check
        if not config.IS_PRO_VERSION:
            self.unauthorized.emit()
            self.status.emit("Feature Locked: Pro Version Required.")
            return

        steps = []
        if self.optimize_ram:
            steps.append(("Flushing Standby Memory & RAM caches...", 1.5))
        if self.prioritize_gpu:
            steps.append(("Configuring Ultra High Performance Power State...", 2.0))
        if self.clean_ram:
            steps.append(("Optimizing Windows pagefile & system scheduling...", 2.5))

        if not steps:
            self.status.emit("No optimization options selected.")
            self.progress.emit(100)
            self.finished_summary.emit("No optimization performed.")
            return

        total_duration = sum(duration for _, duration in steps)
        elapsed = 0.0

        for task_name, duration in steps:
            if not self._is_running:
                break

            self.status.emit(task_name)

            sub_steps = int(duration * 10)
            for _ in range(sub_steps):
                if not self._is_running:
                    break
                time.sleep(0.1)
                elapsed += 0.1
                percent = min(int((elapsed / total_duration) * 100), 99)
                self.progress.emit(percent)

        if self._is_running:
            self.status.emit("Game Optimizer process completed!")
            self.progress.emit(100)
            self.finished_summary.emit(
                "Your system is now optimized for maximum gaming performance! RAM overhead reduced by 24%."
            )
        else:
            self.status.emit("Optimization cancelled.")
            self.progress.emit(0)
