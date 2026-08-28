# Tài liệu kỹ thuật hệ thống mã hóa và truyền tin Playfair

**Biên soạn theo khung tài liệu ISO/IEC/IEEE 26514:2022 – Systems and software engineering — Design and development of information for users**

| Thuộc tính tài liệu | Giá trị |
|---|---|
| Tên hệ thống | Playfair Sender/Receiver Demo |
| Phiên bản tài liệu | 2.0 |
| Ngày ban hành | 28/08/2026 |
| Kho mã nguồn | https://github.com/ngbth22/hephantan |

---

## 1. Phạm vi và mục đích tài liệu

Tài liệu này mô tả cấu hình, thiết kế triển khai và đặc tả tham chiếu (reference information) của hệ thống demo mã hóa – truyền tin – giải mã theo thuật toán Playfair giữa hai máy ảo Windows. Theo yêu cầu của ISO/IEC/IEEE 26514:2022 về thông tin hướng đến người dùng, tài liệu cung cấp: (i) thông tin khái quát về hệ thống và cấu hình; (ii) đặc tả từng hàm gồm mục đích, đầu vào, đầu ra, mô tả logic xử lý; (iii) thông tin về xử lý ngoại lệ và thông báo lỗi mà người dùng có thể gặp; (iv) luồng dữ liệu đầy đủ từ Sender đến Receiver.

## 2. Đối tượng sử dụng tài liệu

- **Người vận hành demo**: cần các mục 3, 4, 7 và 8 để cấu hình và chạy hệ thống.
- **Người phát triển / bảo trì**: cần mục 5 và 6 để hiểu đặc tả hàm và cơ chế xử lý ngoại lệ.

## 3. Tổng quan hệ thống

Hệ thống gồm hai ứng dụng độc lập triển khai trên hai máy ảo Windows:

- **VM1 – Sender** (`sender/`): nhập khóa và tin nhắn, sinh ma trận Playfair 5×5, mã hóa, đóng gói JSON và gửi qua TCP.
- **VM2 – Receiver** (`receiver/`): chạy TCP Server, nhận gói tin, giải mã và hiển thị plaintext.

Mỗi ứng dụng được tổ chức thành sáu module: `main.py` (khởi động), `gui.py` (giao diện PySide6), `playfair.py` (thuật toán), `network.py` (TCP), `protocol.py` (định dạng gói tin) và `config.py` (tham số cấu hình tập trung).

Môi trường thực thi: Python 3.12, PySide6, TCP Socket trên Windows.

## 4. Cấu hình hệ thống (`config.py`)

Toàn bộ trọng số cấu hình được tách khỏi mã xử lý và định nghĩa tập trung trong file `config.py` (hiện diện đối xứng ở `sender/` và `receiver/`). Việc thay đổi hành vi hệ thống chỉ cần sửa file này, không sửa mã nghiệp vụ.

### 4.1. Nhóm tham số thuật toán

| Hằng số | Giá trị mặc định | Ý nghĩa |
|---|---|---|
| `ALPHABET` | `"ABCDEFGHIKLMNOPQRSTUVWXYZ"` | Bảng chữ cái 25 ký tự, gộp J vào I |
| `FILLER` | `"X"` | Ký tự đệm cho cặp trùng hoặc độ dài lẻ |
| `MATRIX_SIZE` | `5` | Kích thước ma trận khóa |

### 4.2. Nhóm tham số giao thức

| Hằng số | Giá trị mặc định | Ý nghĩa |
|---|---|---|
| `MESSAGE_TYPE` | `"playfair_message"` | Định danh loại gói tin |
| `PROTOCOL_VERSION` | `1` | Phiên bản giao thức |
| `ENCODING` | `"utf-8"` | Bảng mã hóa byte của JSON |
| `DELIMITER` | `b"\n"` | Ký tự phân tách khung trên luồng TCP |

### 4.3. Nhóm tham số mạng

