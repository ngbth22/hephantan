"""
gui.py (VM2 - Receiver) - Giao dien PySide6 cho may nhan.

Hien thi: trang thai Server, Ciphertext nhan duoc, ma tran Playfair,
Plaintext sau giai ma va log truyen nhan.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import playfair
import protocol
from network import ReceiverServer

DEFAULT_PORT = 5000


class ReceiverWindow(QMainWindow):
    """Cua so chinh cua ung dung Receiver (VM2)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VM2 - Playfair Receiver")
        self.resize(760, 680)
        self._server: ReceiverServer | None = None
        self._build_ui()

    # ------------------------------------------------------------- UI
    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        mono = QFont("Consolas", 11)

        # --- Nhom dieu khien server ---
        server_group = QGroupBox("TCP Server")
        server_layout = QHBoxLayout(server_group)

        server_layout.addWidget(QLabel("IP lắng nghe:"))
        self.host_edit = QLineEdit("0.0.0.0")
        self.host_edit.setToolTip("0.0.0.0 = lắng nghe trên mọi card mạng")
        server_layout.addWidget(self.host_edit)

        server_layout.addWidget(QLabel("Port:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(DEFAULT_PORT)
        server_layout.addWidget(self.port_spin)

        self.start_button = QPushButton("Khởi động Server")
        self.start_button.clicked.connect(self.on_start_server)
        server_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Dừng Server")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.on_stop_server)
        server_layout.addWidget(self.stop_button)

        root.addWidget(server_group)

        self.status_label = QLabel("Trạng thái: Server chưa chạy.")
        root.addWidget(self.status_label)

        # --- Nhom du lieu nhan ---
        data_group = QGroupBox("Dữ liệu nhận được")
        data_layout = QGridLayout(data_group)

        data_layout.addWidget(QLabel("Khóa nhận được:"), 0, 0)
        self.key_view = QLineEdit()
        self.key_view.setReadOnly(True)
        data_layout.addWidget(self.key_view, 0, 1)

        data_layout.addWidget(QLabel("Ciphertext:"), 1, 0, Qt.AlignTop)
        self.ciphertext_view = QPlainTextEdit()
        self.ciphertext_view.setReadOnly(True)
        self.ciphertext_view.setFont(mono)
        self.ciphertext_view.setFixedHeight(60)
        data_layout.addWidget(self.ciphertext_view, 1, 1)

        data_layout.addWidget(QLabel("Ma trận Playfair 5×5:"), 2, 0, Qt.AlignTop)
        self.matrix_view = QPlainTextEdit()
        self.matrix_view.setReadOnly(True)
        self.matrix_view.setFont(mono)
        self.matrix_view.setFixedHeight(110)
        data_layout.addWidget(self.matrix_view, 2, 1)

        data_layout.addWidget(QLabel("Plaintext giải mã:"), 3, 0, Qt.AlignTop)
        self.plaintext_view = QPlainTextEdit()
        self.plaintext_view.setReadOnly(True)
        self.plaintext_view.setFont(mono)
        self.plaintext_view.setFixedHeight(60)
        data_layout.addWidget(self.plaintext_view, 3, 1)

        root.addWidget(data_group)

        # --- Log truyen nhan ---
        log_group = QGroupBox("Log truyền nhận")
        log_layout = QVBoxLayout(log_group)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(mono)
        log_layout.addWidget(self.log_view)
        root.addWidget(log_group, stretch=1)

        self.setCentralWidget(central)

    # -------------------------------------------------------- Handlers
    def on_start_server(self) -> None:
        host = self.host_edit.text().strip() or "0.0.0.0"
        port = self.port_spin.value()

        self._server = ReceiverServer(host, port, parent=self)
        self._server.log.connect(self._log)
        self._server.started_ok.connect(self._on_server_started)
        self._server.packet_received.connect(self._on_packet)
        self._server.error.connect(self._on_server_error)
        self._server.stopped.connect(self._on_server_stopped)
        self._server.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.host_edit.setEnabled(False)
        self.port_spin.setEnabled(False)

    def on_stop_server(self) -> None:
        if self._server:
            self._server.stop()
            self.status_label.setText("Trạng thái: Đang dừng server ...")

    def _on_server_started(self, message: str) -> None:
        self.status_label.setText(f"Trạng thái: {message}")
        self._log(message)

    def _on_server_error(self, message: str) -> None:
        self.status_label.setText(f"Trạng thái: LỖI - {message}")
        self._log(f"LỖI: {message}")
        self._reset_controls()

    def _on_server_stopped(self) -> None:
        self.status_label.setText("Trạng thái: Server đã dừng.")
        self._log("Server đã dừng.")
        self._reset_controls()

    def _reset_controls(self) -> None:
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.host_edit.setEnabled(True)
        self.port_spin.setEnabled(True)

    def _on_packet(self, raw: bytes) -> None:
        """Nhan goi tin JSON: lay khoa + ciphertext, giai ma va hien thi."""
        try:
            payload = protocol.unpack_message(raw)
        except ValueError as exc:
            self._log(f"LỖI giải gói tin: {exc}")
            return

        key = payload["key"]
        ciphertext = payload["ciphertext"]
        timestamp = payload.get("timestamp", "?")

        self.key_view.setText(key)
        self.ciphertext_view.setPlainText(ciphertext)
        self._log(f"[{timestamp}] Ciphertext: {ciphertext}")

        try:
            matrix = playfair.build_matrix(key)
            plaintext = playfair.decrypt(ciphertext, key)
        except ValueError as exc:
            self._log(f"LỖI giải mã Playfair: {exc}")
            self.plaintext_view.setPlainText(f"(Không giải mã được: {exc})")
            return

        self.matrix_view.setPlainText(playfair.matrix_to_string(matrix))
        self.plaintext_view.setPlainText(plaintext)
        self._log(f"Plaintext giải mã: {plaintext}")

    def _log(self, line: str) -> None:
        self.log_view.appendPlainText(line)

    def closeEvent(self, event) -> None:
        """Dung server truoc khi dong cua so."""
        if self._server and self._server.isRunning():
            self._server.stop()
            self._server.wait(2000)
        super().closeEvent(event)
