"""
common.py - Cac tham so, ham sinh du lieu tat dinh va giao thuc truyen tin benchmark.
"""

from __future__ import annotations

import os
import socket
import struct
import sys

# Them thu muc goc vao sys.path de import cac module thuat toan
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENDER_DIR = os.path.join(BASE_DIR, "sender")
RECEIVER_DIR = os.path.join(BASE_DIR, "receiver")

if SENDER_DIR not in sys.path:
    sys.path.insert(0, SENDER_DIR)

import aes_cbc
import caesar
import config
import playfair

# 4 thuat toan danh gia
ALGO_NONE = "None"
ALGO_CAESAR = "Caesar"
ALGO_PLAYFAIR = "Playfair"
ALGO_AES_128_CBC = "AES-128-CBC"
ALGORITHMS = [ALGO_NONE, ALGO_CAESAR, ALGO_PLAYFAIR, ALGO_AES_128_CBC]

# 3 kich thuoc du lieu: 1 KB, 100 KB, 1 MB
SIZE_1KB = 1024
SIZE_100KB = 102400
SIZE_1MB = 1048576
SIZES = [SIZE_1KB, SIZE_100KB, SIZE_1MB]

SIZE_LABELS = {
    SIZE_1KB: "1 KB",
    SIZE_100KB: "100 KB",
    SIZE_1MB: "1 MB",
}

# Tham so ma hoa co dinh
CAESAR_SHIFT = 3
PLAYFAIR_KEY = "MONARCHY"
AES_KEY = b"0123456789abcdef"  # 16 byte khoa doi xung co dinh cho benchmark

# So luot chay
WARMUP_RUNS = 1
BENCHMARK_RUNS = 30
TOTAL_PER_COMBO = WARMUP_RUNS + BENCHMARK_RUNS  # 31
TOTAL_COMBINATIONS = len(ALGORITHMS) * len(SIZES)  # 12
TOTAL_EXECUTIONS = TOTAL_COMBINATIONS * TOTAL_PER_COMBO  # 372
TOTAL_SAMPLES = TOTAL_COMBINATIONS * BENCHMARK_RUNS  # 360

# Dinh dang khung tin TCP (Binary Framing)
# Header: [algo (16B str)] [size_bytes (4B uint)] [run_id (4B uint)] [is_warmup (1B bool)] [packet_len (4B uint)]
HEADER_FORMAT = "!16sII?I"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 29 bytes

# ACK: [decrypt_ms (8B)] [verify_ms (8B)] [success (1B)] [dec_cpu_pct (8B)] [dec_ram_mb (8B)] [dec_ram_delta_kb (8B)]
ACK_FORMAT = "!dd?ddd"
ACK_SIZE = struct.calcsize(ACK_FORMAT)  # 41 bytes


def generate_plaintext(size_bytes: int) -> str:
    """
    Sinh chuoi plaintext tat dinh chi gom cac chu cai in hoa A-Z.
    Su dung bang chu cai 25 ky tu (A-Z, loai tru J de dam bao Playfair khong bi lech ky tu).
    Dam bao khong co hai ky tu giong nhau lien tiep de Playfair khong can chen X.
    """
    pattern = config.ALPHABET  # "ABCDEFGHIKLMNOPQRSTUVWXYZ" (25 ky tu)
    repeat_count = (size_bytes // len(pattern)) + 1
    full_str = pattern * repeat_count
    return full_str[:size_bytes]


def send_all(sock: socket.socket, data: bytes) -> None:
    """Gui toan bo du lieu qua socket."""
    sock.sendall(data)


def recv_all(sock: socket.socket, num_bytes: int) -> bytes:
    """Doc chinh xac num_bytes tu socket."""
    buf = bytearray()
    while len(buf) < num_bytes:
        chunk = sock.recv(num_bytes - len(buf))
        if not chunk:
            raise ConnectionError(f"Socket bi dong dot ngot, con thieu {num_bytes - len(buf)} byte.")
        buf.extend(chunk)
    return bytes(buf)


def send_frame(
    sock: socket.socket,
    algo: str,
    size_bytes: int,
    run_id: int,
    is_warmup: bool,
    packet_data: bytes,
) -> None:
    """Dong goi va gui mot khung du lieu tu Sender den Receiver."""
    algo_bytes = algo.encode("ascii").ljust(16, b"\x00")
    header = struct.pack(
        HEADER_FORMAT,
        algo_bytes,
        size_bytes,
        run_id,
        is_warmup,
        len(packet_data),
    )
    send_all(sock, header + packet_data)


def recv_frame(sock: socket.socket) -> tuple[str, int, int, bool, bytes]:
    """Nhan mot khung du lieu phia Receiver."""
    header_raw = recv_all(sock, HEADER_SIZE)
    algo_raw, size_bytes, run_id, is_warmup, packet_len = struct.unpack(HEADER_FORMAT, header_raw)
    algo = algo_raw.rstrip(b"\x00").decode("ascii")
    packet_data = recv_all(sock, packet_len)
    return algo, size_bytes, run_id, is_warmup, packet_data


def send_ack(
    sock: socket.socket,
    decrypt_ms: float,
    verify_ms: float,
    success: bool,
    dec_cpu_pct: float = 0.0,
    dec_ram_mb: float = 0.0,
    dec_ram_delta_kb: float = 0.0,
) -> None:
    """Gui ACK tu Receiver ve Sender (bao gom ca thoi gian, CPU va RAM cua Receiver)."""
    ack_data = struct.pack(
        ACK_FORMAT,
        decrypt_ms,
        verify_ms,
        success,
        dec_cpu_pct,
        dec_ram_mb,
        dec_ram_delta_kb,
    )
    send_all(sock, ack_data)


def recv_ack(sock: socket.socket) -> tuple[float, float, bool, float, float, float]:
    """Nhan ACK tai Sender (tra ve decrypt_ms, verify_ms, success, dec_cpu_pct, dec_ram_mb, dec_ram_delta_kb)."""
    ack_raw = recv_all(sock, ACK_SIZE)
    decrypt_ms, verify_ms, success, dec_cpu_pct, dec_ram_mb, dec_ram_delta_kb = struct.unpack(
        ACK_FORMAT, ack_raw
    )
    return decrypt_ms, verify_ms, success, dec_cpu_pct, dec_ram_mb, dec_ram_delta_kb