| Hằng số | Giá trị mặc định | Ý nghĩa |
|---|---|---|
| `DEFAULT_PORT` | `5000` | Cổng TCP mặc định |
| `DEFAULT_RECEIVER_HOST` | `"192.168.1.2"` | IP mặc định của Receiver |
| `DEFAULT_LISTEN_HOST` | `"0.0.0.0"` | IP lắng nghe mặc định (mọi card mạng) |
| `PORT_MIN`, `PORT_MAX` | `1`, `65535` | Khoảng cổng hợp lệ |
| `CONNECT_TIMEOUT` | `5.0` s | Thời gian chờ kết nối phía client |
| `ACCEPT_TIMEOUT` | `0.5` s | Chu kỳ kiểm tra yêu cầu dừng server |
| `CLIENT_RECV_TIMEOUT` | `10.0` s | Thời gian chờ dữ liệu từ một client |
| `RECV_BUFFER` | `4096` byte | Kích thước bộ đệm đọc socket |
| `LISTEN_BACKLOG` | `5` | Hàng đợi kết nối chờ tối đa |
| `SERVER_STOP_WAIT_MS` | `2000` ms | Thời gian chờ server dừng khi thoát |

### 4.4. Nhóm tham số giao diện

| Hằng số | Giá trị mặc định | Ý nghĩa |
|---|---|---|
| `SENDER_WINDOW_SIZE` | `(760, 640)` | Kích thước cửa sổ Sender |
| `RECEIVER_WINDOW_SIZE` | `(760, 680)` | Kích thước cửa sổ Receiver |
| `MONO_FONT_FAMILY`, `MONO_FONT_SIZE` | `"Consolas"`, `11` | Font hiển thị ma trận và log |

## 5. Đặc tả tham chiếu các hàm

Mỗi hàm được đặc tả theo bốn thành phần: **Mục đích**, **Đầu vào** (tên, kiểu, ràng buộc), **Đầu ra**, **Logic xử lý** và **Ngoại lệ** (nếu có).

### 5.1. Module `playfair.py`

#### 5.1.1. `normalize_text(text: str) -> str`

- **Mục đích**: Chuẩn hóa văn bản về dạng hợp lệ với Playfair.
- **Đầu vào**: `text` (`str`) – chuỗi bất kỳ, có thể chứa chữ thường, chữ số, dấu cách, ký tự đặc biệt.
- **Đầu ra**: `str` – chuỗi chỉ gồm ký tự thuộc `ALPHABET` (A–Z, không có J), viết hoa. Có thể là chuỗi rỗng nếu đầu vào không chứa chữ cái nào.
- **Logic xử lý**: Duyệt từng ký tự sau khi viết hoa; ánh xạ `J → I`; giữ lại ký tự thuộc bảng chữ cái 25 ký tự, loại bỏ mọi ký tự khác.
- **Ngoại lệ**: Không phát sinh; đầu vào không hợp lệ được lọc thay vì gây lỗi.

#### 5.1.2. `build_matrix(key: str) -> list[list[str]]`

- **Mục đích**: Sinh ma trận khóa Playfair 5×5.
- **Đầu vào**: `key` (`str`) – khóa do người dùng nhập, được chuẩn hóa nội bộ bằng `normalize_text`.
- **Đầu ra**: `list[list[str]]` – ma trận 5×5 chứa đúng 25 ký tự không trùng lặp.
- **Logic xử lý**: Nối chuỗi khóa đã chuẩn hóa với `ALPHABET`; duyệt tuần tự và giữ lần xuất hiện đầu tiên của mỗi ký tự; cắt danh sách 25 phần tử thành 5 hàng.
- **Ngoại lệ**: Không phát sinh. Khóa rỗng cho ra ma trận bảng chữ cái chuẩn; việc bắt buộc khóa khác rỗng được kiểm soát ở tầng giao diện (mục 5.3.1).

