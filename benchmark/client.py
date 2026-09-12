"""
client.py - Sender Benchmark Client.

Chay tren Sender (VM1):
python benchmark/client.py --host 192.168.1.2 --port 5000 --output benchmark/results/benchmark_results.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import socket
import sys
import time

import psutil

proc = psutil.Process()

from common import (
    AES_KEY,
    ALGO_AES_128_CBC,
    ALGO_CAESAR,
    ALGO_NONE,
    ALGO_PLAYFAIR,
    ALGORITHMS,
    BENCHMARK_RUNS,
    CAESAR_SHIFT,
    PLAYFAIR_KEY,
    SIZES,
    WARMUP_RUNS,
    generate_plaintext,
    recv_ack,
    send_frame,
)
import aes_cbc
import caesar
import playfair


def run_benchmark(
    host: str = "127.0.0.1",
    port: int = 5000,
    output_csv: str = "benchmark/results/benchmark_results.csv",
    seed: int | None = 42,
) -> str:
    """
    Thuc hien toan bo kich ban benchmark:
    - 12 to hop (4 thuat toan x 3 size)
    - Tron ngau nhien thu tu 12 to hop MOT LAN DUY NHAT bang random.shuffle()
    - Moi to hop: 1 warm-up + 30 lan do chinh
    - Ghi ket qua 360 mau vao CSV
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)

    # 1. Tao danh sach 12 to hop va shuffle mot lan duy nhat
    combinations = [(algo, sz) for algo in ALGORITHMS for sz in SIZES]
    if seed is not None:
        random.seed(seed)
    random.shuffle(combinations)

    print("============================================================")
    print("  KHOI DONG BENCHMARK MA HOA MANG SENDER -> RECEIVER")
    print(f"  Dich den: {host}:{port}")
    print(f"  Tong to hop: {len(combinations)} | Warm-up/to hop: {WARMUP_RUNS} | Mau/to hop: {BENCHMARK_RUNS}")
    print(f"  Tong thuc thi: {len(combinations) * (WARMUP_RUNS + BENCHMARK_RUNS)} luot (372 luot)")
    print(f"  Mau phan tich: {len(combinations) * BENCHMARK_RUNS} mau (360 mau)")
    print("============================================================")
    print("Thu tu chay 12 to hop sau khi shuffle:")
    for idx, (algo, sz) in enumerate(combinations, 1):
        print(f"  {idx:02d}. {algo:12s} - {sz // 1024:4d} KB ({sz} B)")
    print("------------------------------------------------------------")

    # 2. Ket noi toi Receiver
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    # Bat TCP_NODELAY de giam do tre framing
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    csv_rows = []
    run_id_counter = 1

    try:
        total_combo = len(combinations)
        for c_idx, (algo, size_bytes) in enumerate(combinations, 1):
            print(f"\n>>> [To hop {c_idx:02d}/{total_combo:02d}] {algo} - {size_bytes} Byte")

            # A. Warm-up run (loai khoi thong ke)
            for w_idx in range(WARMUP_RUNS):
                plain = generate_plaintext(size_bytes)
                if algo == ALGO_NONE:
                    cipher_bytes = plain.encode("utf-8")
                    packet_bytes = cipher_bytes
                elif algo == ALGO_CAESAR:
                    cipher_str = caesar.encrypt(plain, CAESAR_SHIFT)
                    cipher_bytes = cipher_str.encode("utf-8")
                    packet_bytes = cipher_bytes
                elif algo == ALGO_PLAYFAIR:
                    cipher_str = playfair.encrypt(plain, PLAYFAIR_KEY)
                    cipher_bytes = cipher_str.encode("utf-8")
                    packet_bytes = cipher_bytes
                elif algo == ALGO_AES_128_CBC:
                    iv = os.urandom(16)
                    cipher_bytes = aes_cbc.encrypt(plain, AES_KEY, iv)
                    packet_bytes = iv + cipher_bytes

                send_frame(sock, algo, size_bytes, 0, True, packet_bytes)
                recv_ack(sock)
                print(f"    [Warm-up OK] Da chay xong 1 luot khoi dong cho {algo} {size_bytes}B")

            # B. 30 lan do chinh
            for m_idx in range(1, BENCHMARK_RUNS + 1):
                plain = generate_plaintext(size_bytes)

                # 1. Do thoi gian ma hoa (encryption_ms), CPU va RAM
                m_before = proc.memory_info().rss
                p_enc_start = time.process_time()
                t_enc_start = time.perf_counter()
                if algo == ALGO_NONE:
                    # None: khong ma hoa, chi lay byte UTF-8
                    cipher_bytes = plain.encode("utf-8")
                    packet_bytes = cipher_bytes
                elif algo == ALGO_CAESAR:
                    cipher_str = caesar.encrypt(plain, CAESAR_SHIFT)
                    cipher_bytes = cipher_str.encode("utf-8")
                    packet_bytes = cipher_bytes
                elif algo == ALGO_PLAYFAIR:
                    cipher_str = playfair.encrypt(plain, PLAYFAIR_KEY)
                    cipher_bytes = cipher_str.encode("utf-8")
                    packet_bytes = cipher_bytes
                elif algo == ALGO_AES_128_CBC:
                    iv = os.urandom(16)
                    cipher_bytes = aes_cbc.encrypt(plain, AES_KEY, iv)
                    packet_bytes = iv + cipher_bytes
                else:
                    raise ValueError(f"Thuat toan khong hop le: {algo}")

                t_enc_end = time.perf_counter()
                p_enc_end = time.process_time()
                m_after = proc.memory_info().rss

                encryption_ms = (t_enc_end - t_enc_start) * 1000.0
                cpu_time_ms = (p_enc_end - p_enc_start) * 1000.0
                enc_cpu_pct = round(min(100.0, (cpu_time_ms / encryption_ms * 100.0)), 1) if encryption_ms > 0 else 0.0
                enc_ram_mb = round(m_after / (1024.0 * 1024.0), 2)
                enc_ram_delta_kb = round(max(0.0, (m_after - m_before) / 1024.0), 1)

                ciphertext_size_bytes = len(cipher_bytes)
                packet_size_bytes = len(packet_bytes)

                # 2. Gui packet va cho ACK -> rtt_ms = t(nhan ACK) - t(gui)
                t_send = time.perf_counter()
                send_frame(sock, algo, size_bytes, run_id_counter, False, packet_bytes)
                (
                    decrypt_ms,
                    verify_ms,
                    success,
                    dec_cpu_pct,
                    dec_ram_mb,
                    dec_ram_delta_kb,
                ) = recv_ack(sock)
                t_ack = time.perf_counter()

                rtt_ms = (t_ack - t_send) * 1000.0

                # 3. Cong thuc duy nhat: total_ms = encryption_ms + rtt_ms
                total_ms = encryption_ms + rtt_ms
                throughput_kbps = (size_bytes / 1024.0) / (total_ms / 1000.0) if total_ms > 0 else 0.0

                row = {
                    "run_id": run_id_counter,
                    "algorithm": algo,
                    "size_bytes": size_bytes,
                    "ciphertext_size_bytes": ciphertext_size_bytes,
                    "packet_size_bytes": packet_size_bytes,
                    "encryption_ms": round(encryption_ms, 4),
                    "decrypt_ms": round(decrypt_ms, 4),
                    "verify_ms": round(verify_ms, 4),
                    "rtt_ms": round(rtt_ms, 4),
                    "total_ms": round(total_ms, 4),
                    "throughput_kbps": round(throughput_kbps, 2),
                    "enc_cpu_pct": enc_cpu_pct,
                    "dec_cpu_pct": round(dec_cpu_pct, 1),
                    "enc_ram_mb": enc_ram_mb,
                    "dec_ram_mb": round(dec_ram_mb, 2),
                    "enc_ram_delta_kb": enc_ram_delta_kb,
                    "dec_ram_delta_kb": round(dec_ram_delta_kb, 1),
                    "success": success,
                }
                csv_rows.append(row)

                if m_idx % 10 == 0 or m_idx == BENCHMARK_RUNS:
                    print(
                        f"    Run {m_idx:02d}/30 (ID:{run_id_counter:03d}) | "
                        f"Enc: {encryption_ms:6.2f}ms | Dec: {decrypt_ms:6.2f}ms | "
                        f"RTT: {rtt_ms:6.2f}ms | Tot: {total_ms:6.2f}ms | "
                        f"CPU: {enc_cpu_pct:4.1f}%/{dec_cpu_pct:4.1f}% | "
                        f"RAM: {enc_ram_mb:4.1f}M/{dec_ram_mb:4.1f}M | "
                        f"TP: {throughput_kbps:8.1f} KB/s | Success: {success}"
                    )

                run_id_counter += 1

    finally:
        sock.close()

    # 3. Ghi ket qua vao CSV theo dung schema yeu cau
    fieldnames = [
        "run_id",
        "algorithm",
        "size_bytes",
        "ciphertext_size_bytes",
        "packet_size_bytes",
        "encryption_ms",
        "decrypt_ms",
        "verify_ms",
        "rtt_ms",
        "total_ms",
        "throughput_kbps",
        "enc_cpu_pct",
        "dec_cpu_pct",
        "enc_ram_mb",
        "dec_ram_mb",
        "enc_ram_delta_kb",
        "dec_ram_delta_kb",
        "success",
    ]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print("------------------------------------------------------------")
    print(f"[+] Hoan tat benchmark! Da luu {len(csv_rows)} mau vao: {output_csv}")
    return output_csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sender Benchmark Client")
    parser.add_argument("--host", default="127.0.0.1", help="Dia chi IP cua Receiver (mac dinh: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Cong TCP cua Receiver (mac dinh: 5000)")
    parser.add_argument(
        "--output",
        default="benchmark/results/benchmark_results.csv",
        help="Duong dan file CSV xuat ket qua",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed ngau nhien cho shuffle (mac dinh: 42)")
    args = parser.parse_args()

    run_benchmark(args.host, args.port, args.output, args.seed)
