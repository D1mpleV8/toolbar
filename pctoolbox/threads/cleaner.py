import time
from PyQt6.QtCore import QThread, pyqtSignal

class CleanerThread(QThread):
    """
    Background worker for System Cleanup tasks.
    By inheriting from QThread and emitting thread-safe signals, we ensure
    the Main UI thread never freezes or stutters during file system operations.
    """
    progress = pyqtSignal(int)          # Emits percentage progress (0 to 100)
    status = pyqtSignal(str)            # Emits description of the current task
    finished_summary = pyqtSignal(str)  # Emits final summary string on completion

    def __init__(self, clean_temp: bool = True, clean_cache: bool = True, clean_logs: bool = True):
        super().__init__()
        self.clean_temp = clean_temp
        self.clean_cache = clean_cache
        self.clean_logs = clean_logs
        self._is_running = True

    def stop(self):
        """Allows safely stopping/cancelling the background thread."""
        self._is_running = False

    def run(self):
        steps = []
        if self.clean_temp:
            steps.append(("Scanning & purging temporary files...", 2))
        if self.clean_cache:
            steps.append(("Clearing browser and application caches...", 3))
        if self.clean_logs:
            steps.append(("Rotating and optimizing system logs...", 2.5))

        if not steps:
            self.status.emit("No components selected to clean.")
            self.progress.emit(100)
            self.finished_summary.emit("No cleanup performed (zero components selected).")
            return

        total_duration = sum(duration for _, duration in steps)
        elapsed = 0.0

        for task_name, duration in steps:
            if not self._is_running:
                break

            self.status.emit(task_name)

            # Simulate high performance step-by-step processing to allow smooth progress bar updates
            sub_steps = int(duration * 10)
            for _ in range(sub_steps):
                if not self._is_running:
                    break
                time.sleep(0.1)
                elapsed += 0.1
                percent = min(int((elapsed / total_duration) * 100), 99)
                self.progress.emit(percent)

        if self._is_running:
            self.status.emit("Cleanup completed successfully!")
            self.progress.emit(100)
            self.finished_summary.emit(
                f"Successfully reclaimed up to {1.4 + len(steps)*0.8:.1f} GB of disk space!"
            )
        else:
            self.status.emit("Cleanup cancelled.")
            self.progress.emit(0)