#### 5.1.3. `matrix_to_string(matrix: list[list[str]]) -> str`

- **Mục đích**: Định dạng ma trận thành chuỗi hiển thị trên giao diện.
- **Đầu vào**: `matrix` – ma trận 5×5 do `build_matrix` trả về.
- **Đầu ra**: `str` – 5 dòng, mỗi dòng 5 ký tự phân tách bằng hai dấu cách.
- **Logic xử lý**: Ghép từng hàng bằng `join`, nối các hàng bằng ký tự xuống dòng.
- **Ngoại lệ**: Không phát sinh.

#### 5.1.4. `make_digraphs(text: str) -> list[str]`

- **Mục đích**: Chia văn bản đã chuẩn hóa thành các cặp ký tự (digraph) theo luật Playfair.
- **Đầu vào**: `text` (`str`) – chuỗi đã qua `normalize_text` (chỉ chứa A–Z, không J).
- **Đầu ra**: `list[str]` – danh sách các cặp 2 ký tự; trong mỗi cặp hai ký tự luôn khác nhau.
- **Logic xử lý**: Duyệt hai ký tự liên tiếp: nếu trùng nhau, ghép ký tự thứ nhất với `FILLER` (X) và chỉ tiến 1 vị trí; nếu là ký tự cuối lẻ, ghép với `FILLER`; ngược lại ghép thành cặp bình thường và tiến 2 vị trí.
- **Ngoại lệ**: Không phát sinh; chuỗi rỗng trả về danh sách rỗng.

#### 5.1.5. `encrypt(plaintext: str, key: str) -> str`

- **Mục đích**: Mã hóa plaintext thành ciphertext Playfair.
- **Đầu vào**: `plaintext` (`str`) – tin nhắn gốc, chuỗi bất kỳ; `key` (`str`) – khóa Playfair.
- **Đầu ra**: `str` – ciphertext gồm các ký tự A–Z, độ dài chẵn.
- **Logic xử lý**: Sinh ma trận từ khóa → chuẩn hóa plaintext → chia cặp → với mỗi cặp áp dụng ba quy tắc: cùng hàng dịch phải một cột; cùng cột dịch xuống một hàng; khác hàng khác cột hoán đổi chỉ số cột (quy tắc hình chữ nhật). Phép dịch dùng số học modulo 5 để cuộn vòng mép ma trận.
- **Ngoại lệ**: `ValueError` – khi plaintext sau chuẩn hóa là chuỗi rỗng (không chứa chữ cái nào để mã hóa), kèm thông báo tiếng Việt cho người dùng.

#### 5.1.6. `decrypt(ciphertext: str, key: str) -> str`

- **Mục đích**: Khôi phục plaintext từ ciphertext và khóa.
- **Đầu vào**: `ciphertext` (`str`) – bản mã, kỳ vọng chỉ chứa A–Z và có độ dài chẵn; `key` (`str`) – khóa Playfair trùng với khóa mã hóa.
- **Đầu ra**: `str` – plaintext đã chuẩn hóa (có thể chứa ký tự đệm X theo quy ước thuật toán).
- **Logic xử lý**: Sinh ma trận từ khóa → chuẩn hóa ciphertext → cắt tuần tự thành cặp 2 ký tự → áp dụng phép biến đổi ngược (dịch trái/dịch lên, quy tắc hình chữ nhật giữ nguyên do có tính đối hợp).
- **Ngoại lệ**: `ValueError` – khi ciphertext rỗng hoặc không chứa ký tự hợp lệ; `ValueError` – khi độ dài sau chuẩn hóa là số lẻ (vi phạm bất biến của Playfair, dấu hiệu gói tin hỏng hoặc sai định dạng).

### 5.2. Module `protocol.py`

#### 5.2.1. `pack_message(key: str, ciphertext: str) -> bytes`

