"""
protocol.py - Dinh dang du lieu truyen giua VM1 (Sender) va VM2 (Receiver).

Format goi tin: JSON UTF-8, ket thuc bang ky tu xuong dong '\\n'
(newline-delimited JSON) de tach cac goi tin tren luong TCP.

Ho tro 3 thuat toan: Playfair, Caesar, AES-128-CBC.

Cau truc goi tin phien ban 2:
{
    "type": "crypto_message",
    "version": 2,
    "algorithm": "playfair" | "caesar" | "aes-128-cbc",
    "key": "<khoa hoac do dich>",
    "iv": "<vector IV 16 byte (hex) neu dung AES-128-CBC>",
    "ciphertext": "<ban ma>",
    "timestamp": "<thoi diem gui, ISO 8601>"
}
"""

from __future__ import annotations

import json
from datetime import datetime

from config import (
    ALGORITHM_AES_128_CBC,
    ALGORITHM_PLAYFAIR,
    DELIMITER,
    ENCODING,
    LEGACY_MESSAGE_TYPE,
    MESSAGE_TYPE,
    PROTOCOL_VERSION,
    SUPPORTED_ALGORITHMS,
)


def pack_message(
    algorithm: str,
    key: str,
    ciphertext: str,
    iv: str = "",
) -> bytes:
    """
    Dong goi thong tin ma hoa thanh goi tin JSON san sang gui qua TCP.

    Args:
        algorithm: 'playfair', 'caesar' hoac 'aes-128-cbc'.
        key: chuoi khoa Playfair, do dich Caesar (so nguyen dang str), hoac khoa AES.
        ciphertext: ban ma (chuoi chu hoa, text, hoac Base64/Hex).
        iv: vector khoi tao (bat buoc doi voi aes-128-cbc).

    Returns:
        Khung byte JSON UTF-8 ket thuc bang ky tu phan tach '\\n'.
    """
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"Thuat toan '{algorithm}' khong duoc ho tro. Ho tro: {SUPPORTED_ALGORITHMS}")

    payload: dict = {
        "type": MESSAGE_TYPE,
        "version": PROTOCOL_VERSION,
        "algorithm": algorithm,
        "key": str(key),
        "ciphertext": ciphertext,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    if iv:
        payload["iv"] = iv

    return json.dumps(payload, ensure_ascii=False).encode(ENCODING) + DELIMITER


def unpack_message(raw: bytes) -> dict:
    """
    Giai ma goi tin JSON nhan duoc, kiem tra tinh hop le va tuong thich nguoc.

    Returns:
        dict chua cac truong du lieu cua goi tin:
        type, version, algorithm, key, ciphertext, (iv neu co), timestamp.
    """
    try:
        payload = json.loads(raw.decode(ENCODING))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Goi tin khong phai JSON hop le: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("Goi tin phai la mot JSON object.")

    msg_type = payload.get("type")
    # Tuong thich nguoc goi tin phien ban 1 (playfair_message)
    if msg_type == LEGACY_MESSAGE_TYPE:
        payload["algorithm"] = ALGORITHM_PLAYFAIR
    elif msg_type != MESSAGE_TYPE:
        raise ValueError(
            f"Goi tin khong dung loai cho phep (nhan '{msg_type}', mong muon '{MESSAGE_TYPE}' hoac '{LEGACY_MESSAGE_TYPE}')."
        )

    algorithm = payload.get("algorithm", ALGORITHM_PLAYFAIR)
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"Thuat toan '{algorithm}' khong nam trong danh muc ho tro: {SUPPORTED_ALGORITHMS}")
    payload["algorithm"] = algorithm

    if "key" not in payload:
        raise ValueError("Goi tin thieu truong 'key'.")
    if "ciphertext" not in payload:
        raise ValueError("Goi tin thieu truong 'ciphertext'.")

    # Kiem tra rieng doi voi AES-128-CBC
    if algorithm == ALGORITHM_AES_128_CBC:
        if not payload.get("iv"):
            raise ValueError("Goi tin AES-128-CBC thieu truong 'iv'.")

    return payload
