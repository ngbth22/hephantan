"""
playfair.py - Trien khai thuat toan ma hoa / giai ma Playfair.

Quy uoc:
- Bang chu cai 25 ky tu (A-Z, gop J vao I).
- Ma tran khoa 5x5 duoc sinh tu khoa nguoi dung nhap.
- Chuan hoa plaintext: viet hoa, bo ky tu ngoai A-Z, thay J bang I.
- Chia cap (digraph): cap trung ky tu thi chen 'X' vao giua,
  neu do dai le thi them 'X' vao cuoi.
"""

from __future__ import annotations

ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # khong co J
FILLER = "X"
MATRIX_SIZE = 5


def normalize_text(text: str) -> str:
    """Chuan hoa van ban: viet hoa, thay J->I, loai bo ky tu khong phai A-Z."""
    result = []
    for ch in text.upper():
        if ch == "J":
            ch = "I"
        if ch in ALPHABET:
            result.append(ch)
    return "".join(result)


def build_matrix(key: str) -> list[list[str]]:
    """Tao ma tran Playfair 5x5 tu khoa."""
    normalized_key = normalize_text(key)
    seen: list[str] = []
    for ch in normalized_key + ALPHABET:
        if ch not in seen:
            seen.append(ch)
    return [seen[i * MATRIX_SIZE:(i + 1) * MATRIX_SIZE] for i in range(MATRIX_SIZE)]


def matrix_to_string(matrix: list[list[str]]) -> str:
    """Chuyen ma tran thanh chuoi de hien thi tren GUI."""
    return "\n".join("  ".join(row) for row in matrix)


def _position_map(matrix: list[list[str]]) -> dict[str, tuple[int, int]]:
    return {
        matrix[r][c]: (r, c)
        for r in range(MATRIX_SIZE)
        for c in range(MATRIX_SIZE)
    }


def make_digraphs(text: str) -> list[str]:
    """Chia van ban da chuan hoa thanh cac cap ky tu theo luat Playfair."""
    digraphs: list[str] = []
    i = 0
    while i < len(text):
        a = text[i]
        b = text[i + 1] if i + 1 < len(text) else ""
        if not b:
            digraphs.append(a + FILLER)
            i += 1
        elif a == b:
            digraphs.append(a + FILLER)
            i += 1
        else:
            digraphs.append(a + b)
            i += 2
    return digraphs


def _shift_pair(matrix: list[list[str]], pair: str, direction: int) -> str:
    """Bien doi mot cap ky tu. direction = +1 (ma hoa) hoac -1 (giai ma)."""
    pos = _position_map(matrix)
    (r1, c1), (r2, c2) = pos[pair[0]], pos[pair[1]]

    if r1 == r2:  # cung hang: dich cot
        c1 = (c1 + direction) % MATRIX_SIZE
        c2 = (c2 + direction) % MATRIX_SIZE
    elif c1 == c2:  # cung cot: dich hang
        r1 = (r1 + direction) % MATRIX_SIZE
        r2 = (r2 + direction) % MATRIX_SIZE
    else:  # hinh chu nhat: hoan doi cot
        c1, c2 = c2, c1

    return matrix[r1][c1] + matrix[r2][c2]


def encrypt(plaintext: str, key: str) -> str:
    """Ma hoa plaintext bang khoa Playfair, tra ve ciphertext."""
    matrix = build_matrix(key)
    normalized = normalize_text(plaintext)
    if not normalized:
        raise ValueError("Plaintext khong chua ky tu chu cai nao de ma hoa.")
    digraphs = make_digraphs(normalized)
    return "".join(_shift_pair(matrix, pair, +1) for pair in digraphs)


def decrypt(ciphertext: str, key: str) -> str:
    """Giai ma ciphertext bang khoa Playfair, tra ve plaintext (da chuan hoa)."""
    matrix = build_matrix(key)
    normalized = normalize_text(ciphertext)
    if not normalized:
        raise ValueError("Ciphertext rong hoac khong hop le.")
    if len(normalized) % 2 != 0:
        raise ValueError("Ciphertext Playfair phai co do dai chan.")
    digraphs = [normalized[i:i + 2] for i in range(0, len(normalized), 2)]
    return "".join(_shift_pair(matrix, pair, -1) for pair in digraphs)