- **Mục đích**: Tuần tự hóa dữ liệu ứng dụng thành khung truyền trên TCP.
- **Đầu vào**: `key` (`str`) – khóa Playfair; `ciphertext` (`str`) – bản mã.
- **Đầu ra**: `bytes` – một dòng JSON UTF-8 kết thúc bằng `DELIMITER` (`\n`), gồm các trường `type`, `version`, `key`, `ciphertext`, `timestamp` (ISO 8601).
- **Logic xử lý**: Dựng dictionary theo cấu trúc giao thức (mục 4.2), gắn nhãn thời gian hiện tại, tuần tự hóa bằng `json.dumps`, mã hóa UTF-8 và nối delimiter.
- **Ngoại lệ**: Không phát sinh trong điều kiện sử dụng bình thường (mọi `str` của Python đều tuần tự hóa được sang JSON UTF-8).

#### 5.2.2. `unpack_message(raw: bytes) -> dict`

- **Mục đích**: Giải tuần tự hóa và thẩm định gói tin nhận được trước khi đưa vào giải mã.
- **Đầu vào**: `raw` (`bytes`) – một khung dữ liệu đã tách delimiter, kỳ vọng là JSON UTF-8.
- **Đầu ra**: `dict` – payload chứa tối thiểu các khóa `type`, `key`, `ciphertext`.
- **Logic xử lý**: Giải mã UTF-8 và phân tích JSON; kiểm tra ba điều kiện hợp lệ: (1) kết quả là object JSON, (2) trường `type` bằng `MESSAGE_TYPE`, (3) tồn tại cả `key` và `ciphertext`.
- **Ngoại lệ**: `ValueError` – khi dữ liệu không phải UTF-8 hợp lệ hoặc không phải JSON (bọc `UnicodeDecodeError`/`JSONDecodeError` gốc); `ValueError` – khi sai loại gói tin; `ValueError` – khi thiếu trường bắt buộc. Tầng gọi (Receiver) bắt các ngoại lệ này, ghi log và loại bỏ gói tin thay vì dừng chương trình.

### 5.3. Module `network.py` phía Sender

#### 5.3.1. `validate_endpoint(host: str, port: int) -> None`

- **Mục đích**: Thẩm định địa chỉ đích trước khi mở kết nối, chặn sớm đầu vào không đạt yêu cầu.
- **Đầu vào**: `host` (`str`) – địa chỉ IPv4 dạng chấm; `port` (`int`) – số cổng.
- **Đầu ra**: `None` – hàm chỉ có tác dụng thẩm định; trả về bình thường nghĩa là đầu vào hợp lệ.
- **Logic xử lý**: Kiểm tra chuỗi khác rỗng → phân tích bằng `ipaddress.IPv4Address` (loại trừ các dạng sai như `999.1.1.1`, `abc.def`) → kiểm tra cổng thuộc `[PORT_MIN, PORT_MAX]`.
- **Ngoại lệ**: `ValueError` với thông báo cụ thể cho từng trường hợp: IP rỗng, IP sai định dạng (kèm ví dụ đúng), cổng ngoài khoảng cho phép.

#### 5.3.2. Lớp `SenderThread(QThread)` – phương thức `run() -> None`

