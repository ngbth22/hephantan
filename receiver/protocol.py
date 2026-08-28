"""
protocol.py - Dinh dang du lieu truyen giua VM1 (Sender) va VM2 (Receiver).

Format goi tin: JSON UTF-8, ket thuc bang ky tu xuong dong '\n'
(newline-delimited JSON) de tach cac goi tin tren luong TCP.

Cau truc goi tin:
{
    "type": "playfair_message",
    "version": 1,
    "key": "<khoa Playfair>",
    "ciphertext": "<ban ma>",
    "timestamp": "<thoi diem gui, ISO 8601>"
}
"""

from __future__ import annotations

import json
from datetime import datetime

from config import DELIMITER, ENCODING, MESSAGE_TYPE, PROTOCOL_VERSION


def pack_message(key: str, ciphertext: str) -> bytes:
    """Dong goi khoa va ciphertext thanh goi tin JSON san sang gui qua TCP."""
    payload = {
        "type": MESSAGE_TYPE,
        "version": PROTOCOL_VERSION,
        "key": key,
        "ciphertext": ciphertext,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    return json.dumps(payload, ensure_ascii=False).encode(ENCODING) + DELIMITER


def unpack_message(raw: bytes) -> dict:
    """Giai ma goi tin JSON nhan duoc, kiem tra tinh hop le co ban."""
    try:
        payload = json.loads(raw.decode(ENCODING))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Goi tin khong phai JSON hop le: {exc}") from exc

    if not isinstance(payload, dict) or payload.get("type") != MESSAGE_TYPE:
        raise ValueError("Goi tin khong dung dinh dang playfair_message.")
    if "key" not in payload or "ciphertext" not in payload:
        raise ValueError("Goi tin thieu truong 'key' hoac 'ciphertext'.")
    return payload
