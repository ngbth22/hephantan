"""
network.py (VM2 - Receiver) - TCP Server lang nghe va nhan goi tin tu VM1.

Server chay tren QThread rieng, chap nhan nhieu ket noi lan luot.
Moi goi tin JSON ket thuc bang '\n'; du lieu nhan duoc bao ve GUI
thong qua Signal de hien thi va giai ma.
"""

from __future__ import annotations

import socket

from PySide6.QtCore import QThread, Signal

ACCEPT_TIMEOUT = 0.5   # giay - de kiem tra co yeu cau dung server khong
RECV_BUFFER = 4096


class ReceiverServer(QThread):
    """TCP Server: lang nghe, nhan du lieu va phat tin hieu cho GUI."""

    log = Signal(str)
    started_ok = Signal(str)        # server da lang nghe thanh cong
    packet_received = Signal(bytes)  # mot goi tin JSON hoan chinh
    error = Signal(str)
    stopped = Signal()

    def __init__(self, host: str, port: int, parent=None):
        super().__init__(parent)
        self._host = host
        self._port = port
        self._running = False

    def stop(self) -> None:
        """Yeu cau dung server (duoc kiem tra trong vong lap accept)."""
        self._running = False

    def run(self) -> None:
        try:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self._host, self._port))
            server_sock.listen(5)
            server_sock.settimeout(ACCEPT_TIMEOUT)
        except OSError as exc:
            self.error.emit(
                f"Không thể mở server tại {self._host}:{self._port} - {exc}"
            )
            return

        self._running = True
        self.started_ok.emit(
            f"Server đang lắng nghe tại {self._host}:{self._port}"
        )

        try:
            while self._running:
                try:
                    client_sock, addr = server_sock.accept()
                except socket.timeout:
                    continue
                except OSError as exc:
                    self.error.emit(f"Lỗi khi chấp nhận kết nối: {exc}")
                    break

                self.log.emit(f"Kết nối mới từ {addr[0]}:{addr[1]}")
                self._handle_client(client_sock, addr)
        finally:
            server_sock.close()
            self.stopped.emit()

    def _handle_client(self, client_sock: socket.socket, addr) -> None:
        """Doc du lieu tu mot client, tach goi tin theo dau xuong dong."""
        buffer = b""
        client_sock.settimeout(10.0)
        try:
            with client_sock:
                while self._running:
                    try:
                        chunk = client_sock.recv(RECV_BUFFER)
                    except socket.timeout:
                        self.log.emit(f"{addr[0]}: hết thời gian chờ dữ liệu.")
                        break
                    if not chunk:
                        break  # client dong ket noi
                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        if line.strip():
                            self.log.emit(
                                f"Nhận {len(line)} byte từ {addr[0]}:{addr[1]}"
                            )
                            self.packet_received.emit(line)
        except OSError as exc:
            self.log.emit(f"Lỗi khi nhận dữ liệu từ {addr[0]}: {exc}")
        self.log.emit(f"Đã đóng kết nối với {addr[0]}:{addr[1]}")