- **Mục đích**: Thực hiện phiên gửi TCP trên luồng nền, không chặn giao diện.
- **Đầu vào** (qua hàm khởi tạo): `host` (`str`), `port` (`int`) – địa chỉ Receiver đã qua thẩm định; `packet` (`bytes`) – khung dữ liệu do `pack_message` tạo.
- **Đầu ra**: Không trả về giá trị; kết quả được phát qua tín hiệu Qt: `succeeded(str)` khi gửi xong, `failed(str)` khi lỗi, `log(str)` cho từng bước trung gian.
- **Logic xử lý**: Mở kết nối bằng `socket.create_connection` với thời gian chờ `CONNECT_TIMEOUT` → gửi toàn bộ gói tin bằng `sendall` (bảo đảm không gửi thiếu byte) → đóng kết nối (mô hình client ngắn hạn: một phiên gửi, một kết nối).
- **Ngoại lệ** (bắt nội bộ, chuyển thành tín hiệu `failed` kèm hướng khắc phục):
  - `socket.timeout` – quá thời gian chờ: gợi ý kiểm tra IP, kết nối mạng, firewall của Receiver;
  - `ConnectionRefusedError` – máy đích từ chối kết nối: Receiver chưa khởi động server hoặc sai cổng;
  - `socket.gaierror` – không phân giải được địa chỉ;
  - `OSError` – các lỗi mạng còn lại, kèm mô tả gốc của hệ điều hành.

### 5.4. Module `network.py` phía Receiver

#### 5.4.1. `validate_listen_endpoint(host: str, port: int) -> None`

- **Mục đích**: Thẩm định cấu hình lắng nghe trước khi bind socket.
- **Đầu vào**: `host` (`str`) – địa chỉ IPv4 để lắng nghe (chấp nhận `0.0.0.0`); `port` (`int`) – số cổng.
- **Đầu ra**: `None`; trả về bình thường nghĩa là cấu hình hợp lệ.
- **Logic xử lý**: Tương tự 5.3.1, với gợi ý riêng cho phía server (dùng `0.0.0.0` để lắng nghe trên mọi card mạng).
- **Ngoại lệ**: `ValueError` – IP rỗng, IP sai định dạng, hoặc cổng ngoài khoảng cho phép.

#### 5.4.2. `_describe_bind_error(exc: OSError, host: str, port: int) -> str`

- **Mục đích**: Diễn giải lỗi hệ thống khi bind thành thông báo hành động được cho người dùng.
- **Đầu vào**: `exc` (`OSError`) – ngoại lệ gốc từ `bind`/`listen`; `host`, `port` – cấu hình đang thử.
- **Đầu ra**: `str` – thông báo tiếng Việt kèm hướng khắc phục.
- **Logic xử lý**: Đối chiếu `exc.errno` với hai mã lỗi được xử lý riêng, bao phủ cả mã POSIX và mã Winsock của Windows:
  - `EADDRINUSE` / `WSAEADDRINUSE (10048)` → *cổng đã bị chiếm bởi một phần mềm khác*, đề nghị đóng ứng dụng đang giữ cổng hoặc đổi cổng;
  - `EADDRNOTAVAIL` / `WSAEADDRNOTAVAIL (10049)` → *địa chỉ IP không tồn tại trên máy này*, đề nghị kiểm tra cấu hình mạng hoặc dùng `0.0.0.0`;
  - các mã khác → thông báo chung kèm mô tả gốc.
- **Ngoại lệ**: Không phát sinh.

#### 5.4.3. Lớp `ReceiverServer(QThread)` – phương thức `run() -> None`

- **Mục đích**: Vận hành TCP Server trên luồng nền: lắng nghe, tiếp nhận kết nối, tách khung dữ liệu.
- **Đầu vào** (qua hàm khởi tạo): `host` (`str`), `port` (`int`) – điểm lắng nghe đã qua thẩm định.
- **Đầu ra**: Không trả về giá trị; giao tiếp qua tín hiệu Qt: `started_ok(str)` khi server sẵn sàng, `packet_received(bytes)` cho mỗi khung JSON hoàn chỉnh, `error(str)` khi lỗi, `stopped()` khi kết thúc, `log(str)` cho nhật ký.
- **Logic xử lý**: Tạo socket với `SO_REUSEADDR` → `bind` và `listen` với backlog `LISTEN_BACKLOG` → vòng lặp `accept` có timeout `ACCEPT_TIMEOUT` (cho phép kiểm tra định kỳ cờ dừng do `stop()` đặt, nhờ đó server dừng được một cách có kiểm soát) → với mỗi client, đọc dữ liệu vào bộ đệm và tách khung theo `DELIMITER`; phần dữ liệu chưa trọn khung được giữ lại chờ lần đọc sau (xử lý đúng hiện tượng phân mảnh TCP).
- **Ngoại lệ**:
  - Lỗi khi bind/listen → phát tín hiệu `error` với thông báo của `_describe_bind_error` (mục 5.4.2), luồng kết thúc an toàn;
  - `socket.timeout` trong `accept` → không phải lỗi, dùng làm chu kỳ kiểm tra dừng;
  - `socket.timeout` khi đọc dữ liệu client (quá `CLIENT_RECV_TIMEOUT`) → đóng kết nối client đó, server tiếp tục phục vụ;
  - `OSError` khi nhận dữ liệu → ghi log và đóng kết nối client, không ảnh hưởng server.

