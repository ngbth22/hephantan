"""
network.py (VM2 - Receiver) - TCP Server lang nghe va nhan goi tin tu VM1.

Server chay tren QThread rieng, chap nhan nhieu ket noi lan luot.
Moi goi tin JSON ket thuc bang '\n'; du lieu nhan duoc bao ve GUI
thong qua Signal de hien thi va giai ma.

Xu ly ngoai le:
- validate_listen_endpoint(): kiem tra IP lang nghe va cong truoc khi bind.
- Phan biet loi bind thuong gap: cong da bi chiem boi tien trinh khac
  (EADDRINUSE), IP khong ton tai tren may (EADDRNOTAVAIL).
"""

from __future__ import annotations

import errno
import ipaddress
import socket

from PySide6.QtCore import QThread, Signal

from config import (
    ACCEPT_TIMEOUT,
    CLIENT_RECV_TIMEOUT,
    DELIMITER,
    LISTEN_BACKLOG,
    PORT_MAX,
    PORT_MIN,
    RECV_BUFFER,
)

# Ma loi Winsock tuong ung tren Windows
_WSAEADDRINUSE = 10048
_WSAEADDRNOTAVAIL = 10049


def validate_listen_endpoint(host: str, port: int) -> None:
    """Kiem tra tinh hop le cua dia chi IP lang nghe va cong.

    Raises:
        ValueError: neu host khong phai IPv4 hop le hoac port
                    nam ngoai khoang [PORT_MIN, PORT_MAX].
    """
    if not host or not host.strip():
        raise ValueError("Dia chi IP lang nghe khong duoc de trong.")
    try:
        ipaddress.IPv4Address(host.strip())
    except ipaddress.AddressValueError as exc:
        raise ValueError(
            f"'{host}' khong phai la dia chi IPv4 hop le "
            "(dung 0.0.0.0 de lang nghe tren moi card mang)."
        ) from exc
    if not (PORT_MIN <= port <= PORT_MAX):
        raise ValueError(
            f"Cong {port} khong hop le, phai nam trong "
            f"khoang {PORT_MIN}-{PORT_MAX}."
        )


def _describe_bind_error(exc: OSError, host: str, port: int) -> str:
    """Dien giai loi bind thanh thong bao de hieu cho nguoi dung."""
    code = exc.errno
    if code in (errno.EADDRINUSE, _WSAEADDRINUSE):
        return (
            f"Cong {port} da bi chiem boi mot phan mem khac. "
            "Hay dong ung dung dang dung cong nay hoac chon cong khac."
        )
    if code in (errno.EADDRNOTAVAIL, _WSAEADDRNOTAVAIL):
        return (
            f"Dia chi IP {host} khong ton tai tren may nay. "
            "Kiem tra lai cau hinh mang hoac dung 0.0.0.0."
        )
    return f"Khong the mo server tai {host}:{port} - {exc}"


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
            server_sock.listen(LISTEN_BACKLOG)
            server_sock.settimeout(ACCEPT_TIMEOUT)
        except OSError as exc:
            self.error.emit(_describe_bind_error(exc, self._host, self._port))
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
        """Doc du lieu tu mot client, tach goi tin theo dau phan cach."""
        buffer = b""
        client_sock.settimeout(CLIENT_RECV_TIMEOUT)
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
                    while DELIMITER in buffer:
                        line, buffer = buffer.split(DELIMITER, 1)
                        if line.strip():
                            self.log.emit(
                                f"Nhận {len(line)} byte từ {addr[0]}:{addr[1]}"
                            )
                            self.packet_received.emit(line)
        except OSError as exc:
            self.log.emit(f"Lỗi khi nhận dữ liệu từ {addr[0]}: {exc}")
        self.log.emit(f"Đã đóng kết nối với {addr[0]}:{addr[1]}")
