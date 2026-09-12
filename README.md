# Demo mã hóa và truyền tin đa thuật toán (Playfair, Caesar, AES-128-CBC) giữa hai máy ảo Windows

Ứng dụng demo mô phỏng đầy đủ quá trình **mã hóa → truyền tin → giải mã** giữa hai máy ảo Windows với 3 thuật toán mật mã phổ biến:

1. **Playfair Cipher**: Thuật toán mã hóa đa ký tự cổ điển dùng ma trận 5×5.
2. **Caesar Cipher**: Thuật toán mã hóa dịch chuyển cổ điển (hỗ trợ dịch $k$ tùy ý, ROT3, ROT13).
3. **AES-128-CBC**: Chuẩn mã hóa khối hiện đại đối xứng 128-bit với chế độ Cipher Block Chaining (CBC), đệm PKCS#7 và vector khởi tạo IV ngẫu nhiên.

Hệ thống gồm 2 thành phần:
- **VM1 – Sender** (`sender/`): chọn thuật toán, cấu hình khóa/IV, nhập tin nhắn, mã hóa, xem trực quan hóa và gửi gói tin qua TCP.
- **VM2 – Receiver** (`receiver/`): chạy TCP Server lắng nghe, tự động nhận biết thuật toán từ gói tin JSON, giải mã và hiển thị plaintext ban đầu cùng log truyền nhận.

## Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.12 / 3.13 |
| Giao diện | PySide6 (Qt for Python) |
| Mật mã học | `cryptography` (chuẩn công nghiệp cho AES-128-CBC) |
| Truyền tin | TCP Socket (Non-blocking trên QThread) |
| Định dạng gói tin | JSON (newline-delimited UTF-8) |
| Benchmark & Đo đạc | `psutil` (giám sát CPU/RAM), `pandas`, `matplotlib`, `numpy` |

## Cấu trúc dự án

```
hephantan/
├── sender/            # VM1 - máy gửi
│   ├── main.py        # khởi động chương trình Sender
│   ├── gui.py         # giao diện PySide6 hỗ trợ 3 thuật toán
│   ├── playfair.py    # thuật toán mã hóa/giải mã Playfair
│   ├── caesar.py      # thuật toán mã hóa/giải mã Caesar
│   ├── aes_cbc.py     # thuật toán mã hóa/giải mã AES-128-CBC
│   ├── network.py     # TCP Client (chạy trên QThread)
│   ├── protocol.py    # đóng gói / giải gói tin JSON (Version 2)
│   └── config.py      # tham số cấu hình tập trung
├── receiver/          # VM2 - máy nhận
│   ├── main.py        # khởi động chương trình Receiver
│   ├── gui.py         # giao diện PySide6 tự động giải mã đa thuật toán
│   ├── playfair.py    # thuật toán mã hóa/giải mã Playfair
│   ├── caesar.py      # thuật toán mã hóa/giải mã Caesar
│   ├── aes_cbc.py     # thuật toán mã hóa/giải mã AES-128-CBC
│   ├── network.py     # TCP Server (chạy trên QThread)
│   ├── protocol.py    # đóng gói / giải gói tin JSON (Version 2)
│   └── config.py      # tham số cấu hình tập trung
├── benchmark/         # Hệ thống đo đạc hiệu năng mã hóa & truyền mạng
│   ├── run_benchmark.py     # Điều phối toàn bộ quy trình benchmark tự động
│   ├── client.py            # Sender benchmark client
│   ├── server.py            # Receiver benchmark server
│   ├── common.py            # Giao thức framing nhị phân & cấu hình thực nghiệm
│   ├── analyze.py           # Thống kê pandas & vẽ 8 biểu đồ matplotlib
│   └── results/             # Kết quả đo đạc thực nghiệm
│       ├── benchmark_results.csv   # 360 mẫu dữ liệu thô (18 cột)
│       ├── detailed_statistics.csv # Thống kê chi tiết (Mean, Std, Median)
│       ├── summary_table.md        # Bảng tổng hợp Markdown
│       └── charts/                 # 8 biểu đồ phân tích độ phân giải cao 300 DPI
│           ├── 01_encryption_time.png
│           ├── 02_decryption_time.png
│           ├── 03_rtt.png
│           ├── 04_total_time.png
│           ├── 05_sizes.png
│           ├── 06_throughput.png
│           ├── 07_cpu_usage.png
│           └── 08_ram_usage.png
├── tests/             # Bộ kiểm thử tự động toàn diện (27 test cases)
│   ├── test_ciphers.py      # Unit tests cho Playfair, Caesar, AES, Protocol
│   ├── test_integration.py  # Integration tests qua TCP Socket
│   └── test_gui.py          # Kiểm thử giao diện PySide6
├── docs/              # Tài liệu báo cáo kỹ thuật
│   ├── bao-cao-trien-khai.md # Báo cáo kỹ thuật triển khai theo ISO/IEC/IEEE 26514:2022
│   └── bao-cao-benchmark.md  # Báo cáo thực nghiệm hiệu năng & phân tích 8 biểu đồ
├── requirements.txt
└── README.md
```