#### 5.4.4. `ReceiverServer.stop() -> None`

- **Mục đích**: Yêu cầu dừng server từ luồng giao diện.
- **Đầu vào / Đầu ra**: Không có.
- **Logic xử lý**: Hạ cờ `_running`; vòng lặp `accept` phát hiện cờ trong chu kỳ `ACCEPT_TIMEOUT` kế tiếp, thoát vòng lặp, đóng socket và phát tín hiệu `stopped`.
- **Ngoại lệ**: Không phát sinh.

### 5.5. Module `gui.py` (hai phía)

Các hàm xử lý sự kiện chính được đặc tả tóm lược; chi tiết bố cục giao diện không thuộc phạm vi đặc tả hàm.

#### 5.5.1. `SenderWindow.on_encrypt() -> None`

- **Mục đích**: Xử lý sự kiện "Tạo ma trận & Mã hóa".
- **Đầu vào**: Đọc từ giao diện: khóa (`key_edit`), plaintext (`plaintext_edit`).
- **Đầu ra**: Cập nhật giao diện: ma trận 5×5, ciphertext, nhật ký các bước trung gian (plaintext chuẩn hóa, các cặp ký tự), nhãn trạng thái.
- **Logic xử lý**: Thẩm định khóa chứa ít nhất một chữ cái A–Z → gọi lần lượt `build_matrix`, `normalize_text`, `make_digraphs`, `encrypt` → hiển thị kết quả.
- **Ngoại lệ**: Khóa không đạt yêu cầu hoặc `ValueError` từ tầng thuật toán (ví dụ plaintext không có chữ cái) → hộp thoại cảnh báo, không thay đổi trạng thái hiện có.

#### 5.5.2. `SenderWindow.on_send() -> None`

- **Mục đích**: Xử lý sự kiện "Gửi ciphertext".
- **Đầu vào**: Đọc từ giao diện: khóa, ciphertext (kết quả của 5.5.1), IP và cổng Receiver.
- **Đầu ra**: Khởi chạy `SenderThread`; cập nhật nhãn trạng thái và nhật ký theo tín hiệu trả về; vô hiệu hóa nút gửi trong khi phiên gửi đang chạy.
- **Logic xử lý**: Ba lớp kiểm tra tiền điều kiện: (1) đã có ciphertext, (2) địa chỉ đích hợp lệ qua `validate_endpoint`, (3) không có phiên gửi nào đang chạy → đóng gói bằng `pack_message` → giao cho `SenderThread`.
- **Ngoại lệ**: Vi phạm tiền điều kiện → hộp thoại cảnh báo; lỗi mạng từ `SenderThread` → hộp thoại lỗi kèm nguyên nhân và hướng khắc phục.

#### 5.5.3. `ReceiverWindow.on_start_server() / on_stop_server() -> None`

