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
BENCH_DIR = os.path.join(ROOT_DIR, "benchmark")
if BENCH_DIR not in sys.path:
    sys.path.insert(0, BENCH_DIR)

from gui import main

if __name__ == "__main__":
    main()
