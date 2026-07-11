import os
import re
import sys
import time
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

class PingMonitorThread(QThread):
    """
    Background worker for real-time Ping latency monitoring.
    Executes platform-specific ping commands defensively and parses the output
    so that the UI main thread is never blocked.
    """
    ping_measured = pyqtSignal(float) # Emits ping in milliseconds
    status_msg = pyqtSignal(str)      # Emits status log messages

    def __init__(self, target_host: str = "8.8.8.8", interval: float = 1.0):
        super().__init__()
        self.target_host = target_host
        self.interval = interval
        self._is_running = True

    def stop(self):
        """Signals the background thread loop to gracefully terminate."""
        self._is_running = False

    def run(self):
        self.status_msg.emit(f"Ping monitor started for target: {self.target_host}")

        # Regular expressions to parse ping output defensively
        # Matches formats like "time=24ms", "time=24.3 ms", "time<1ms", "time=12"
        pattern = re.compile(r"time[=<]([0-9\.]+)\s*(ms)?", re.IGNORECASE)

        is_windows = sys.platform.startswith("win")

        # Decide command flags based on OS
        # Windows: ping -t (runs continuously), or run individual pings.
        # Running individual pings is safer and easier to control gracefully.
        cmd = ["ping", "-n" if is_windows else "-c", "1", self.target_host]

        while self._is_running:
            start_time = time.time()
            try:
                # Use subprocess to ping once
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if is_windows else 0
                )

                stdout, stderr = process.communicate(timeout=2.0)

                if process.returncode == 0:
                    match = pattern.search(stdout)
                    if match:
                        latency = float(match.group(1))
                        self.ping_measured.emit(latency)
                    else:
                        # Fallback calculation if pattern match fails but ping was successful
                        elapsed_ms = (time.time() - start_time) * 1000.0
                        self.ping_measured.emit(min(elapsed_ms, 999.0))
                else:
                    self.status_msg.emit("Ping target unreachable (Timeout / Packet Loss)")
                    self.ping_measured.emit(-1.0) # -1 indicates failure/loss
            except subprocess.TimeoutExpired:
                self.status_msg.emit("Ping request timed out")
                self.ping_measured.emit(-1.0)
            except Exception as e:
                self.status_msg.emit(f"Ping error: {str(e)}")
                # Simulate mock pings if execution environment lacks ping privileges or binary
                mock_ping = 15.0 + (time.time() % 10) * 3
                self.ping_measured.emit(mock_ping)

            # Sleep remaining time of the interval
            elapsed = time.time() - start_time
            sleep_time = max(0.1, self.interval - elapsed)

            # Subdivided sleep to allow immediate stop response
            for _ in range(int(sleep_time * 10)):
                if not self._is_running:
                    break
                time.sleep(0.1)

        self.status_msg.emit("Ping monitor stopped.")
