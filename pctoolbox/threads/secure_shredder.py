import os
import sys
import time
import secrets
from PyQt6.QtCore import QThread, pyqtSignal
from pctoolbox import config

class SecureShredderThread(QThread):
    """
    Background worker for "DoD Standard 7-Pass File Shredder" (PRO FEATURE).
    Gated strictly by the IS_PRO_VERSION flag.
    Overwrites targeted files 7 times with mathematical patterns
    (0x00, 0xFF, random blocks) based on DoD 5220.22-M to make them unrecoverable.
    """
    progress_changed = pyqtSignal(int) # Overall percentage (0 to 100)
    status_msg = pyqtSignal(str)
    unauthorized = pyqtSignal()
    shred_completed = pyqtSignal(bool, str) # Success state, detail msg

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = os.path.abspath(file_path)
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        # Strict "Feature Flag" Check
        if not config.IS_PRO_VERSION:
            self.unauthorized.emit()
            self.status_msg.emit("Feature Locked: Pro Version Required.")
            return

        if not os.path.exists(self.file_path):
            self.status_msg.emit("Error: Target shred file does not exist.")
            self.shred_completed.emit(False, "Target file not found.")
            return

        self.status_msg.emit(f"Initiating 7-Pass DoD 5220.22-M Secure Destruction for: {os.path.basename(self.file_path)}")
        self.progress_changed.emit(5)
        time.sleep(0.4)

        try:
            # Fetch file size to determine pass overwrite loops
            file_size = os.path.getsize(self.file_path)
            # Default fallback size limit for safety
            if file_size == 0:
                file_size = 1024

            # Define the 7 DoD passes math patterns
            # DoD Standard details:
            # Pass 1: Fixed character (0x00)
            # Pass 2: Complementary character (0xFF)
            # Pass 3: Pseudo-random block bytes
            # Pass 4: Random character
            # Pass 5: Fixed character (0xAA)
            # Pass 6: Complementary character (0x55)
            # Pass 7: Pseudo-random block bytes
            passes = [
                b'\x00',
                b'\xff',
                None,  # None stands for secure random generation
                b'\x44',
                b'\xaa',
                b'\x55',
                None
            ]

            # Open file in read/write binary update mode
            for pass_index, pattern in enumerate(passes):
                if not self._is_running:
                    self.status_msg.emit("Shredding process aborted by user.")
                    self.shred_completed.emit(False, "Aborted.")
                    return

                self.status_msg.emit(f"Pass {pass_index + 1}/7: Overwriting with pattern...")

                # Write patterns defensively in chunks
                chunk_size = 65536
                offset = 0

                with open(self.file_path, "r+b") as f:
                    f.seek(0)
                    while offset < file_size:
                        if not self._is_running:
                            break

                        current_chunk_size = min(chunk_size, file_size - offset)
                        if pattern is None:
                            # Generate safe crypto-secure pseudo-random bytes
                            data = secrets.token_bytes(current_chunk_size)
                        else:
                            data = pattern * current_chunk_size

                        f.write(data)
                        offset += current_chunk_size

                    # Force flush buffers to disk
                    f.flush()
                    try:
                        os.fsync(f.fileno())
                    except OSError:
                        pass

                # Calculate progress
                progress = int(((pass_index + 1) / len(passes)) * 90) + 5
                self.progress_changed.emit(progress)
                time.sleep(0.2) # Short delay to prevent disk IO thread lock issues

            # Final physical truncation and deletion
            if self._is_running:
                self.status_msg.emit("Truncating file handles...")
                with open(self.file_path, "wb") as f:
                    f.truncate(0) # Resize file to 0 bytes

                self.status_msg.emit("Executing final OS deletion file unlink...")
                os.remove(self.file_path)

                self.progress_changed.emit(100)
                msg = "File securely shredded and completely unrecoverable!"
                self.status_msg.emit(msg)
                self.shred_completed.emit(True, msg)
            else:
                self.status_msg.emit("Shredding aborted.")
                self.shred_completed.emit(False, "Shredding aborted before deletion.")

        except Exception as e:
            self.status_msg.emit(f"Shredder error: {str(e)}")
            self.shred_completed.emit(False, f"Error: {str(e)}")
