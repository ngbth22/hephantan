"""
config.py - Tap trung toan bo tham so cau hinh cua ung dung.

Moi hang so cau hinh (thuat toan, giao thuc, mang, giao dien) deu duoc
dinh nghia tai day de cac module khac import, tranh rai rac "magic number".
"""

# ============================== Thuat toan Playfair ==============================
ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # bang chu cai 25 ky tu, gop J vao I
FILLER = "X"                            # ky tu dem cho cap trung / do dai le
MATRIX_SIZE = 5                         # kich thuoc ma tran khoa 5x5

# ============================== Giao thuc truyen tin =============================
MESSAGE_TYPE = "playfair_message"       # dinh danh loai goi tin
PROTOCOL_VERSION = 1                    # phien ban giao thuc
ENCODING = "utf-8"                      # bang ma hoa byte cua goi tin JSON
DELIMITER = b"\n"                       # ky tu phan tach khung tren luong TCP

# ============================== Cau hinh mang ====================================
DEFAULT_PORT = 5000                     # cong TCP mac dinh
DEFAULT_RECEIVER_HOST = "192.168.1.2"   # IP mac dinh cua Receiver (VM2)
DEFAULT_LISTEN_HOST = "0.0.0.0"         # IP lang nghe mac dinh (moi card mang)
PORT_MIN = 1                            # cong nho nhat cho phep
PORT_MAX = 65535                        # cong lon nhat cho phep

CONNECT_TIMEOUT = 5.0                   # (giay) thoi gian cho ket noi phia client
ACCEPT_TIMEOUT = 0.5                    # (giay) chu ky kiem tra dung server
CLIENT_RECV_TIMEOUT = 10.0              # (giay) thoi gian cho du lieu tu 1 client
RECV_BUFFER = 4096                      # (byte) kich thuoc bo dem doc socket
LISTEN_BACKLOG = 5                      # so ket noi cho toi da trong hang doi
SERVER_STOP_WAIT_MS = 2000              # (ms) thoi gian cho server dung khi thoat

# ============================== Giao dien ========================================
SENDER_WINDOW_SIZE = (760, 640)         # (rong, cao) cua so Sender
RECEIVER_WINDOW_SIZE = (760, 680)       # (rong, cao) cua so Receiver
MONO_FONT_FAMILY = "Consolas"           # font hien thi ma tran / log
MONO_FONT_SIZE = 11
