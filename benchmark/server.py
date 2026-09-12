"""
server.py - Receiver Benchmark Server.

Chay tren Receiver (VM2):
python benchmark/server.py --host 0.0.0.0 --port 5000
"""

from __future__ import annotations

import argparse
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
    CAESAR_SHIFT,
    PLAYFAIR_KEY,
    generate_plaintext,
    recv_frame,
    send_ack,
)
import aes_cbc
import caesar
import playfair


def handle_client(client_sock: socket.socket, addr: tuple[str, int]) -> None:
    """Xu ly mot phien ket noi benchmark tu Sender."""
    print(f"[*] Ket noi benchmark moi tu {addr[0]}:{addr[1]}")
    count = 0
    try:
        while True:
            try:
                algo, size_bytes, run_id, is_warmup, packet_data = recv_frame(client_sock)
            except (ConnectionError, EOFError, OSError):
                break

            # 1. Do thoi gian giai ma, CPU va RAM
            m_before = proc.memory_info().rss
            p_dec_start = time.process_time()
            t_dec_start = time.perf_counter()
            decryption_success = True
            plain = ""
            try:
                if algo == ALGO_NONE:
                    plain = packet_data.decode("utf-8")
                elif algo == ALGO_CAESAR:
                    plain = caesar.decrypt(packet_data.decode("utf-8"), CAESAR_SHIFT)
                elif algo == ALGO_PLAYFAIR:
                    plain = playfair.decrypt(packet_data.decode("utf-8"), PLAYFAIR_KEY)
                elif algo == ALGO_AES_128_CBC:
                    iv = packet_data[:16]
                    cipher_bytes = packet_data[16:]
                    plain = aes_cbc.decrypt(cipher_bytes, AES_KEY, iv)
                else:
                    decryption_success = False
            except Exception as exc:
                decryption_success = False
                print(f"[!] Loi giai ma {algo} run {run_id}: {exc}")
            t_dec_end = time.perf_counter()
            p_dec_end = time.process_time()
            m_after = proc.memory_info().rss

            decrypt_ms = (t_dec_end - t_dec_start) * 1000.0
            cpu_time_ms = (p_dec_end - p_dec_start) * 1000.0
            dec_cpu_pct = round(min(100.0, (cpu_time_ms / decrypt_ms * 100.0)), 1) if decrypt_ms > 0 else 0.0
            dec_ram_mb = round(m_after / (1024.0 * 1024.0), 2)
            dec_ram_delta_kb = round(max(0.0, (m_after - m_before) / 1024.0), 1)

            # 2. Do thoi gian verify (verify_ms) - so sanh byte-by-byte voi plaintext tai sinh
            t_ver_start = time.perf_counter()
            verify_success = False
            if decryption_success:
                expected_plain = generate_plaintext(size_bytes)
                verify_success = (plain == expected_plain)
            verify_ms = (time.perf_counter() - t_ver_start) * 1000.0

            total_success = decryption_success and verify_success

            # 3. Gui ACK ve Sender (bao gom ca thong so CPU & RAM)
            send_ack(
                client_sock,
                decrypt_ms,
                verify_ms,
                total_success,
                dec_cpu_pct=dec_cpu_pct,
                dec_ram_mb=dec_ram_mb,
                dec_ram_delta_kb=dec_ram_delta_kb,
            )
            count += 1

            label = "WARMUP" if is_warmup else f"RUN {run_id:03d}"
            status = "OK" if total_success else "FAIL"
            if count % 10 == 0 or is_warmup:
                print(
                    f"[{label}] {algo:12s} | {size_bytes:7d}B | "
                    f"Dec: {decrypt_ms:6.2f}ms | CPU: {dec_cpu_pct:4.1f}% | RAM: {dec_ram_mb:4.1f}MB | {status}"
                )
    finally:
        client_sock.close()
        print(f"[*] Dong ket noi voi {addr[0]}:{addr[1]}. Da phuc vu {count} luot.")


def run_server(
    host: str = "0.0.0.0",
    port: int = 5000,
    stop_event: any = None,
    log_callback: any = None,
) -> None:
    """Khoi chay TCP Server lang nghe cac luot benchmark."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(5)
    server_sock.settimeout(0.5)  # Timeout de kiem tra stop_event dinh ky

    msg = f"RECEIVER BENCHMARK SERVER DANG CHAY TAI {host}:{port}"
    print("============================================================")
    print(f"  {msg}")
    print("============================================================")
    if log_callback:
        log_callback(f"[+] {msg}")

    try:
        while True:
            if stop_event and stop_event.is_set():
                break
            try:
                client_sock, addr = server_sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            if log_callback:
                log_callback(f"[*] Ket noi benchmark moi tu {addr[0]}:{addr[1]}")
            handle_client(client_sock, addr)
    except KeyboardInterrupt:
        print("\n[*] Nguoi dung yeu cau dung server.")
    finally:
        server_sock.close()
        if log_callback:
            log_callback("[*] Server da dung lang nghe.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Receiver Benchmark Server")
    parser.add_argument("--host", default="0.0.0.0", help="Dia chi IP lang nghe (mac dinh: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000, help="Cong TCP (mac dinh: 5000)")
    args = parser.parse_args()

    run_server(args.host, args.port)
