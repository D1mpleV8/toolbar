import os
import sys
import time
from PyQt6.QtCore import QThread, pyqtSignal
from pctoolbox import config

class QuickLauncherThread(QThread):
    """
    Background worker for index-based Quick Launcher local/web searches.
    Safely indexes files, application signatures, and handles Pro-Gated AI requests
    without causing any main GUI frame drops.
    """
    search_completed = pyqtSignal(list) # Emits list of search results
    status_changed = pyqtSignal(str)

    def __init__(self, query: str = ""):
        super().__init__()
        self.query = query.strip()

        # Local mock database of apps & control panel tools
        self.local_index = [
            {"name": "Steam Client", "type": "App", "path": "C:/Program Files (x86)/Steam/steam.exe"},
            {"name": "Counter-Strike 2", "type": "Game", "path": "steam://run/730"},
            {"name": "Valorant", "type": "Game", "path": "C:/Riot Games/Valorant.exe"},
            {"name": "Control Panel - Graphics Settings", "type": "Setting", "path": "control.exe graphics"},
            {"name": "Device Manager", "type": "Setting", "path": "devmgmt.msc"},
            {"name": "System Cleaner Utility", "type": "Tool", "path": "pctoolbox://cleaner"},
            {"name": "Game Optimizer Utility", "type": "Tool", "path": "pctoolbox://optimizer"},
            {"name": "Network Manager", "type": "Tool", "path": "pctoolbox://network"},
            {"name": "Smart Folder Organizer", "type": "Tool", "path": "pctoolbox://organizer"}
        ]

    def run(self):
        if not self.query:
            self.search_completed.emit([])
            return

        self.status_changed.emit("Searching...")
        time.sleep(0.1) # Simulate quick asynchronous search debounce latency

        # 1. Pro AI / Web Query Check (Query starts with "?")
        if self.query.startswith("?"):
            ai_query = self.query[1:].strip()

            # Gated Feature Flag licensing check
            if not config.IS_PRO_VERSION:
                # Elegant locked indicator result
                self.search_completed.emit([{
                    "name": "🔑 GPT-4 Search: '" + ai_query + "'",
                    "type": "PRO LOCKED",
                    "path": "PRO_LOCKED"
                }])
                return

            if not ai_query:
                self.search_completed.emit([{
                    "name": "Type a query after ? to ask GPT-4...",
                    "type": "AI Status",
                    "path": "AI_HELP"
                }])
                return

            # Pro-Active simulated ChatGPT / web search response
            self.status_changed.emit("Consulting ChatGPT-4 AI...")
            time.sleep(0.8) # Simulate AI thinking delay

            ai_responses = {
                "ping": "GPT-4 AI: Ping is latency of network packet. Use Google DNS (8.8.8.8) or Cloudflare (1.1.1.1) to optimize.",
                "clean": "GPT-4 AI: System cleaning removes browser temporary files and OS caches safely to reclaim disk space.",
                "fps": "GPT-4 AI: To maximize gaming FPS, close background browser downloads and enable GPU Hardware Acceleration."
            }

            matched_answer = "GPT-4 AI: No instant prompt matches. Launching search on DuckDuckGo..."
            for keyword, ans in ai_responses.items():
                if keyword in ai_query.lower():
                    matched_answer = ans
                    break

            self.search_completed.emit([
                {"name": matched_answer, "type": "ChatGPT Response", "path": f"https://duckduckgo.com/?q={ai_query}"},
                {"name": f"Search Web for: '{ai_query}'", "type": "Web Search", "path": f"https://duckduckgo.com/?q={ai_query}"}
            ])
            return

        # 2. Free Local Index Search
        results = []
        for item in self.local_index:
            if self.query.lower() in item["name"].lower() or self.query.lower() in item["type"].lower():
                results.append(item)

        # Dynamic local folder scans (Simulated defensively)
        if len(results) < 5:
            # Let's search mock folders to find local files matching query
            mock_files = ["billing_invoice.txt", "vacation_photo.png", "cs2_config.cfg", "backup_restore.zip"]
            for f in mock_files:
                if self.query.lower() in f.lower():
                    results.append({"name": f, "type": "Local File", "path": f"C:/Users/User/Documents/{f}"})

        self.search_completed.emit(results)
        self.status_changed.emit("Status: Complete")
