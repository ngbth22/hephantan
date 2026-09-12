"""
test_gui.py - Kiem thu giao dien PySide6 (SenderWindow va ReceiverWindow).
"""

import importlib
import os
import sys
import unittest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENDER_DIR = os.path.join(BASE_DIR, "sender")
RECEIVER_DIR = os.path.join(BASE_DIR, "receiver")


class TestGUISanity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def _import_sender(self):
        # Don sach cac module da import de tranh xung dot ten (network, gui, config, protocol)
        for mod in ["network", "gui", "config", "protocol", "playfair", "caesar", "aes_cbc"]:
            sys.modules.pop(mod, None)
        if RECEIVER_DIR in sys.path:
            sys.path.remove(RECEIVER_DIR)
        if SENDER_DIR not in sys.path:
            sys.path.insert(0, SENDER_DIR)
        return importlib.import_module("gui").SenderWindow

    def _import_receiver(self):
        for mod in ["network", "gui", "config", "protocol", "playfair", "caesar", "aes_cbc"]:
            sys.modules.pop(mod, None)
        if SENDER_DIR in sys.path:
            sys.path.remove(SENDER_DIR)
        if RECEIVER_DIR not in sys.path:
            sys.path.insert(0, RECEIVER_DIR)
        return importlib.import_module("gui").ReceiverWindow

    def test_sender_window_operations(self):
        SenderWindow = self._import_sender()
        window = SenderWindow()
        self.assertIsNotNone(window)

        # 1. Test Playfair
        window.algo_combo.setCurrentIndex(0)
        window.playfair_key_edit.setText("MONARCHY")
        window.plaintext_edit.setPlainText("HELLOPLAYFAIR")
        window.on_encrypt()
        self.assertTrue(len(window.ciphertext_view.toPlainText().strip()) > 0)
        self.assertIn("M  O  N  A  R", window.visual_view.toPlainText())

        # 2. Test Caesar
        window.algo_combo.setCurrentIndex(1)
        window.caesar_shift_spin.setValue(3)
        window.plaintext_edit.setPlainText("ABC")
        window.on_encrypt()
        self.assertEqual(window.ciphertext_view.toPlainText().strip(), "DEF")
        self.assertIn("k = 3", window.visual_view.toPlainText())

        # 3. Test AES-128-CBC
        window.algo_combo.setCurrentIndex(2)
        window.plaintext_edit.setPlainText("AES Secret Message")
        window.on_encrypt()
        self.assertTrue(len(window.ciphertext_view.toPlainText().strip()) > 0)
        self.assertIn("AES-128-CBC", window.visual_view.toPlainText())

        window.close()

    def test_receiver_window_operations(self):
        ReceiverWindow = self._import_receiver()
        receiver_protocol = sys.modules["protocol"]
        receiver_config = sys.modules["config"]
        receiver_aes = sys.modules["aes_cbc"]

        window = ReceiverWindow()
        self.assertIsNotNone(window)

        # 1. Packet Playfair
        pkt_pf = receiver_protocol.pack_message(
            receiver_config.ALGORITHM_PLAYFAIR, "MONARCHY", "GATLMZCLRQTX"
        )
        window._on_packet(pkt_pf.rstrip(receiver_config.DELIMITER))
        self.assertEqual(window.algo_view.text(), "PLAYFAIR")
        self.assertTrue(len(window.plaintext_view.toPlainText()) > 0)

        # 2. Packet Caesar
        pkt_cs = receiver_protocol.pack_message(
            receiver_config.ALGORITHM_CAESAR, "3", "DEF"
        )
        window._on_packet(pkt_cs.rstrip(receiver_config.DELIMITER))
        self.assertEqual(window.algo_view.text(), "CAESAR")
        self.assertEqual(window.plaintext_view.toPlainText(), "ABC")

        # 3. Packet AES-128-CBC
        key = receiver_aes.generate_key()
        iv = receiver_aes.generate_iv()
        msg = "Bảo mật tuyệt đối"
        c_bytes = receiver_aes.encrypt(msg, key, iv)
        pkt_aes = receiver_protocol.pack_message(
            receiver_config.ALGORITHM_AES_128_CBC,
            receiver_aes.bytes_to_hex(key),
            receiver_aes.bytes_to_base64(c_bytes),
            iv=receiver_aes.bytes_to_hex(iv),
        )
        window._on_packet(pkt_aes.rstrip(receiver_config.DELIMITER))
        self.assertEqual(window.algo_view.text(), "AES-128-CBC")
        self.assertEqual(window.plaintext_view.toPlainText(), msg)

        window.close()


if __name__ == "__main__":
    unittest.main()
