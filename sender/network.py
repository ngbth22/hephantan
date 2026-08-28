"""
network.py (VM1 - Sender) - TCP Client gui goi tin sang VM2.

Viec ket noi va gui du lieu chay tren QThread rieng de khong lam
treo giao dien PySide6. Ket qua duoc bao ve GUI thong qua Signal.
"""

from __future__ import annotations

import socket

from PySide6.QtCore import QThread, Signal

CONNECT_TIMEOUT = 5.0  # giay


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
                f"Het thoi gian cho ({CONNECT_TIMEOUT}s) khi ket noi "
                f"toi {self._host}:{self._port}."
            )
        except OSError as exc:
            self.failed.emit(f"Loi mang: {exc}")
