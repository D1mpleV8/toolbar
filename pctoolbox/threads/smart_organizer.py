import os
import re
import shutil
import time
from PyQt6.QtCore import QThread, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pctoolbox import config

class OrganizerEventHandler(FileSystemEventHandler):
    """
    Defensive event handler executing the physical organization of files.
    Standard/Free sorts incoming files into subfolders based on basic extensions.
    Pro/Premium runs filename regex matching and deep-content/metadata keyword routing.
    """
    def __init__(self, watch_dir: str, log_signal: pyqtSignal, rule_signal: pyqtSignal):
        super().__init__()
        self.watch_dir = watch_dir
        self.log_signal = log_signal
        self.rule_signal = rule_signal

        # Basic free categories
        self.categories = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
            "Videos": [".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm"],
            "Docs": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"]
        }

        # Premium Regex Rules (only evaluated when config.IS_PRO_VERSION = True)
        # Pairs: (compile_regex, target_subfolder)
        self.pro_regex_rules = [
            (re.compile(r"screenshot.*", re.IGNORECASE), "Screenshots"),
            (re.compile(r"backup.*", re.IGNORECASE), "Backups"),
            (re.compile(r"temp.*", re.IGNORECASE), "Temp_Files")
        ]

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        filename = os.path.basename(file_path)

        # Ignore temporary downloads (e.g., Chrome .crdownload or Firefox .part)
        if filename.endswith(".crdownload") or filename.endswith(".part") or filename.startswith(".~"):
            return

        # Give the filesystem a moment to unlock the newly written file
        time.sleep(0.3)

        self.log_signal.emit(f"New file detected: {filename}")
        self.organize_file(file_path, filename)

    def organize_file(self, file_path: str, filename: str):
        try:
            if not os.path.exists(file_path):
                return

            dest_folder = None
            rule_matched = "Extension sorting (Free)"

            # Check for Pro Gated Features first
            if config.IS_PRO_VERSION:
                # 1. Advanced Rule Builder - Regex Matching
                for rx, target in self.pro_regex_rules:
                    if rx.match(filename):
                        dest_folder = target
                        rule_matched = f"Pro Regex match: '{rx.pattern}'"
                        break

                # 2. Deep Scan / Content Parsing (e.g., reading text files or PDF simulated contents)
                if not dest_folder:
                    # Let's read simple txt/doc contents to route "Invoices" or "Billing"
                    _, ext = os.path.splitext(filename.lower())
                    if ext in [".txt", ".csv", ".pdf"]:
                        try:
                            # For simplicity we read plain text files to verify the architectural concept.
                            # When reading PDF, we'd use PyPDF or similar; here we read defensively.
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                file_content = f.read(1024) # Read first 1KB defensively
                                if "invoice" in file_content.lower() or "billing" in file_content.lower() or "payment" in file_content.lower():
                                    dest_folder = "Invoices"
                                    rule_matched = "Pro Deep Content scan ('invoice' keyword matched)"
                        except Exception as read_err:
                            self.log_signal.emit(f"Deep Content scan failed for {filename}: {str(read_err)}")

            # Fallback to standard/free extension rules
            if not dest_folder:
                _, ext = os.path.splitext(filename.lower())
                for category, extensions in self.categories.items():
                    if ext in extensions:
                        dest_folder = category
                        break

            # Perform the sorting move
            if dest_folder:
                dest_dir = os.path.join(self.watch_dir, dest_folder)
                os.makedirs(dest_dir, exist_ok=True)

                new_path = os.path.join(dest_dir, filename)
                # Handle filename collisions defensively
                if os.path.exists(new_path):
                    base, ext = os.path.splitext(filename)
                    new_path = os.path.join(dest_dir, f"{base}_{int(time.time())}{ext}")

                shutil.move(file_path, new_path)
                self.log_signal.emit(f"📂 Sorted file to: '{dest_folder}/' [Rule: {rule_matched}]")
                self.rule_signal.emit(dest_folder)
            else:
                self.log_signal.emit(f"No matching rule/category found for: {filename}")

        except Exception as e:
            self.log_signal.emit(f"Error organizing file {filename}: {str(e)}")


class SmartOrganizerThread(QThread):
    """
    Background QThread handling the watchdog Observer lifecycle.
    Keeps filesystem monitoring completely separate from the UI thread to prevent freezes.
    """
    log_msg = pyqtSignal(str)
    rule_matched = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, watch_dir: str = None):
        super().__init__()
        self.watch_dir = watch_dir or os.path.expanduser("~/Downloads")
        self.observer = None
        self._is_running = True

    def stop(self):
        self._is_running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.status_changed.emit("Status: Stopped")

    def run(self):
        # Create target watch directory if it doesn't exist
        os.makedirs(self.watch_dir, exist_ok=True)

        self.log_msg.emit(f"Initializing watchdog observer on: {self.watch_dir}")
        self.status_changed.emit("Status: Monitoring Active")

        # Set up watchdog
        event_handler = OrganizerEventHandler(self.watch_dir, self.log_msg, self.rule_matched)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.watch_dir, recursive=False)
        self.observer.start()

        try:
            while self._is_running:
                # Keep QThread alive, processing filesystem notifications
                time.sleep(1.0)
        except Exception as e:
            self.log_msg.emit(f"Watchdog Observer error: {str(e)}")
        finally:
            if self.observer and self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
            self.log_msg.emit("Watchdog thread exited.")
