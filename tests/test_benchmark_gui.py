"""
test_benchmark_gui.py - Unit test tu dong cho Giao dien do hoa Benchmark GUI.
"""

from __future__ import annotations

import os
import sys
import unittest

# Bat buoc chay Qt o che do offscreen de test tren headless / CI
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication

BENCH_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmark")
if BENCH_DIR not in sys.path:
    sys.path.insert(0, BENCH_DIR)

import gui


class TestBenchmarkGUI(unittest.TestCase):
    """Kiem tra khoi tao va cac ham logic cua BenchmarkWindow."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def setUp(self):
        self.window = gui.BenchmarkWindow()

    def tearDown(self):
        self.window.close()

    def test_window_initialization(self):
        """Kiem tra khoi tao cua so va cac tab."""
        self.assertIn("Benchmark", self.window.windowTitle())
        self.assertEqual(self.window.tabs.count(), 3)
        self.assertEqual(self.window.tabs.tabText(0), "🕹️ Thực thi Benchmark")
        self.assertEqual(self.window.tabs.tabText(1), "📊 Xem 8 Biểu đồ")
        self.assertEqual(self.window.tabs.tabText(2), "📋 Bảng Thống kê & Báo cáo")

    def test_mode_switching(self):
        """Kiem tra chuyen doi che do Local / Sender / Server."""
        # Mac dinh la Local
        self.assertTrue(self.window.radio_local.isChecked())
        self.assertEqual(self.window.edit_host.text(), "127.0.0.1")
        self.assertFalse(self.window.edit_host.isEnabled())

        # Chuyen sang Sender Remote
        self.window.radio_sender.setChecked(True)
        self.window._on_mode_changed(2)
        self.assertTrue(self.window.edit_host.isEnabled())
        self.assertTrue(self.window.btn_ping.isEnabled())
        self.assertIn("SENDER", self.window.btn_start.text())

        # Chuyen sang Receiver Server
        self.window.radio_server.setChecked(True)
        self.window._on_mode_changed(3)
        self.assertEqual(self.window.edit_host.text(), "0.0.0.0")
        self.assertFalse(self.window.edit_host.isEnabled())
        self.assertIn("SERVER", self.window.btn_start.text())

    def test_client_progress_updates_table_and_cards(self):
        """Kiem tra cap nhat tien trinh va chen dong vao bang live."""
        sample_progress = {
            "is_warmup": False,
            "current_run": 1,
            "total_runs": 10,
            "combo_idx": 1,
            "total_combos": 1,
            "algo": "AES-128-CBC",
            "size_bytes": 1024,
            "row": {
                "run_id": 1,
                "algorithm": "AES-128-CBC",
                "size_bytes": 1024,
                "ciphertext_size_bytes": 1040,
                "packet_size_bytes": 1056,
                "encryption_ms": 0.05,
                "decrypt_ms": 0.04,
                "verify_ms": 0.01,
                "rtt_ms": 0.12,
                "total_ms": 0.17,
                "throughput_kbps": 6023.5,
                "enc_cpu_pct": 0.0,
                "dec_cpu_pct": 0.0,
                "enc_ram_mb": 105.0,
                "dec_ram_mb": 105.0,
                "enc_ram_delta_kb": 0.0,
                "dec_ram_delta_kb": 0.0,
                "success": True,
            }
        }
        self.window._on_client_progress(sample_progress)

        self.assertEqual(self.window.table_live.rowCount(), 1)
        self.assertEqual(self.window.table_live.item(0, 0).text(), "#001")
        self.assertEqual(self.window.table_live.item(0, 1).text(), "AES-128-CBC")
        self.assertEqual(self.window.table_live.item(0, 12).text(), "PASS")
        self.assertIn("1 / 10", self.window.lbl_card_progress.text())

    def test_chart_viewer_navigation(self):
        """Kiem tra dieu huong bieu do tren Tab 2."""
        self.assertEqual(self.window.combo_charts.count(), 8)
        self.window.combo_charts.setCurrentIndex(0)
        self.window._on_next_chart()
        self.assertEqual(self.window.combo_charts.currentIndex(), 1)
        self.window._on_prev_chart()
        self.assertEqual(self.window.combo_charts.currentIndex(), 0)

    def test_stats_table_loads(self):
        """Kiem tra doc bang thong ke neu co san file detailed_statistics.csv."""
        stat_csv = os.path.join(self.window.results_dir, "detailed_statistics.csv")
        if os.path.exists(stat_csv):
            self.window._load_stats_table()
            self.assertGreater(self.window.table_stats.rowCount(), 0)

    def test_worker_live_execution(self):
        """Kiem tra khoi chay luong Server + Client thuc te o quy mo mini."""
        import tempfile
        import time

        test_port = 5099
        server_worker = gui.BenchmarkServerWorker("127.0.0.1", test_port)
        server_worker.start()
        time.sleep(0.3)

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_csv = os.path.join(tmpdir, "test.csv")
                client_worker = gui.BenchmarkClientWorker(
                    host="127.0.0.1",
                    port=test_port,
                    output_csv=tmp_csv,
                    seed=42,
                    algorithms=["None"],
                    sizes=[1024],
                    benchmark_runs=1,
                    warmup_runs=0,
                )
                progress_data = []
                client_worker.progress_signal.connect(lambda d: progress_data.append(d))
                client_worker.start()
                client_worker.wait(5000)
                QApplication.processEvents()

                self.assertTrue(os.path.exists(tmp_csv))
                self.assertEqual(len(progress_data), 1)
                self.assertEqual(progress_data[0]["row"]["algorithm"], "None")
        finally:
            server_worker.stop()
            server_worker.wait(2000)


if __name__ == "__main__":
    unittest.main()