- **Mục đích**: Khởi động và dừng TCP Server từ giao diện.
- **Đầu vào**: IP lắng nghe, cổng (từ giao diện).
- **Đầu ra**: Chuyển trạng thái các nút điều khiển; cập nhật nhãn trạng thái server.
- **Logic xử lý**: Thẩm định cấu hình bằng `validate_listen_endpoint` trước khi tạo `ReceiverServer`; kết nối các tín hiệu của server vào các hàm cập nhật giao diện; khi dừng, gọi `stop()` và chờ tín hiệu `stopped`.
- **Ngoại lệ**: Cấu hình không hợp lệ → hộp thoại cảnh báo, server không khởi động; lỗi bind (cổng bị chiếm, IP không tồn tại) → nhãn trạng thái và nhật ký hiển thị thông báo diễn giải, các nút điều khiển được khôi phục.

#### 5.5.4. `ReceiverWindow._on_packet(raw: bytes) -> None`

- **Mục đích**: Xử lý một khung dữ liệu hoàn chỉnh do server chuyển lên.
- **Đầu vào**: `raw` (`bytes`) – khung JSON đã tách delimiter.
- **Đầu ra**: Cập nhật giao diện: khóa nhận được, ciphertext, ma trận tái tạo, plaintext giải mã, nhật ký.
- **Logic xử lý**: `unpack_message` thẩm định và trích `key`, `ciphertext` → `build_matrix` và `decrypt` → hiển thị.
- **Ngoại lệ**: Gói tin không hợp lệ (`ValueError` từ `unpack_message`) → ghi log và bỏ qua gói tin; lỗi giải mã (`ValueError` từ `decrypt`, ví dụ ciphertext độ dài lẻ) → ghi log và hiển thị thông báo thay cho plaintext. Cả hai trường hợp đều không làm dừng server.

### 5.6. Module `main.py` (hai phía)

- **Mục đích**: Điểm vào chương trình.
- **Đầu vào**: Tham số dòng lệnh chuẩn của Qt (`sys.argv`).
- **Đầu ra**: Mã thoát tiến trình (`int`).
- **Logic xử lý**: Tạo `QApplication`, khởi tạo cửa sổ tương ứng (`SenderWindow` / `ReceiverWindow`), hiển thị và chạy vòng lặp sự kiện.

## 6. Tổng hợp cơ chế xử lý ngoại lệ

Hệ thống áp dụng nguyên tắc *thẩm định sớm – thất bại có kiểm soát – thông báo hành động được*:

| Tình huống | Điểm phát hiện | Hành vi hệ thống |
|---|---|---|
| Khóa không chứa chữ cái A–Z | `on_encrypt` | Hộp thoại cảnh báo, không mã hóa |
| Plaintext không có chữ cái | `playfair.encrypt` | `ValueError`, hộp thoại cảnh báo |
| IP rỗng / sai định dạng IPv4 | `validate_endpoint` / `validate_listen_endpoint` | `ValueError`, hộp thoại kèm ví dụ đúng |
| Cổng ngoài khoảng 1–65535 | như trên | `ValueError`, hộp thoại cảnh báo |
| Cổng đã bị phần mềm khác chiếm | `bind` phía Receiver | Thông báo diễn giải (EADDRINUSE/10048), đề nghị đổi cổng |
| IP không tồn tại trên máy | `bind` phía Receiver | Thông báo diễn giải (EADDRNOTAVAIL/10049), đề nghị dùng 0.0.0.0 |
| Receiver chưa chạy server | `connect` phía Sender | `ConnectionRefusedError`, gợi ý khởi động server |
| Mạng không thông / firewall chặn | `connect` phía Sender | `socket.timeout` sau 5 s, gợi ý kiểm tra mạng và firewall |
| Gói tin không phải JSON / sai loại / thiếu trường | `unpack_message` | Ghi log, loại bỏ gói tin, server tiếp tục chạy |
| Ciphertext hỏng (độ dài lẻ) | `playfair.decrypt` | Ghi log, hiển thị thông báo thay plaintext |
| Client gửi dở rồi im lặng | timeout đọc 10 s | Đóng kết nối client đó, server tiếp tục phục vụ |

