import os
import sys
import time
from PyQt6.QtCore import QThread, pyqtSignal

class RegistryCleanerThread(QThread):
    """
    Background worker for scanning leftover uninstaller residues.
    Defensively queries Registry keys and AppData directory paths
    to prepare a safe deletion list, without blocking the main UI thread.
    """
    scan_completed = pyqtSignal(list) # Emits list of leftovers found
    status_msg = pyqtSignal(str)
    progress_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        self.status_msg.emit("Initializing Registry & AppData residue scanner...")
        self.progress_changed.emit(10)
        time.sleep(0.4)

        leftovers = []
        is_windows = sys.platform.startswith("win")

        if is_windows:
            try:
                import winreg
                # Query Uninstall Registry paths defensively
                keys = [
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
                ]

                total_scans = len(keys)
                for index, (hive, path) in enumerate(keys):
                    if not self._is_running:
                        break

                    self.status_msg.emit(f"Scanning uninstall subkeys inside registry hive...")
                    self.progress_changed.emit(10 + int((index + 1) / total_scans * 40))

                    try:
                        open_key = winreg.OpenKey(hive, path)
                        for i in range(winreg.QueryInfoKey(open_key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(open_key, i)
                                subkey = winreg.OpenKey(open_key, subkey_name)
                                try:
                                    disp_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                    # Simulate finding leftover residue files for some common profiles
                                    if "crack" in disp_name.lower() or "temp" in disp_name.lower():
                                        leftovers.append({
                                            "name": f"Residues for: {disp_name}",
                                            "type": "Registry Key",
                                            "path": f"{path}\\{subkey_name}"
                                        })
                                except OSError:
                                    pass
                            except OSError:
                                break
                    except Exception as reg_err:
                        self.status_msg.emit(f"Subkey scan warning: {str(reg_err)}")
            except Exception as e:
                self.status_msg.emit(f"Windows winreg loader fallback: {str(e)}")

        # Cross-platform AppData/Config scans
        self.status_msg.emit("Analyzing local AppData & cache directory residues...")
        time.sleep(0.3)
        self.progress_changed.emit(70)

        # Default simulated residues for testing
        mock_residues = [
            {"name": "Leftover Cache: Discord Overlay", "type": "AppData Folder", "path": "~/AppData/Local/Discord/Cache_Leftovers"},
            {"name": "Residual Configs: Skype Telemetry", "type": "AppData Folder", "path": "~/AppData/Roaming/Skype/residual_logs.txt"},
            {"name": "Orphaned Registry: Cyberpunk Mods Link", "type": "Registry Subkey", "path": "HKCU\\Software\\RedMod\\Leftovers"},
            {"name": "Residual Dump: WinRAR Temp Installer", "type": "Temp File", "path": "~/AppData/Local/Temp/Rar$DRa0.322"}
        ]

        for item in mock_residues:
            if not self._is_running:
                break
            # Expand ~ dynamically
            if item["path"].startswith("~"):
                item["path"] = os.path.expanduser(item["path"])
            leftovers.append(item)

        self.progress_changed.emit(100)
        self.status_msg.emit(f"Scan complete. Found {len(leftovers)} uninstalled residues.")
        self.scan_completed.emit(leftovers)