## Cài đặt (trên cả hai máy ảo)

```powershell
# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

## Chạy chương trình

### 1. Trên VM2 (Receiver) – chạy trước:

```powershell
cd receiver
python main.py
```

- Chọn IP lắng nghe (mặc định `0.0.0.0` – mọi card mạng), Port (mặc định `5000`).
- Bấm **Khởi động Server**.

### 2. Trên VM1 (Sender):

```powershell
cd sender
python main.py
```

- Chọn thuật toán trong danh sách:
  - **Playfair (Ma trận 5×5)**: Nhập khóa (ví dụ `MONARCHY`), nhập tin nhắn, bấm **Tạo ma trận & Mã hóa**.
  - **Caesar (Dịch chuyển)**: Chọn độ dịch $k$ (ví dụ `k = 3` hoặc bấm nút `ROT13`), nhập tin nhắn, bấm **Mã hóa Caesar**.
  - **AES-128-CBC (Mã hóa khối)**: Nhập khóa 16 byte (hoặc bấm **Tạo khóa ngẫu nhiên**), vector IV 16 byte (hoặc bấm **Tạo IV ngẫu nhiên**), nhập tin nhắn, bấm **Mã hóa AES-128-CBC**.
- Nhập **IP của VM2** và Port, bấm **Gửi ciphertext**.

VM2 sẽ tự động nhận gói tin, hiển thị thuật toán tương ứng, khóa, IV, ma trận/thông số giải mã, plaintext giải mã và log chi tiết.

## Chạy kiểm thử tự động

Dự án tích hợp bộ kiểm thử tự động toàn diện:

```powershell
# Chạy toàn bộ 27 test cases
python -m unittest discover -s tests -p "test_*.py"
```

## Định dạng gói tin (protocol.py - Version 2)

Mỗi gói tin là một dòng JSON UTF-8 kết thúc bằng ký tự xuống dòng `\n` (newline-delimited JSON).

### 1. Gói tin Playfair:
```json
{
  "type": "crypto_message",
  "version": 2,
  "algorithm": "playfair",
  "key": "MONARCHY",
  "ciphertext": "GATLMZCLRQTX",
  "timestamp": "2026-09-12T12:30:00"
}
```

### 2. Gói tin Caesar:
```json
{
  "type": "crypto_message",
  "version": 2,
  "algorithm": "caesar",
  "key": "3",
  "ciphertext": "Khoor, Zruog!",
  "timestamp": "2026-09-12T12:30:00"
}
```

### 3. Gói tin AES-128-CBC:
```json
{
  "type": "crypto_message",
  "version": 2,
  "algorithm": "aes-128-cbc",
  "key": "2b7e151628aed2a6abf7158809cf4f3c",
  "iv": "000102030405060708090a0b0c0d0e0f",
  "ciphertext": "mF3bO8k0V29Z1X9L+r4Xgw==",
  "timestamp": "2026-09-12T12:30:00"
}
```

> **Tính tương thích ngược:** Hệ thống vẫn nhận diện và xử lý bình thường các gói tin phiên bản 1 (`"type": "playfair_message"`).

## Quy ước các thuật toán

### 1. Playfair Cipher
- Bảng chữ cái 25 ký tự: gộp **J → I**.
- Chuẩn hóa: viết hoa, loại bỏ ký tự không phải A–Z.
- Cặp trùng ký tự: chèn **X** vào giữa; độ dài lẻ: thêm **X** vào cuối.
- Cùng hàng → dịch phải (mã hóa) / dịch trái (giải mã).
- Cùng cột → dịch xuống (mã hóa) / dịch lên (giải mã).
- Khác hàng khác cột → hoán đổi cột (quy tắc hình chữ nhật).

### 2. Caesar Cipher
- Dịch chuyển theo số học modulo 26: $C = (P + k) \pmod{26}$.
- Hỗ trợ chữ hoa A–Z và chữ thường a–z.
- Giữ nguyên khoảng trắng, chữ số và các ký tự đặc biệt.
- Giải mã: dịch ngược lại theo $-k \pmod{26}$.

### 3. AES-128-CBC
- Độ dài khóa: 128 bit (16 byte). Chấp nhận chuỗi văn bản 16 ký tự hoặc Hex 32 ký tự.
- Kích thước khối: 128 bit (16 byte).
- Vector khởi tạo (IV): 16 byte, truyền kèm trong gói tin (Hex).
- Đệm: PKCS#7 (chuẩn mật mã cho mã hóa khối).
- Plaintext hỗ trợ đầy đủ UTF-8 (tiếng Việt có dấu, ký tự đặc biệt).
- Ciphertext truyền qua mạng dưới dạng Base64.

## Cấu hình mạng giữa hai máy ảo

1. Đặt hai VM cùng một mạng (ví dụ Internal Network / Host-only), gán IP tĩnh cùng dải, ví dụ VM1 = `192.168.1.1`, VM2 = `192.168.1.2`.
2. Kiểm tra kết nối: từ VM1 chạy `ping 192.168.1.2`.
3. Kiểm tra TCP: sau khi VM2 khởi động server, từ VM1 chạy
   `Test-NetConnection 192.168.1.2 -Port 5000`.
4. Mở port trên Windows Firewall của VM2 nếu bị chặn:

```powershell
New-NetFirewallRule -DisplayName "Crypto Receiver" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## Chạy Benchmark Hệ thống (12 tổ hợp × 31 lượt = 372 lượt)

