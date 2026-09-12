"""
gui.py (VM2 - Receiver) - Giao dien PySide6 cho may nhan.

Ho tro 3 thuat toan: Playfair, Caesar, AES-128-CBC.
Hien thi: Trang thai Server, Thong tin goi tin (Thuat toan, Khoa, IV),
Ciphertext, Truc quan hoa (Ma tran / Bang dich / Thong so khoi AES),
Plaintext sau khi giai ma va Nhat ky truyen nhan.
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
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import aes_cbc
import caesar
import config
import playfair
import protocol
from network import ReceiverServer, validate_listen_endpoint


class ReceiverWindow(QMainWindow):
    """Cua so chinh cua ung dung Receiver (VM2)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VM2 - Cryptography Receiver (Playfair / Caesar / AES-128-CBC)")
        self.resize(*config.RECEIVER_WINDOW_SIZE)
        self._server: ReceiverServer | None = None
        self._build_ui()

    # ------------------------------------------------------------- UI
    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        mono = QFont(config.MONO_FONT_FAMILY, config.MONO_FONT_SIZE)

        # --- Nhom dieu khien server ---
        server_group = QGroupBox("TCP Server")
        server_layout = QHBoxLayout(server_group)

        server_layout.addWidget(QLabel("IP lắng nghe:"))
        self.host_edit = QLineEdit(config.DEFAULT_LISTEN_HOST)
        self.host_edit.setToolTip("0.0.0.0 = lắng nghe trên mọi card mạng")
        server_layout.addWidget(self.host_edit)

        server_layout.addWidget(QLabel("Port:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(config.PORT_MIN, config.PORT_MAX)
        self.port_spin.setValue(config.DEFAULT_PORT)
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
        data_group = QGroupBox("Dữ liệu nhận được & Giải mã")
        data_layout = QGridLayout(data_group)

        data_layout.addWidget(QLabel("Thuật toán:"), 0, 0)
        self.algo_view = QLineEdit()
        self.algo_view.setReadOnly(True)
        data_layout.addWidget(self.algo_view, 0, 1)

        data_layout.addWidget(QLabel("Khóa nhận được:"), 1, 0)
        self.key_view = QLineEdit()
        self.key_view.setReadOnly(True)
        data_layout.addWidget(self.key_view, 1, 1)

        data_layout.addWidget(QLabel("Vector IV (AES):"), 2, 0)
        self.iv_view = QLineEdit()
        self.iv_view.setReadOnly(True)
        data_layout.addWidget(self.iv_view, 2, 1)

        data_layout.addWidget(QLabel("Ciphertext:"), 3, 0, Qt.AlignTop)
        self.ciphertext_view = QPlainTextEdit()
        self.ciphertext_view.setReadOnly(True)
        self.ciphertext_view.setFont(mono)
        self.ciphertext_view.setFixedHeight(55)
        data_layout.addWidget(self.ciphertext_view, 3, 1)

        self.visual_label = QLabel("Trực quan hóa:")
        data_layout.addWidget(self.visual_label, 4, 0, Qt.AlignTop)
        self.visual_view = QPlainTextEdit()
        self.visual_view.setReadOnly(True)
        self.visual_view.setFont(mono)
        self.visual_view.setFixedHeight(90)
        data_layout.addWidget(self.visual_view, 4, 1)

        data_layout.addWidget(QLabel("Plaintext giải mã:"), 5, 0, Qt.AlignTop)
        self.plaintext_view = QPlainTextEdit()
        self.plaintext_view.setReadOnly(True)
        self.plaintext_view.setFont(mono)
        self.plaintext_view.setFixedHeight(60)
        data_layout.addWidget(self.plaintext_view, 5, 1)

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
        host = self.host_edit.text().strip() or config.DEFAULT_LISTEN_HOST
        port = self.port_spin.value()

        try:
            validate_listen_endpoint(host, port)
        except ValueError as exc:
            QMessageBox.warning(self, "Cấu hình không hợp lệ", str(exc))
            return

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
        """Nhan goi tin JSON: phan tich thuat toan, khoa, ciphertext va giai ma."""
        try:
            payload = protocol.unpack_message(raw)
        except ValueError as exc:
            self._log(f"LỖI giải gói tin: {exc}")
            return

        algo = payload.get("algorithm", config.ALGORITHM_PLAYFAIR)
        key = payload.get("key", "")
        ciphertext = payload.get("ciphertext", "")
        iv = payload.get("iv", "")
        timestamp = payload.get("timestamp", "?")

        self.algo_view.setText(algo.upper())
        self.key_view.setText(str(key))
        self.iv_view.setText(iv if iv else "(Không dùng)")
        self.ciphertext_view.setPlainText(ciphertext)
        self._log(f"[{timestamp}] Nhận gói tin [{algo}] - Ciphertext: {ciphertext}")

        try:
            if algo == config.ALGORITHM_PLAYFAIR:
                self._decrypt_playfair(key, ciphertext)
            elif algo == config.ALGORITHM_CAESAR:
                self._decrypt_caesar(key, ciphertext)
            elif algo == config.ALGORITHM_AES_128_CBC:
                self._decrypt_aes(key, iv, ciphertext)
            else:
                raise ValueError(f"Thuật toán '{algo}' chưa được hỗ trợ giải mã.")
        except Exception as exc:
            self._log(f"LỖI giải mã [{algo}]: {exc}")
            self.plaintext_view.setPlainText(f"(Không giải mã được: {exc})")

    def _decrypt_playfair(self, key: str, ciphertext: str) -> None:
        matrix = playfair.build_matrix(key)
        plaintext = playfair.decrypt(ciphertext, key)

        self.visual_label.setText("Ma trận Playfair 5×5:")
        self.visual_view.setPlainText(playfair.matrix_to_string(matrix))
        self.plaintext_view.setPlainText(plaintext)
        self._log(f"[Playfair] Plaintext giải mã: {plaintext}")

    def _decrypt_caesar(self, key: str, ciphertext: str) -> None:
        shift = caesar.normalize_shift(key)
        plaintext = caesar.decrypt(ciphertext, shift)

        self.visual_label.setText("Bảng quy tắc dịch Caesar:")
        self.visual_view.setPlainText(caesar.get_mapping_string(shift))
        self.plaintext_view.setPlainText(plaintext)
        self._log(f"[Caesar] Plaintext giải mã (k={shift}): {plaintext}")

    def _decrypt_aes(self, key: str, iv: str, ciphertext: str) -> None:
        key_bytes = aes_cbc.parse_bytes(key, config.AES_KEY_SIZE, "Khóa AES")
        iv_bytes = aes_cbc.parse_bytes(iv, config.AES_BLOCK_SIZE, "Vector IV")
        cipher_bytes = aes_cbc.base64_to_bytes(ciphertext)
        plaintext = aes_cbc.decrypt(cipher_bytes, key_bytes, iv_bytes)

        info_str = aes_cbc.get_aes_info_string(
            key_bytes,
            iv_bytes,
            len(plaintext.encode("utf-8")),
            len(cipher_bytes),
        )
        self.visual_label.setText("Thông số giải mã AES-128-CBC:")
        self.visual_view.setPlainText(info_str)
        self.plaintext_view.setPlainText(plaintext)
        self._log(f"[AES-128-CBC] Plaintext giải mã: {plaintext}")

    def _log(self, line: str) -> None:
        self.log_view.appendPlainText(line)

    def closeEvent(self, event) -> None:
        """Dung server truoc khi dong cua so."""
        if self._server and self._server.isRunning():
            self._server.stop()
            self._server.wait(config.SERVER_STOP_WAIT_MS)
        super().closeEvent(event)
