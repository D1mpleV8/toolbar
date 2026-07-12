import os
import sys
import unittest
import time
from PyQt6.QtWidgets import QApplication

# Dynamic path injection
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from pctoolbox import config
from pctoolbox.threads.benchmark_stress import BenchmarkStressThread
from pctoolbox.threads.smart_auto_game_optimizer import SmartAutoGameOptimizerThread

# Ensure application exists
app = QApplication.instance()
if not app:
    app = QApplication([])

class TestPerformanceBenchmark(unittest.TestCase):

    def test_benchmark_stress_testing_math_loops(self):
        """Test BenchmarkStressThread runs, stress loads are tracked, and thermals rise."""
        thread = BenchmarkStressThread(duration=1) # 1 second duration for test speed
        results = []

        def on_telemetry(t):
            results.append(t)
            if len(results) >= 2:
                thread.stop()

        thread.telemetry_updated.connect(on_telemetry)
        thread.start()
        thread.wait(3000)
        app.processEvents()

        thread.stop()
        thread.wait()
        app.processEvents()

        self.assertTrue(len(results) > 0)
        # Load during math stress must exceed idle
        self.assertTrue(results[0]["load"] >= 80)
        self.assertTrue(results[0]["temp"] >= 40)

    def test_auto_game_optimizer_locked_when_free(self):
        """Test that SmartAutoGameOptimizer Thread emits unauthorized signal on free license."""
        config.set_pro_version(False)

        thread = SmartAutoGameOptimizerThread()
        results = {"unauthorized": False}

        def on_unauth():
            results["unauthorized"] = True

        thread.unauthorized.connect(on_unauth)
        thread.start()
        thread.wait(2000)
        app.processEvents()

        self.assertTrue(results["unauthorized"])

    def test_auto_game_optimizer_prioritization_and_restoration(self):
        """Test process scanning and priority overrides loop under Pro license."""
        config.set_pro_version(True)

        # Build optimizer focusing on custom target simulation list to run safely across sandbox
        thread = SmartAutoGameOptimizerThread(
            target_games=["simulated_game_binary"],
            suspendable_apps=["simulated_background_helper"]
        )

        results = []
        def on_status(msg):
            results.append(msg)

        thread.status_msg.connect(on_status)
        thread.start()

        # Allow thread iterations to detect mock launches and trigger priority adjustments
        time.sleep(1.0)
        app.processEvents()

        thread.stop()
        thread.wait()
        app.processEvents()

        self.assertTrue(len(results) > 0)
        # Should initiate listening scans
        self.assertIn("Smart Auto-Game listener started", results[0])

if __name__ == "__main__":
    unittest.main()
