#!/usr/bin/env python3
"""
benchmark_gui.py - Trinh khoi chay nhanh Giao dien do hoa Benchmark Ma hoa Mang.

Cach chay:
python benchmark_gui.py
"""

import os
import sys

# Dam bao import duoc benchmark.gui
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
BENCH_DIR = os.path.join(ROOT_DIR, "benchmark")
if BENCH_DIR not in sys.path:
    sys.path.insert(0, BENCH_DIR)

if __name__ == "__main__":
    try:
        try:
            from benchmark.gui import main
        except ImportError:
            from gui import main
        main()
    except Exception as exc:
        import traceback
        err_msg = traceback.format_exc()
        # Ghi log ra file de nguoi dung co the xem ngay
        log_path = os.path.join(ROOT_DIR, "error_log.txt")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(err_msg)
        except Exception:
            pass

        # Hien hop thoai loi neu tren Windows va nguoi dung click dup chuot
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Không thể khởi động Giao diện Benchmark!\n\nChi tiết lỗi:\n{err_msg}\n\nThông tin lỗi đã được lưu vào: error_log.txt",
                "Lỗi Khởi Động Benchmark GUI",
                0x10,  # MB_ICONERROR
            )
        except Exception:
            pass
        raise
