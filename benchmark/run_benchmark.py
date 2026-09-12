"""
run_benchmark.py - Trinh dieu phoi toan bo quy trinh Benchmark:
1. Kiem tra mang / ping test toi Receiver (neu la IP tu xa).
2. Khoi dong server ngam (neu chay che do local) hoac ket noi server VM2.
3. Chay 12 to hop x (1 warm-up + 30 do chinh) = 372 luot.
4. Luu 360 mau phan tich vao CSV.
5. Chay phan tich thong ke pandas va sinh 6 bieu do matplotlib.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import threading
import time

# Them duong dan hien tai vao sys.path
BENCH_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BENCH_DIR)

import analyze
import client
import server


def perform_ping_test(host: str, count: int = 10) -> bool:
    """Kiem tra do tre mang va ti le mat goi bang lenh ping (ho tro ca Windows va Linux)."""
    import platform
    print(f"[*] Dang thuc hien Ping test toi {host} ({count} goi tin) ...")
    try:
        flag = "-n" if platform.system().lower() == "windows" else "-c"
        cmd = ["ping", flag, str(count), host]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=count * 2)
        print(res.stdout)
        out = res.stdout.lower()
        if "0% loss" in out or "0% packet loss" in out or "0.0% packet loss" in out:
            print("[+] Ping test hoan hao: 0% mat goi.")
            return True
        elif "100% loss" in out or "100% packet loss" in out or "unreachable" in out:
            print("[!] CANH BAO: Khong ping duoc toi host. Vui long kiem tra firewall hoac cau hinh mang!")
            return False
        else:
            print("[!] CANH BAO: Co hien tuong mat goi. Kiem tra lai adapter mang Bridge/Host-Only.")
            return True
    except Exception as exc:
        print(f"[!] Khong the thuc hien ping: {exc}")
        return True


def run_full_pipeline(
    host: str = "127.0.0.1",
    port: int = 5000,
    results_dir: str = "benchmark/results",
    seed: int = 42,
    is_local: bool | None = None,
) -> None:
    """Thuc thi toan bo quy trinh benchmark."""
    os.makedirs(results_dir, exist_ok=True)
    csv_file = os.path.join(results_dir, "benchmark_results.csv")
    charts_dir = os.path.join(results_dir, "charts")
    summary_md = os.path.join(results_dir, "summary_table.md")

    # Tu dong phat hien che do:
    # Neu khong truyen hoac la 127.0.0.1 / localhost -> tu chay self-test (khoi dong server ngam)
    # Neu la IP khac -> tu chuyen sang remote (khong khoi dong server ngam)
    clean_host = host.strip() if host else "127.0.0.1"
    if is_local is None:
        is_local = clean_host.lower() in ("127.0.0.1", "localhost")

    server_thread = None
    stop_event = threading.Event()

    if is_local:
        print("[*] Che do SELF-TEST (LOCAL): Tu dong khoi dong Receiver Server noi bo tren luong nen ...")
        def start_bg_server():
            server.run_server(host="127.0.0.1", port=port, stop_event=stop_event)

        server_thread = threading.Thread(target=start_bg_server, daemon=True)
        server_thread.start()
        time.sleep(0.5)  # Cho server san sang
    else:
        print(f"[*] Che do REMOTE: Ket noi toi Receiver tai {clean_host}:{port} (khong bat server noi bo) ...")
        perform_ping_test(clean_host, count=10)

    # 1. Chay benchmark
    t_start = time.perf_counter()
    client.run_benchmark(
        host=clean_host,
        port=port,
        output_csv=csv_file,
        seed=seed,
    )
    total_duration = time.perf_counter() - t_start

    print(f"\n[+] Thoi gian thuc hien toan bo 372 luot benchmark: {total_duration:.2f} giay.")

    # 2. Phan tich du lieu va ve bieu do
    print("\n[*] Dang phan tich du lieu bang pandas va tao bieu do matplotlib ...")
    df = analyze.load_and_validate(csv_file)
    df_rates, df_stats = analyze.compute_statistics(df)
    analyze.generate_charts(df_stats, charts_dir)
    analyze.export_markdown_summary(df_rates, df_stats, summary_md)

    print("\n============================================================")
    print("  HOAN TAT TOAN BO TIEN TRINH BENCHMARK!")
    print(f"  - File CSV:      {csv_file}")
    print(f"  - Bang ket qua:  {summary_md}")
    print(f"  - 8 Bieu do:     {charts_dir}")
    print("============================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Benchmark Orchestrator")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Dia chi IP cua Receiver (mac dinh: 127.0.0.1 -> tu chay self-test; neu la IP khac -> tu dong chuyen sang remote)",
    )
    parser.add_argument("--port", type=int, default=5000, help="Cong TCP (mac dinh: 5000)")
    parser.add_argument("--results-dir", default="benchmark/results", help="Thu muc luu ket qua")
    parser.add_argument("--seed", type=int, default=42, help="Seed ngau nhien")
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Cuong che che do remote (khong bat server noi bo du la 127.0.0.1)",
    )
    parser.add_argument("--gui", action="store_true", help="Mo giao dien do hoa Benchmark GUI")
    args = parser.parse_args()

    if args.gui:
        import gui
        gui.main()
        sys.exit(0)

    # Neu nguoi dung truyen flag --remote ro rang, cuong che is_local=False, con khong de ham tu xac dinh theo --host
    is_local_flag = False if args.remote else None

    run_full_pipeline(
        host=args.host,
        port=args.port,
        results_dir=args.results_dir,
        seed=args.seed,
        is_local=is_local_flag,
    )
