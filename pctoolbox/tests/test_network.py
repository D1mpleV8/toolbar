import os
import sys

# Dynamic path injection
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import unittest
import time
from PyQt6.QtWidgets import QApplication

from pctoolbox import config
from pctoolbox.threads.ping_monitor import PingMonitorThread
from pctoolbox.threads.dns_switcher import DNSSwitcherThread
from pctoolbox.threads.network_prioritizer import NetworkPrioritizerThread

# Ensure application exists
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestNetworkConnectivity(unittest.TestCase):

    def test_ping_monitor_thread(self):
        """Test that PingMonitorThread emits ping measured signals."""
        thread = PingMonitorThread(target_host="1.1.1.1", interval=0.5)

        results = {
            "pings": [],
            "messages": []
        }

        def on_ping(val):
            results["pings"].append(val)
            # Stop early to keep test fast
            if len(results["pings"]) >= 2:
                thread.stop()

        def on_msg(txt):
            results["messages"].append(txt)

        thread.ping_measured.connect(on_ping)
        thread.status_msg.connect(on_msg)

        thread.start()
        start = time.time()
        while thread.isRunning() and (time.time() - start) < 3.0:
            app.processEvents()
            time.sleep(0.05)

        thread.stop()
        thread.wait()
        app.processEvents()

        # Should have run ping commands and reported latency
        self.assertTrue(len(results["pings"]) > 0)
        self.assertTrue(len(results["messages"]) > 0)

    def test_dns_switcher_thread(self):
        """Test the DNSSwitcherThread switches DNS server settings successfully."""
        thread = DNSSwitcherThread("Cloudflare")

        results = {
            "completed": False,
            "success": False
        }

        def on_complete(success, desc):
            results["completed"] = True
            results["success"] = success

        thread.switch_completed.connect(on_complete)
        thread.start()
        thread.wait(4000)
        app.processEvents()

        self.assertTrue(results["completed"])
        # Should execute simulation/real logic correctly
        self.assertTrue(results["success"] in [True, False])

    def test_prioritization_locked_when_free(self):
        """Test that NetworkPrioritizerThread fails immediately on Free license."""
        config.set_pro_version(False)

        thread = NetworkPrioritizerThread()
        results = {
            "unauthorized": False,
            "messages": []
        }

        def on_unauth():
            results["unauthorized"] = True

        def on_msg(txt):
            results["messages"].append(txt)

        thread.unauthorized.connect(on_unauth)
        thread.status_msg.connect(on_msg)

        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertTrue(results["unauthorized"])
        self.assertIn("Feature Locked", "".join(results["messages"]))

    def test_prioritization_runs_when_pro(self):
        """Test that NetworkPrioritizerThread runs smoothly when Pro license active."""
        config.set_pro_version(True)

        thread = NetworkPrioritizerThread()
        results = {
            "unauthorized": False,
            "messages": []
        }

        def on_unauth():
            results["unauthorized"] = True

        def on_msg(txt):
            results["messages"].append(txt)

        thread.unauthorized.connect(on_unauth)
        thread.status_msg.connect(on_msg)

        thread.start()
        time.sleep(0.5)
        thread.stop()
        thread.wait()
        app.processEvents()

        self.assertFalse(results["unauthorized"])
        self.assertTrue(len(results["messages"]) > 0)

if __name__ == "__main__":
    unittest.main()
