# Bang Tong hop Ket qua Benchmark Ma hoa Mang

## 1. Ti le thanh cong (Success Rate)

| Thuat toan | Kich thuoc | Tong so luot | Thanh cong | Ti le (%) |
|---|---|---:|---:|---:|
| None | 1 KB | 30 | 30 | 100.0% |
| None | 100 KB | 30 | 30 | 100.0% |
| None | 1 MB | 30 | 30 | 100.0% |
| Caesar | 1 KB | 30 | 30 | 100.0% |
| Caesar | 100 KB | 30 | 30 | 100.0% |
| Caesar | 1 MB | 30 | 30 | 100.0% |
| Playfair | 1 KB | 30 | 30 | 100.0% |
| Playfair | 100 KB | 30 | 30 | 100.0% |
| Playfair | 1 MB | 30 | 30 | 100.0% |
| AES-128-CBC | 1 KB | 30 | 30 | 100.0% |
| AES-128-CBC | 100 KB | 30 | 30 | 100.0% |
| AES-128-CBC | 1 MB | 30 | 30 | 100.0% |

## 2. Chi tiet cac chi so thoi gian va bang thong (Chi tinh tren luot thanh cong)

| Thuat toan | Size | Ciphertext (B) | Packet (B) | Encrypt Mean (ms) | Decrypt Mean (ms) | RTT Mean (ms) | Total Mean (ms) | Total Median (ms) | Throughput (KB/s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| None | 1 KB | 1,024 | 1,024 | 0.00 | 0.00 | 0.08 | 0.08 | 0.07 | 12749.3 |
| None | 100 KB | 102,400 | 102,400 | 0.00 | 0.01 | 0.14 | 0.14 | 0.13 | 739441.6 |
| None | 1 MB | 1,048,576 | 1,048,576 | 0.16 | 0.18 | 1.45 | 1.61 | 1.57 | 637905.8 |
| Caesar | 1 KB | 1,024 | 1,024 | 0.01 | 0.01 | 0.08 | 0.09 | 0.08 | 11856.1 |
| Caesar | 100 KB | 102,400 | 102,400 | 0.07 | 0.07 | 0.22 | 0.29 | 0.30 | 349013.7 |
| Caesar | 1 MB | 1,048,576 | 1,048,576 | 0.72 | 0.75 | 2.55 | 3.27 | 2.65 | 370911.5 |
| Playfair | 1 KB | 1,024 | 1,024 | 1.15 | 1.18 | 1.28 | 2.43 | 2.34 | 414.2 |
| Playfair | 100 KB | 102,400 | 102,400 | 102.75 | 102.26 | 104.06 | 206.81 | 203.80 | 484.5 |
| Playfair | 1 MB | 1,048,576 | 1,048,576 | 1145.20 | 1120.57 | 1124.98 | 2270.18 | 2294.41 | 452.0 |
| AES-128-CBC | 1 KB | 1,040 | 1,056 | 0.02 | 0.02 | 0.11 | 0.13 | 0.12 | 7925.2 |
| AES-128-CBC | 100 KB | 102,416 | 102,432 | 0.10 | 0.05 | 0.21 | 0.30 | 0.30 | 336974.6 |
| AES-128-CBC | 1 MB | 1,048,592 | 1,048,608 | 1.39 | 1.09 | 2.45 | 3.84 | 3.79 | 267264.8 |

## 3. Chi tiet muc su dung CPU va RAM (Chi tinh tren luot thanh cong)

| Thuat toan | Size | Sender CPU (%) | Receiver CPU (%) | Sender RAM (MB) | Receiver RAM (MB) | Sender Delta (KB) | Receiver Delta (KB) |
|---|---|---:|---:|---:|---:|---:|---:|
| None | 1 KB | 0.0% | 0.0% | 104.2 MB | 104.2 MB | 0.0 KB | 0.0 KB |
| None | 100 KB | 0.0% | 0.0% | 104.2 MB | 104.2 MB | 0.0 KB | 0.0 KB |
| None | 1 MB | 0.0% | 0.0% | 108.0 MB | 108.8 MB | 0.0 KB | 0.0 KB |
| Caesar | 1 KB | 0.0% | 0.0% | 104.6 MB | 104.6 MB | 0.0 KB | 0.0 KB |
| Caesar | 100 KB | 0.0% | 0.0% | 104.2 MB | 104.2 MB | 0.0 KB | 0.0 KB |
| Caesar | 1 MB | 0.0% | 0.0% | 108.0 MB | 108.9 MB | 0.0 KB | 0.0 KB |
| Playfair | 1 KB | 0.0% | 0.0% | 103.6 MB | 103.6 MB | 0.0 KB | 0.0 KB |
| Playfair | 100 KB | 95.7% | 96.0% | 102.2 MB | 102.1 MB | 157.7 KB | 103.7 KB |
| Playfair | 1 MB | 98.6% | 98.0% | 108.9 MB | 108.9 MB | 2.8 KB | 83.9 KB |
| AES-128-CBC | 1 KB | 0.0% | 0.0% | 104.6 MB | 104.6 MB | 0.0 KB | 0.0 KB |
| AES-128-CBC | 100 KB | 0.0% | 0.0% | 103.4 MB | 103.4 MB | 0.0 KB | 0.0 KB |
| AES-128-CBC | 1 MB | 6.7% | 6.7% | 110.5 MB | 110.8 MB | 0.0 KB | 0.0 KB |