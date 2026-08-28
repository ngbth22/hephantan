"""
gui.py (VM1 - Sender) - Giao dien PySide6 cho may gui.

Hien thi: Key, Plaintext, ma tran Playfair 5x5, Ciphertext,
thong tin ket noi (IP/Port cua Receiver) va trang thai gui.
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

import playfair
import protocol
from network import SenderThread

DEFAULT_PORT = 5000


class SenderWindow(QMainWindow):
    """Cua so chinh cua ung dung Sender (VM1)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VM1 - Playfair Sender")
        self.resize(760, 640)
        self._sender_thread: SenderThread | None = None
        self._build_ui()

    # ------------------------------------------------------------- UI
    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)

        # --- Nhom nhap lieu ---
        input_group = QGroupBox("Dữ liệu đầu vào")
        input_layout = QGridLayout(input_group)

        input_layout.addWidget(QLabel("Khóa Playfair:"), 0, 0)
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("Ví dụ: MONARCHY")
        input_layout.addWidget(self.key_edit, 0, 1)

        input_layout.addWidget(QLabel("Plaintext:"), 1, 0, Qt.AlignTop)
        self.plaintext_edit = QPlainTextEdit()
        self.plaintext_edit.setPlaceholderText("Nhập nội dung tin nhắn...")
        self.plaintext_edit.setFixedHeight(80)
        input_layout.addWidget(self.plaintext_edit, 1, 1)

        self.encrypt_button = QPushButton("Tạo ma trận && Mã hóa")
        self.encrypt_button.clicked.connect(self.on_encrypt)
        input_layout.addWidget(self.encrypt_button, 2, 1, Qt.AlignRight)

        root.addWidget(input_group)

        # --- Nhom ket qua ma hoa ---
        result_group = QGroupBox("Kết quả mã hóa")
        result_layout = QGridLayout(result_group)
        mono = QFont("Consolas", 11)

        result_layout.addWidget(QLabel("Ma trận Playfair 5×5:"), 0, 0, Qt.AlignTop)
        self.matrix_view = QPlainTextEdit()
        self.matrix_view.setReadOnly(True)
        self.matrix_view.setFont(mono)
        self.matrix_view.setFixedHeight(110)
        result_layout.addWidget(self.matrix_view, 0, 1)

        result_layout.addWidget(QLabel("Ciphertext:"), 1, 0, Qt.AlignTop)
        self.ciphertext_view = QPlainTextEdit()
        self.ciphertext_view.setReadOnly(True)
        self.ciphertext_view.setFont(mono)
        self.ciphertext_view.setFixedHeight(70)
        result_layout.addWidget(self.ciphertext_view, 1, 1)

        root.addWidget(result_group)

        # --- Nhom ket noi ---
        conn_group = QGroupBox("Kết nối tới Receiver (VM2)")
        conn_layout = QHBoxLayout(conn_group)

        conn_layout.addWidget(QLabel("IP Receiver:"))
        self.host_edit = QLineEdit("192.168.1.2")
        conn_layout.addWidget(self.host_edit)

        conn_layout.addWidget(QLabel("Port:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(DEFAULT_PORT)
        conn_layout.addWidget(self.port_spin)

        self.send_button = QPushButton("Gửi ciphertext")
        self.send_button.clicked.connect(self.on_send)
        conn_layout.addWidget(self.send_button)

        root.addWidget(conn_group)

        # --- Trang thai / log ---
        status_group = QGroupBox("Trạng thái gửi")
        status_layout = QVBoxLayout(status_group)
        self.status_label = QLabel("Chưa gửi.")
        status_layout.addWidget(self.status_label)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(mono)
        status_layout.addWidget(self.log_view)
        root.addWidget(status_group, stretch=1)

        self.setCentralWidget(central)

    # -------------------------------------------------------- Handlers
    def on_encrypt(self) -> None:
        """Tao ma tran, chuan hoa, chia cap va ma hoa plaintext."""
        key = self.key_edit.text().strip()
        plaintext = self.plaintext_edit.toPlainText()

        if not playfair.normalize_text(key):
            QMessageBox.warning(self, "Thiếu khóa",
                                "Khóa phải chứa ít nhất một chữ cái A-Z.")
            return

        try:
            matrix = playfair.build_matrix(key)
            normalized = playfair.normalize_text(plaintext)
            digraphs = playfair.make_digraphs(normalized)
            ciphertext = playfair.encrypt(plaintext, key)
        except ValueError as exc:
            QMessageBox.warning(self, "Không thể mã hóa", str(exc))
            return

        self.matrix_view.setPlainText(playfair.matrix_to_string(matrix))
        self.ciphertext_view.setPlainText(ciphertext)
        self._log(f"Plaintext chuẩn hóa : {normalized}")
        self._log(f"Chia cặp ký tự      : {' '.join(digraphs)}")
        self._log(f"Ciphertext          : {ciphertext}")
        self.status_label.setText("Đã mã hóa xong, sẵn sàng gửi.")

    def on_send(self) -> None:
        """Dong goi JSON va gui ciphertext sang VM2 qua TCP."""
        key = self.key_edit.text().strip()
        ciphertext = self.ciphertext_view.toPlainText().strip()
        host = self.host_edit.text().strip()
        port = self.port_spin.value()

        if not ciphertext:
            QMessageBox.warning(self, "Chưa có ciphertext",
                                "Hãy bấm 'Tạo ma trận & Mã hóa' trước khi gửi.")
            return
        if not host:
            QMessageBox.warning(self, "Thiếu IP",
                                "Hãy nhập địa chỉ IP của Receiver (VM2).")
            return
        if self._sender_thread and self._sender_thread.isRunning():
            QMessageBox.information(self, "Đang gửi",
                                    "Đang có một phiên gửi, vui lòng đợi.")
            return

        packet = protocol.pack_message(key, ciphertext)
        self._log(f"Gói tin JSON: {packet.decode('utf-8').strip()}")

        self.send_button.setEnabled(False)
        self.status_label.setText(f"Đang gửi tới {host}:{port} ...")

        self._sender_thread = SenderThread(host, port, packet, parent=self)
        self._sender_thread.log.connect(self._log)
        self._sender_thread.succeeded.connect(self._on_send_success)
        self._sender_thread.failed.connect(self._on_send_failure)
        self._sender_thread.finished.connect(
            lambda: self.send_button.setEnabled(True)
        )
        self._sender_thread.start()

    def _on_send_success(self, message: str) -> None:
        self.status_label.setText(message)
        self._log(message)

    def _on_send_failure(self, message: str) -> None:
        self.status_label.setText(f"Lỗi: {message}")
        self._log(f"LỖI: {message}")
        QMessageBox.critical(self, "Gửi thất bại", message)

    def _log(self, line: str) -> None:
        self.log_view.appendPlainText(line)
