"""
caesar.py - Trien khai thuat toan ma hoa / giai ma Caesar (dich chuyen ky tu).

Quy uoc:
- Khoa la mot so nguyen shift k (vi du k = 3 cho Caesar co dien, k = 13 cho ROT13).
- Phep bien doi duoc thuc hien theo modulo 26 tren cac ky tu chu cai A-Z va a-z.
- Cac ky tu khong phai chu cai (khoang trang, chu so, dau cau) duoc giu nguyen.
"""

from __future__ import annotations

UPPERCASE_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWERCASE_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
ALPHABET_SIZE = 26


def normalize_shift(shift: int | str) -> int:
    """Chuan hoa do dich ve so nguyen hop le trong khoang 0-25."""
    try:
        val = int(shift)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Do dich Caesar phai la so nguyen, nhan duoc '{shift}'.") from exc
    return val % ALPHABET_SIZE


def encrypt(plaintext: str, shift: int | str) -> str:
    """Ma hoa plaintext bang thuat toan Caesar voi do dich shift."""
    if not plaintext:
        raise ValueError("Plaintext khong duoc de trong.")

    k = normalize_shift(shift)
    upper_shifted = UPPERCASE_ALPHABET[k:] + UPPERCASE_ALPHABET[:k]
    lower_shifted = LOWERCASE_ALPHABET[k:] + LOWERCASE_ALPHABET[:k]
    trans_table = str.maketrans(
        UPPERCASE_ALPHABET + LOWERCASE_ALPHABET,
        upper_shifted + lower_shifted,
    )
    return plaintext.translate(trans_table)


def decrypt(ciphertext: str, shift: int | str) -> str:
    """Giai ma ciphertext Caesar bang cach dich nguoc lai do dich shift."""
    if not ciphertext:
        raise ValueError("Ciphertext khong duoc de trong.")

    k = normalize_shift(shift)
    return encrypt(ciphertext, -k)


def get_mapping_string(shift: int | str) -> str:
    """Tao chuoi truc quan hoa bang anh xa dich chuyen chu cai."""
    k = normalize_shift(shift)
    plain_chars = " ".join(UPPERCASE_ALPHABET)
    cipher_chars = " ".join(UPPERCASE_ALPHABET[k:] + UPPERCASE_ALPHABET[:k])
    return (
        f"Goc:  {plain_chars}\n"
        f"Dich: {cipher_chars}  (k = {k})"
    )
