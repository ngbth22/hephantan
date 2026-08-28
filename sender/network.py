"""
network.py (VM1 - Sender) - TCP Client gui goi tin sang VM2.

Viec ket noi va gui du lieu chay tren QThread rieng de khong lam
treo giao dien PySide6. Ket qua duoc bao ve GUI thong qua Signal.

Xu ly ngoai le:
- validate_endpoint(): kiem tra dia chi IP va cong truoc khi ket noi.
- Phan biet cac loi mang thuong gap: bi tu choi ket noi (server chua
  chay / firewall), het thoi gian cho, host khong ton tai.
"""

from __future__ import annotations

import ipaddress
import socket

from PySide6.QtCore import QThread, Signal

from config import CONNECT_TIMEOUT, PORT_MAX, PORT_MIN


def validate_endpoint(host: str, port: int) -> None:
    """Kiem tra tinh hop le cua dia chi IP va cong dich.

    Raises:
        ValueError: neu host rong, khong phai dia chi IPv4 hop le,
                    hoac port nam ngoai khoang [PORT_MIN, PORT_MAX].
    """
    if not host or not host.strip():
        raise ValueError("Dia chi IP cua Receiver khong duoc de trong.")
    try:
        ipaddress.IPv4Address(host.strip())
    except ipaddress.AddressValueError as exc:
        raise ValueError(
            f"'{host}' khong phai la dia chi IPv4 hop le "
            "(vi du dung: 192.168.1.2)."
        ) from exc
    if not (PORT_MIN <= port <= PORT_MAX):
        raise ValueError(
            f"Cong {port} khong hop le, phai nam trong "
            f"khoang {PORT_MIN}-{PORT_MAX}."
        )


class SenderThread(QThread):
    """Ket noi toi Receiver, gui mot goi tin roi dong ket noi."""

    log = Signal(str)
    succeeded = Signal(str)   # thong bao gui thanh cong
    failed = Signal(str)      # thong bao loi

    def __init__(self, host: str, port: int, packet: bytes, parent=None):
        super().__init__(parent)
        self._host = host
        self._port = port
        self._packet = packet

    def run(self) -> None:
        try:
            self.log.emit(f"Dang ket noi toi {self._host}:{self._port} ...")
            with socket.create_connection(
                (self._host, self._port), timeout=CONNECT_TIMEOUT
            ) as sock:
                self.log.emit("Ket noi TCP thanh cong.")
                sock.sendall(self._packet)
                self.log.emit(f"Da gui {len(self._packet)} byte.")
            self.succeeded.emit(
                f"Gui thanh cong toi {self._host}:{self._port}"
            )
        except socket.timeout:
            self.failed.emit(
                f"Het thoi gian cho ({CONNECT_TIMEOUT}s) khi ket noi toi "
                f"{self._host}:{self._port}. Kiem tra IP, ket noi mang "
                "hoac firewall cua Receiver."
            )
        except ConnectionRefusedError:
            self.failed.emit(
                f"{self._host}:{self._port} tu choi ket noi. "
                "Receiver chua khoi dong server hoac sai cong."
            )
        except socket.gaierror as exc:
            self.failed.emit(
                f"Khong phan giai duoc dia chi '{self._host}': {exc}"
            )
        except OSError as exc:
            self.failed.emit(f"Loi mang: {exc}")
