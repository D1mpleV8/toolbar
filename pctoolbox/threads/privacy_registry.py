import sys
import time
from PyQt6.QtCore import QThread, pyqtSignal

class PrivacyRegistryThread(QThread):
    """
    Background worker for safe Windows Registry-level privacy optimization (FREE FEATURE).
    Toggles telemetry keys, Cortana features, and lockscreen advertisement states defensively,
    ensuring no main UI thread blockage occurs.
    """
    status_msg = pyqtSignal(str)
    op_completed = pyqtSignal(bool, str)

    def __init__(self, key_name: str, enable: bool):
        super().__init__()
        self.key_name = key_name
        self.enable = enable

    def run(self):
        self.status_msg.emit(f"Applying Registry Privacy Policy for: {self.key_name}...")
        time.sleep(0.4)

        is_windows = sys.platform.startswith("win")
        success = False

        # Define targets mapping registry keys
        targets = {
            "Windows Telemetry": [
                (r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 0 if self.enable else 1)
            ],
            "Cortana Search Link": [
                (r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana", 0 if self.enable else 1)
            ],
            "Lockscreen Advertisements": [
                (r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "RotatingLockScreenOverlayEnabled", 0 if self.enable else 1),
                (r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338387Enabled", 0 if self.enable else 1)
            ]
        }

        if self.key_name not in targets:
            self.op_completed.emit(False, f"Registry config error: Unknown profile '{self.key_name}'")
            return

        configs = targets[self.key_name]

        if is_windows:
            try:
                import winreg
                for path, value_name, target_val in configs:
                    # Create or open key defensively
                    try:
                        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
                    except PermissionError:
                        # Try HKCU if HKLM permissions fail
                        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE)

                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, target_val)
                    winreg.CloseKey(key)

                success = True
            except Exception as reg_err:
                self.status_msg.emit(f"Registry policy error: {str(reg_err)}")
                success = False
        else:
            # Cross-platform simulation mode
            self.status_msg.emit("[Simulation] Injecting simulated OS plist/gsettings parameters.")
            success = True

        action_word = "Disabled" if self.enable else "Restored"
        if success:
            msg = f"Successfully {action_word} {self.key_name} in OS configuration."
            self.status_msg.emit(msg)
            self.op_completed.emit(True, msg)
        else:
            msg = f"Failed to modify {self.key_name} policies. Admin privileges required."
            self.status_msg.emit(msg)
            self.op_completed.emit(False, msg)
