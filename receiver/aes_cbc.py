"""
aes_cbc.py - Trien khai thuat toan ma hoa / giai ma AES-128-CBC voi dem PKCS#7.

Quy uoc:
- Thuat toan: AES (Advanced Encryption Standard).
- Do dai khoa: 128 bit (16 byte).
- Che do ma hoa: CBC (Cipher Block Chaining).
- Vector khoi tao (IV): 128 bit (16 byte), ngau nhien hoac do nguoi dung chi dinh.
- Kieu dem: PKCS#7 (kich thuoc khoi 16 byte = 128 bit).
- Plaintext: chuoi UTF-8 tuy y (ho tro tieng Viet co dau, ky tu dac biet).
- Ciphertext: truyen duoi dang chuoi Base64 hoac Hex tren mang / JSON.
"""

from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

AES_KEY_SIZE = 16   # 128 bit = 16 byte
AES_BLOCK_SIZE = 16  # 128 bit = 16 byte


def generate_key() -> bytes:
    """Sinh khoa ngau nhien an toan co do dai 16 byte (128 bit)."""
    return os.urandom(AES_KEY_SIZE)


def generate_iv() -> bytes:
    """Sinh vector khoi tao (IV) ngau nhien co do dai 16 byte (128 bit)."""
    return os.urandom(AES_BLOCK_SIZE)


def parse_bytes(text: str, expected_len: int = 16, label: str = "Khóa") -> bytes:
    """
    Chuyen doi chuoi nhap lieu thanh bytes.
    Chap nhan:
    - Chuoi Hex (do dai gap doi expected_len, vi du 32 ky tu hex cho 16 byte).
    - Chuoi van ban UTF-8 co do dai dung expected_len byte.
    """
    clean_text = text.strip()
    if not clean_text:
        raise ValueError(f"{label} khong duoc de trong.")

    # Thu giai ma hex neu do dai la 32 ky tu va tat ca la ky tu hex
    if len(clean_text) == expected_len * 2:
        try:
            return bytes.fromhex(clean_text)
        except ValueError:
            pass

    # Thu duoi dang van ban UTF-8
    raw_bytes = clean_text.encode("utf-8")
    if len(raw_bytes) == expected_len:
        return raw_bytes

    raise ValueError(
        f"{label} phai co do dai dung {expected_len} byte "
        f"({expected_len * 2} ky tu Hex hoac {expected_len} ky tu van ban ASCII/UTF-8). "
        f"Do dai hien tai: {len(raw_bytes)} byte."
    )


def bytes_to_hex(data: bytes) -> str:
    """Chuyen bytes sang chuoi Hex."""
    return data.hex()


def hex_to_bytes(hex_str: str) -> bytes:
    """Chuyen chuoi Hex sang bytes."""
    clean = hex_str.strip()
    return bytes.fromhex(clean)


def bytes_to_base64(data: bytes) -> str:
    """Chuyen bytes sang chuoi Base64 UTF-8."""
    return base64.b64encode(data).decode("ascii")


def base64_to_bytes(b64_str: str) -> bytes:
    """Chuyen chuoi Base64 sang bytes."""
    clean = b64_str.strip().encode("ascii")
    return base64.b64decode(clean)


def encrypt(plaintext: str | bytes, key: bytes, iv: bytes) -> bytes:
    """
    Ma hoa plaintext bang AES-128-CBC voi dem PKCS#7.
    Tra ve du lieu nhi phan ciphertext.
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"Khoa AES-128 phai dung {AES_KEY_SIZE} byte, nhan duoc {len(key)} byte.")
    if len(iv) != AES_BLOCK_SIZE:
        raise ValueError(f"Vector IV phai dung {AES_BLOCK_SIZE} byte, nhan duoc {len(iv)} byte.")

    if isinstance(plaintext, str):
        if not plaintext:
            raise ValueError("Plaintext khong duoc de trong.")
        raw_data = plaintext.encode("utf-8")
    else:
        if not plaintext:
            raise ValueError("Plaintext khong duoc de trong.")
        raw_data = plaintext

    # Ap dung dem PKCS#7
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(raw_data) + padder.finalize()

    # Ma hoa AES-128-CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return ciphertext


def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> str:
    """
    Giai ma ciphertext AES-128-CBC va loai bo dem PKCS#7.
    Tra ve chuoi plaintext UTF-8 ban dau.
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"Khoa AES-128 phai dung {AES_KEY_SIZE} byte, nhan duoc {len(key)} byte.")
    if len(iv) != AES_BLOCK_SIZE:
        raise ValueError(f"Vector IV phai dung {AES_BLOCK_SIZE} byte, nhan duoc {len(iv)} byte.")
    if not ciphertext:
        raise ValueError("Ciphertext khong duoc de trong.")
    if len(ciphertext) % AES_BLOCK_SIZE != 0:
        raise ValueError(
            f"Do dai ciphertext ({len(ciphertext)} byte) khong phai boi so cua "
            f"kich thuoc khoi AES ({AES_BLOCK_SIZE} byte)."
        )

    # Giai ma AES-128-CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    try:
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    except Exception as exc:
        raise ValueError(f"Loi giai ma AES: {exc}") from exc

    # Bo dem PKCS#7
    unpadder = padding.PKCS7(128).unpadder()
    try:
        raw_data = unpadder.update(padded_plaintext) + unpadder.finalize()
    except ValueError as exc:
        raise ValueError(
            "Loi giai ma: Dem PKCS#7 khong hop le (sai khoa hoac sai IV)."
        ) from exc

    try:
        return raw_data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Khong the giai ma UTF-8 cho plaintext sau giai ma.") from exc


def get_aes_info_string(key: bytes, iv: bytes, plaintext_len: int, ciphertext_len: int) -> str:
    """Tao chuoi thong tin truc quan ve cac tham so ma hoa AES-128-CBC."""
    num_blocks = ciphertext_len // AES_BLOCK_SIZE if ciphertext_len else 0
    return (
        f"Thuat toan       : AES-128-CBC (PKCS#7)\n"
        f"Khoa (Hex, 16B)  : {bytes_to_hex(key)}\n"
        f"IV   (Hex, 16B)  : {bytes_to_hex(iv)}\n"
        f"Do dai Plaintext : {plaintext_len} byte -> Sau dem: {ciphertext_len} byte ({num_blocks} khoi)"
    )
