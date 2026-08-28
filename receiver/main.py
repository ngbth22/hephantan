"""
main.py (VM2 - Receiver) - Khoi dong ung dung Playfair Receiver.

Chay: python main.py
"""

import sys

from PySide6.QtWidgets import QApplication

from gui import ReceiverWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = ReceiverWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
