# Báo cáo triển khai hệ thống mã hóa và truyền tin Playfair

## 1. Mở đầu

Báo cáo này trình bày cấu hình, phương án triển khai và luồng dữ liệu của ứng dụng demo mã hóa – truyền tin – giải mã theo thuật toán Playfair giữa hai máy ảo Windows. Hệ thống được xây dựng nhằm mô phỏng một kênh liên lạc đơn giản trong môi trường phân tán: bên gửi (VM1 – Sender) thực hiện biến đổi mật mã trên plaintext, đóng gói bản mã theo một giao thức thống nhất, rồi chuyển dữ liệu qua mạng TCP tới bên nhận (VM2 – Receiver). Bên nhận khôi phục plaintext từ ciphertext và khóa tương ứng, sau đó hiển thị kết quả trên giao diện.

Mục tiêu của triển khai không phải là xây dựng một kênh mật mã an toàn theo nghĩa mật mã học hiện đại, mà là minh họa đầy đủ các bước xử lý từ lớp ứng dụng đến lớp vận chuyển: chuẩn hóa văn bản, sinh ma trận khóa, mã hóa theo cặp ký tự, đóng gói gói tin và truyền nhận trên socket.

## 2. Cấu hình hệ thống

### 2.1. Cấu hình phần mềm

| Thành phần | Cấu hình triển khai |
|---|---|
| Ngôn ngữ lập trình | Python 3.12 (môi trường kiểm thử nội bộ: Python 3.13) |
| Thư viện giao diện | PySide6 |
| Lớp mạng | TCP Socket (`socket.AF_INET`, `SOCK_STREAM`) |
| Định dạng gói tin | JSON UTF-8, phân tách theo dòng (newline-delimited JSON) |
| Hệ điều hành mục tiêu | Windows, chạy trên hai máy ảo độc lập |

Mỗi máy được tổ chức thành năm module độc lập: `main.py` khởi tạo tiến trình ứng dụng; `gui.py` xây dựng giao diện; `playfair.py` hiện thực thuật toán; `network.py` xử lý TCP; `protocol.py` đóng gói và kiểm tra tính hợp lệ của gói tin.

### 2.2. Cấu hình mạng giữa hai máy ảo

Hai máy ảo được đặt trên cùng một mạng logic (Internal Network hoặc Host-only) và gán địa chỉ IP tĩnh cùng dải, ví dụ:

- VM1 (Sender): `192.168.1.1`
- VM2 (Receiver): `192.168.1.2`
- Cổng dịch vụ: TCP `5000`

Receiver lắng nghe mặc định trên `0.0.0.0:5000`, tức mọi giao diện mạng của VM2. Sender kết nối chủ động tới địa chỉ IP và cổng của Receiver. Thời gian chờ kết nối phía client được cấu hình 5 giây; phía server, vòng lặp `accept` dùng timeout 0,5 giây để có thể dừng tiến trình lắng nghe một cách có kiểm soát.

Trước khi chạy ứng dụng, kênh mạng được kiểm tra bằng ICMP (`ping`) và bằng kiểm tra cổng TCP (`Test-NetConnection`). Nếu hệ thống tường lửa Windows trên VM2 chặn kết nối đến, cần mở inbound rule cho cổng 5000.

### 2.3. Cấu hình giao thức ứng dụng

Gói tin truyền trên TCP có dạng một đối tượng JSON, kết thúc bằng ký tự xuống dòng `\n` để tách khung trên luồng byte. Các trường bắt buộc gồm:

| Trường | Vai trò |
|---|---|
| `type` | Nhận dạng gói tin, giá trị cố định `playfair_message` |
| `version` | Phiên bản giao thức, hiện tại bằng `1` |
| `key` | Khóa Playfair do người dùng nhập tại Sender |
| `ciphertext` | Bản mã sau khi mã hóa |
| `timestamp` | Thời điểm gửi theo ISO 8601 |

Việc gửi kèm khóa trong cùng gói tin cho phép Receiver giải mã tự động trong ngữ cảnh demo. Đây là lựa chọn triển khai phục vụ minh họa luồng xử lý, không phải mô hình phân phối khóa an toàn.

## 3. Triển khai

### 3.1. Thuật toán Playfair (`playfair.py`)

Thuật toán được hiện thực trên bảng chữ cái 25 ký tự, trong đó `J` được ánh xạ về `I`. Ma trận khóa 5×5 được sinh bằng cách điền lần lượt các ký tự duy nhất của khóa, sau đó bổ sung phần còn lại của bảng chữ cái.

Quá trình mã hóa gồm bốn bước: (1) chuẩn hóa văn bản – viết hoa, loại bỏ ký tự ngoài A–Z, thay `J` bằng `I`; (2) chia cặp (digraph) – nếu hai ký tự liên tiếp trùng nhau thì chèn `X`, nếu độ dài lẻ thì thêm `X` vào cuối; (3) tra vị trí từng cặp trên ma trận; (4) biến đổi theo ba quy tắc cổ điển: cùng hàng thì dịch cột, cùng cột thì dịch hàng, còn lại thì hoán đổi cột theo hình chữ nhật. Giải mã dùng cùng ma trận nhưng đảo chiều dịch chuyển.

### 3.2. Lớp giao thức (`protocol.py`)

Module này đóng vai trò biên giới giữa dữ liệu ứng dụng và dữ liệu mạng. Hàm `pack_message` tuần tự hóa khóa, ciphertext và siêu dữ liệu thành một dòng JSON UTF-8. Hàm `unpack_message` thực hiện giải mã JSON, kiểm tra kiểu gói tin và sự hiện diện của các trường bắt buộc. Mọi gói tin không hợp lệ bị loại bỏ tại Receiver trước khi gọi giải mã.