Hệ thống tích hợp sẵn bộ kịch bản đo đạc hiệu năng mạng tự động theo chuẩn thực nghiệm:
- 4 thuật toán: `None`, `Caesar`, `Playfair`, `AES-128-CBC`
- 3 kích thước: `1 KB`, `100 KB`, `1 MB`
- 1 lượt warm-up + 30 lượt đo chính per tổ hợp = 372 lượt thực thi, 360 mẫu phân tích.
- Thu thập toàn diện: Thời gian mã hóa/giải mã, độ trễ RTT, tổng thời gian, thông lượng (throughput), mức chiếm dụng CPU (%) và bộ nhớ RAM (RSS & Delta).

### Cách 1: Tự động toàn bộ (chạy benchmark nội bộ):
```powershell
python benchmark/run_benchmark.py
```
Lệnh sẽ tự động khởi động Receiver ngầm, chạy toàn bộ 372 lượt đo, xuất CSV, tính toán thống kê và vẽ 8 biểu đồ so sánh vào `benchmark/results/charts/`.

### Cách 2: Chạy phân tán trên 2 máy ảo:
- **Trên VM2 (Receiver)**:
  ```powershell
  python benchmark/server.py --host 0.0.0.0 --port 5000
  ```
- **Trên VM1 (Sender)**:
  ```powershell
  python benchmark/client.py --host 192.168.1.2 --port 5000 --output benchmark/results/benchmark_results.csv
  python benchmark/analyze.py --csv benchmark/results/benchmark_results.csv
  ```

---

## Tài liệu kỹ thuật dự án

Toàn bộ tài liệu chi tiết được lưu trữ trong thư mục `docs/` và `benchmark/results/`:

1. [**Báo cáo Triển khai Hệ thống (docs/bao-cao-trien-khai.md)**](docs/bao-cao-trien-khai.md): Báo cáo kỹ thuật chuẩn ISO/IEC/IEEE 26514:2022 về kiến trúc hệ thống, giao thức mạng, đặc tả thuật toán và kiểm thử.
2. [**Báo cáo Thực nghiệm Benchmark (docs/bao-cao-benchmark.md)**](docs/bao-cao-benchmark.md): Báo cáo đầy đủ về kịch bản đo 372 lượt, bảng thống kê thời gian/băng thông/CPU/RAM và phân tích chuyên sâu 8 biểu đồ trực quan.
3. [**Bảng tổng hợp số liệu Benchmark (benchmark/results/summary_table.md)**](benchmark/results/summary_table.md): Bảng số liệu thống kê trung bình và trung vị của toàn bộ 360 mẫu phân tích.
4. [**Thư mục 8 biểu đồ trực quan (benchmark/results/charts/)**](benchmark/results/charts/): Chứa các biểu đồ phân giải cao (300 DPI) về thời gian, RTT, kích thước gói tin, thông lượng, CPU usage và RAM usage.

> **Lưu ý:** Đây là ứng dụng demo phục vụ học tập. Khóa được gửi kèm trong gói tin để VM2 giải mã tự động phục vụ trực quan hóa, điều này không an toàn trong môi trường thực tế nếu chưa kết hợp trao đổi khóa bất đối xứng (như RSA/Diffie-Hellman).