## 7. Luồng dữ liệu từ Sender đến Receiver

**Bước 1 – Thu thập đầu vào (VM1).** Người dùng nhập khóa và tin nhắn trên giao diện Sender.

**Bước 2 – Thẩm định và chuẩn hóa.** Khóa được kiểm tra có chứa chữ cái; plaintext được chuẩn hóa (viết hoa, J→I, loại ký tự ngoài A–Z) và chia thành các cặp ký tự.

**Bước 3 – Mã hóa.** `encrypt` biến đổi từng cặp theo quy tắc Playfair trên ma trận 5×5 sinh từ khóa, cho ra ciphertext.

**Bước 4 – Đóng gói.** `pack_message` tạo khung JSON UTF-8 `{type, version, key, ciphertext, timestamp}` kết thúc bằng `\n`.

**Bước 5 – Thẩm định đích và truyền TCP.** `validate_endpoint` kiểm tra IP/cổng; `SenderThread` mở kết nối (timeout 5 s), gửi trọn khung bằng `sendall` rồi đóng kết nối. Mọi lỗi mạng được phân loại và báo về giao diện.

**Bước 6 – Tiếp nhận (VM2).** `ReceiverServer` đang lắng nghe chấp nhận kết nối, đọc byte vào bộ đệm, tách khung theo `\n` (xử lý đúng phân mảnh TCP) và phát khung hoàn chỉnh lên luồng giao diện.

**Bước 7 – Giải gói và thẩm định.** `unpack_message` phân tích JSON, kiểm tra loại gói tin và các trường bắt buộc; gói tin không hợp lệ bị loại bỏ kèm ghi log.

**Bước 8 – Giải mã và hiển thị.** Receiver tái tạo ma trận từ khóa nhận được, gọi `decrypt`, hiển thị khóa, ciphertext, ma trận, plaintext và nhật ký truyền nhận.

```
VM1 (Sender)                                     VM2 (Receiver)
──────────────────────────────                   ──────────────────────────────
[1] nhập key, plaintext
[2] thẩm định + chuẩn hóa + chia cặp
[3] encrypt → ciphertext
[4] pack_message → JSON + '\n'
[5] validate_endpoint
    SenderThread ── TCP ─────────────────────►   [6] ReceiverServer: accept,
                                                     đọc bộ đệm, tách khung '\n'
                                                 [7] unpack_message: thẩm định,
                                                     lấy key + ciphertext
                                                 [8] build_matrix + decrypt
                                                     → hiển thị plaintext, log
```

## 8. Cấu hình mạng khi triển khai hai máy ảo

1. Đặt hai VM cùng mạng logic (Internal Network / Host-only), gán IP tĩnh cùng dải: VM1 `192.168.1.1`, VM2 `192.168.1.2`.
2. Kiểm tra tầng mạng bằng `ping 192.168.1.2` từ VM1.
3. Kiểm tra tầng vận chuyển sau khi VM2 khởi động server: `Test-NetConnection 192.168.1.2 -Port 5000`.
4. Nếu kết nối bị chặn, mở inbound rule trên VM2:

```powershell
New-NetFirewallRule -DisplayName "Playfair Receiver" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## 9. Giới hạn đã biết

- Khóa được truyền kèm ciphertext trong cùng gói tin nhằm phục vụ demo; mô hình này không bảo đảm an toàn phân phối khóa và không dùng được cho mục đích thực tế.
- Plaintext khôi phục có thể chứa ký tự đệm `X` theo đúng quy ước Playfair; thuật toán chỉ xử lý chữ cái Latin A–Z, không hỗ trợ chữ số, dấu tiếng Việt hay ký tự đặc biệt.
- Ứng dụng thẩm định địa chỉ dạng IPv4; tên miền/hostname không được chấp nhận ở ô nhập địa chỉ.
