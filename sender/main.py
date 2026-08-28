"""
main.py (VM1 - Sender) - Khoi dong ung dung Playfair Sender.

Chay: python main.py
"""

import sys

from PySide6.QtWidgets import QApplication

from gui import SenderWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = SenderWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