### 3.3. Lớp mạng (`network.py`)

Sender dùng mô hình TCP client ngắn hạn: mở kết nối, gửi toàn bộ gói tin bằng `sendall`, rồi đóng socket. Receiver dùng mô hình TCP server bền vững: bind, listen, chấp nhận lần lượt các kết nối và đọc dữ liệu vào bộ đệm cho đến khi gặp dấu `\n`.

Cả client và server đều chạy trên `QThread` riêng, trao đổi trạng thái với giao diện thông qua tín hiệu Qt (`Signal`). Cách tổ chức này tách I/O mạng khỏi luồng giao diện, tránh làm đóng băng cửa sổ khi chờ kết nối hoặc khi server đang lắng nghe.

### 3.4. Giao diện và khởi động (`gui.py`, `main.py`)

Giao diện Sender cho phép nhập khóa, plaintext, địa chỉ Receiver, đồng thời hiển thị ma trận 5×5, ciphertext, thông tin kết nối và nhật ký gửi. Giao diện Receiver cho phép khởi động hoặc dừng server, đồng thời hiển thị khóa nhận được, ciphertext, ma trận Playfair tái tạo, plaintext sau giải mã và nhật ký truyền nhận. `main.py` chỉ chịu trách nhiệm tạo `QApplication` và mở cửa sổ tương ứng.

## 4. Luồng dữ liệu từ Sender đến Receiver

Luồng xử lý được mô tả tuần tự như sau.

**Bước 1 – Thu thập đầu vào tại VM1.** Người dùng nhập khóa Playfair và nội dung tin nhắn trên giao diện Sender.

**Bước 2 – Chuẩn hóa và sinh ma trận.** Hệ thống chuẩn hóa khóa, xây dựng ma trận 5×5, chuẩn hóa plaintext và chia thành các cặp ký tự. Các kết quả trung gian được hiển thị để đối chiếu.

**Bước 3 – Mã hóa.** Mỗi cặp được biến đổi theo quy tắc Playfair. Chuỗi ciphertext thu được là đầu vào duy nhất của lớp truyền tin, ngoài khóa dùng để giải mã phía nhận.

**Bước 4 – Đóng gói.** `protocol.pack_message` tạo bản ghi JSON gồm `type`, `version`, `key`, `ciphertext` và `timestamp`, rồi mã hóa UTF-8 và gắn delimiter `\n`.

**Bước 5 – Truyền TCP.** `SenderThread` thiết lập kết nối tới IP/port của VM2, gửi toàn bộ khung dữ liệu và đóng kết nối. Trạng thái thành công hoặc lỗi được phản hồi về giao diện Sender.

**Bước 6 – Tiếp nhận tại VM2.** TCP Server đang lắng nghe chấp nhận kết nối, đọc byte vào bộ đệm và tách khung theo `\n`. Gói tin hoàn chỉnh được phát tín hiệu lên luồng giao diện.

**Bước 7 – Giải gói và kiểm tra.** `protocol.unpack_message` khôi phục đối tượng JSON, xác nhận kiểu `playfair_message` và lấy ra `key` cùng `ciphertext`.

**Bước 8 – Giải mã và hiển thị.** Receiver tái tạo ma trận từ khóa nhận được, gọi `playfair.decrypt`, rồi hiển thị ciphertext, ma trận và plaintext trên giao diện, đồng thời ghi nhật ký truyền nhận.

Sơ đồ tóm tắt:

```
VM1 (Sender)
  plaintext, key
       │
       ▼
  chuẩn hóa → ma trận 5×5 → chia cặp → Playfair.encrypt
       │
       ▼
  JSON {type, version, key, ciphertext, timestamp} + '\n'
       │
       ▼
  TCP Client  ──────────────────────────────►  TCP Server
                                               VM2 (Receiver)
                                                    │
                                                    ▼
                                          unpack JSON → lấy key, ciphertext
                                                    │
                                                    ▼
                                          ma trận 5×5 → Playfair.decrypt
                                                    │
                                                    ▼
                                          hiển thị plaintext
```

Như vậy, dữ liệu đi qua bốn lớp xử lý liên tiếp: lớp mật mã, lớp giao thức, lớp vận chuyển TCP và lớp trình bày. Mỗi lớp chỉ phụ thuộc vào đầu ra của lớp liền trước, nên có thể kiểm thử độc lập – từ mã hóa/giải mã vòng tròn trên cùng một máy cho đến truyền nhận đầy đủ giữa hai máy ảo.

## 5. Kết luận

Hệ thống đã được triển khai theo kiến trúc module rõ ràng, với Sender và Receiver đối xứng về thuật toán nhưng bất đối xứng về vai trò mạng (client/server). Cấu hình mạng dựa trên IP tĩnh và cổng TCP cố định; cấu hình phần mềm dựa trên Python, PySide6 và JSON. Luồng dữ liệu từ Sender đến Receiver khép kín các bước mã hóa, đóng gói, truyền tin, giải gói và giải mã, đáp ứng yêu cầu mô phỏng quá trình truyền tin mật giữa hai máy ảo Windows.

Hạn chế cần lưu ý: khóa được gửi cùng ciphertext nên hệ thống chỉ phù hợp cho mục đích minh họa học thuật; plaintext khôi phục có thể chứa ký tự đệm `X` theo đúng quy ước Playfair, và thuật toán chỉ xử lý chữ cái Latin, không mã hóa dấu tiếng Việt hay ký tự đặc biệt.
