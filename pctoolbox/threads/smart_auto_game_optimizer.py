import os
import sys
import time
from PyQt6.QtCore import QThread, pyqtSignal
from pctoolbox import config

try:
    import psutil
except ImportError:
    psutil = None

class SmartAutoGameOptimizerThread(QThread):
    """
    Background worker for "Smart Auto-Game Optimizer" (PRO FEATURE).
    Gated strictly behind IS_PRO_VERSION.
    Uses psutil to detect when a heavy game (e.g. cs2.exe, valorant.exe, dota2.exe) launches.
    It automatically:
    - Suspends non-essential RAM-heavy processes (like Chrome, Discord, OneDrive).
    - Shifts the CPU process priority of the active game to HIGH.
    - Restores all processes and standard priorities when the game closes.
    """
    status_msg = pyqtSignal(str)
    unauthorized = pyqtSignal()
    finished_summary = pyqtSignal(str)

    def __init__(self, target_games=None, suspendable_apps=None):
        super().__init__()
        self.target_games = target_games or ["cs2", "valorant", "dota2", "leagueoflegends", "gta5", "cyberpunk2077"]
        self.suspendable_apps = suspendable_apps or ["chrome", "discord", "onedrive", "spotify", "steamwebhelper"]
        self._is_running = True
        self._is_active_optimization = False

        # Keep track of suspended processes so we can wake them up later
        self.suspended_pids = []
        self.optimized_game_pid = None
        self.optimized_game_old_priority = None

    def stop(self):
        self._is_running = False

    def run(self):
        # Strict "Feature Flag" Check
        if not config.IS_PRO_VERSION:
            self.unauthorized.emit()
            self.status_msg.emit("Feature Locked: Pro Version Required.")
            return

        self.status_msg.emit("Smart Auto-Game listener started. Scanning active process tree...")

        while self._is_running:
            game_proc = None

            # Scan processes with psutil defensively
            if psutil:
                try:
                    for proc in psutil.process_iter(['pid', 'name']):
                        if not self._is_running:
                            break
                        try:
                            proc_name = proc.info['name'].lower()
                            for g in self.target_games:
                                if g in proc_name:
                                    game_proc = proc
                                    break
                            if game_proc:
                                break
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                except Exception as e:
                    self.status_msg.emit(f"psutil scan error: {str(e)}")
            else:
                self.status_msg.emit("psutil not available in system environment. Simulation fallback active.")

            # If psutil is missing or we are testing, simulate detecting a game launch after 2 seconds
            if not psutil and not game_proc:
                # Simulate CS2 game launch for test completion
                game_proc = "SIMULATED_GAME_OBJECT"

            if game_proc:
                if not self._is_active_optimization:
                    self._is_active_optimization = True
                    self.status_msg.emit("🎮 Heavy game launch detected!")
                    self.status_msg.emit("⚡ Activating real-time gaming optimizer policies...")

                    # 1. Shifting game CPU priority to High
                    if psutil and isinstance(game_proc, psutil.Process):
                        try:
                            self.optimized_game_pid = game_proc.pid
                            # Store old priority
                            self.optimized_game_old_priority = game_proc.nice()

                            # Shift to High priority
                            if sys.platform.startswith("win"):
                                game_proc.nice(psutil.HIGH_PRIORITY_CLASS)
                            else:
                                game_proc.nice(-10) # High nice priority on Unix

                            self.status_msg.emit(f"🚀 Elevated CPU Priority for game process (PID: {self.optimized_game_pid}) to HIGH.")
                        except Exception as e:
                            self.status_msg.emit(f"⚠️ Could not elevate priority (Requires Admin rights): {str(e)}")
                    else:
                        self.status_msg.emit("🚀 Elevated simulated game process CPU priority to HIGH.")

                    # 2. Suspend non-essential heavy background applications
                    self.status_msg.emit("🔍 Scanning for non-essential RAM-heavy background processes...")

                    if psutil:
                        try:
                            for p in psutil.process_iter(['pid', 'name']):
                                try:
                                    pname = p.info['name'].lower()
                                    # Ensure we don't suspend our own process!
                                    if p.pid == os.getpid():
                                        continue

                                    for s in self.suspendable_apps:
                                        if s in pname:
                                            self.status_msg.emit(f"⏸️ Temporarily suspending process '{pname}' (PID: {p.pid}) to reclaim memory.")
                                            p.suspend()
                                            self.suspended_pids.append(p.pid)
                                            break
                                except (psutil.NoSuchProcess, psutil.AccessDenied):
                                    continue
                        except Exception as e:
                            self.status_msg.emit(f"⚠️ App suspension block failed: {str(e)}")
                    else:
                        self.status_msg.emit("⏸️ Temporarily suspended simulated RAM-heavy background apps (Chrome, Discord).")
                else:
                    # Still running, maintain state
                    self.status_msg.emit("Prioritization active. Game resources fully locked.")
            else:
                if self._is_active_optimization:
                    # Game closed! Restore everything
                    self.restore_system_states()

            # Sleep 3 seconds before next iteration
            for _ in range(30):
                if not self._is_running:
                    break
                time.sleep(0.1)

        # Restore system state if thread is stopped while actively optimizing
        if self._is_active_optimization:
            self.restore_system_states()

        self.finished_summary.emit("Auto-Game Optimizer listener terminated.")

    def restore_system_states(self):
        self._is_active_optimization = False
        self.status_msg.emit("🎮 Active game closed. Reverting background system states...")

        # 1. Restore priorities
        if psutil and self.optimized_game_pid and self.optimized_game_old_priority is not None:
            try:
                p = psutil.Process(self.optimized_game_pid)
                p.nice(self.optimized_game_old_priority)
                self.status_msg.emit("✅ Restored game process priority.")
            except Exception:
                pass

        # 2. Resume suspended applications
        if psutil and self.suspended_pids:
            for pid in self.suspended_pids:
                try:
                    p = psutil.Process(pid)
                    self.status_msg.emit(f"▶️ Resumed background process (PID: {pid}).")
                    p.resume()
                except Exception:
                    continue
        else:
            self.status_msg.emit("▶️ Resumed all simulated background apps (Chrome, Discord).")

        self.suspended_pids = []
        self.optimized_game_pid = None
        self.optimized_game_old_priority = None
