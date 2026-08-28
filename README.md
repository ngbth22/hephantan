# Demo mã hóa và truyền tin Playfair giữa hai máy ảo Windows

Ứng dụng demo mô phỏng đầy đủ quá trình **mã hóa → truyền tin → giải mã** bằng
thuật toán **Playfair** giữa hai máy ảo Windows:

- **VM1 – Sender** (`sender/`): nhập khóa và tin nhắn, tạo ma trận Playfair 5×5,
  chuẩn hóa, chia cặp ký tự, mã hóa và gửi ciphertext qua TCP.
- **VM2 – Receiver** (`receiver/`): chạy TCP Server lắng nghe, nhận gói tin,
  giải mã Playfair và hiển thị plaintext ban đầu.

## Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.12 |
| Giao diện | PySide6 (Qt for Python) |
| Truyền tin | TCP Socket |
| Định dạng gói tin | JSON (newline-delimited) |

## Cấu trúc dự án

```
hephantan/
├── sender/            # VM1 - máy gửi
│   ├── main.py        # khởi động chương trình
│   ├── gui.py         # giao diện PySide6
│   ├── playfair.py    # thuật toán mã hóa/giải mã Playfair
│   ├── network.py     # TCP Client (chạy trên QThread)
│   ├── protocol.py    # đóng gói / giải gói tin JSON
│   └── config.py      # tham số cấu hình tập trung
├── receiver/          # VM2 - máy nhận
│   ├── main.py
│   ├── gui.py
│   ├── playfair.py
│   ├── network.py     # TCP Server (chạy trên QThread)
│   ├── protocol.py
│   └── config.py
├── requirements.txt
└── README.md
```

## Cài đặt (trên cả hai máy ảo)

```powershell
# Yêu cầu Python 3.12 đã cài sẵn
pip install -r requirements.txt
```

## Chạy chương trình

**Trên VM2 (Receiver) – chạy trước:**

```powershell
cd receiver
python main.py
```

Chọn IP lắng nghe (mặc định `0.0.0.0` – mọi card mạng), Port (mặc định `5000`)
rồi bấm **Khởi động Server**.

**Trên VM1 (Sender):**

```powershell
cd sender
python main.py
```

1. Nhập **Khóa Playfair** (ví dụ `MONARCHY`) và **Plaintext**.
2. Bấm **Tạo ma trận & Mã hóa** → xem ma trận 5×5 và ciphertext.
3. Nhập **IP của VM2** và Port, bấm **Gửi ciphertext**.

VM2 sẽ nhận gói tin, hiển thị ciphertext, ma trận Playfair, plaintext sau
giải mã và log truyền nhận.

## Định dạng gói tin (protocol.py)

```json
{
  "type": "playfair_message",
  "version": 1,
  "key": "MONARCHY",
  "ciphertext": "GATLMZCLRQTX",
  "timestamp": "2026-08-28T14:30:00"
}
```

Mỗi gói tin là một dòng JSON UTF-8 kết thúc bằng ký tự xuống dòng `\n`.

## Quy ước thuật toán Playfair

- Bảng chữ cái 25 ký tự: gộp **J → I**.
- Chuẩn hóa: viết hoa, loại bỏ ký tự không phải A–Z.
- Cặp trùng ký tự: chèn **X** vào giữa; độ dài lẻ: thêm **X** vào cuối.
- Cùng hàng → dịch phải (mã hóa) / dịch trái (giải mã).
- Cùng cột → dịch xuống (mã hóa) / dịch lên (giải mã).
- Hình chữ nhật → hoán đổi cột.

## Cấu hình mạng giữa hai máy ảo

1. Đặt hai VM cùng một mạng (ví dụ Internal Network / Host-only), gán IP tĩnh
   cùng dải, ví dụ VM1 = `192.168.1.1`, VM2 = `192.168.1.2`.
2. Kiểm tra kết nối: từ VM1 chạy `ping 192.168.1.2`.
3. Kiểm tra TCP: sau khi VM2 khởi động server, từ VM1 chạy
   `Test-NetConnection 192.168.1.2 -Port 5000`.
4. Nếu không kết nối được, mở port trên Windows Firewall của VM2:

```powershell
New-NetFirewallRule -DisplayName "Playfair Receiver" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## Luồng hoạt động tổng thể

```
VM1 nhập tin nhắn → Playfair mã hóa → tạo ciphertext
    → TCP truyền qua mạng → VM2 nhận ciphertext
    → Playfair giải mã → hiển thị plaintext
```

> **Lưu ý:** Đây là ứng dụng demo phục vụ học tập. Khóa được gửi kèm trong gói
> tin để VM2 giải mã tự động, điều này không an toàn trong thực tế.
