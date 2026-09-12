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
| None | 1 KB | 1,024 | 1,024 | 0.00 | 0.00 | 0.08 | 0.09 | 0.07 | 12628.2 |
| None | 100 KB | 102,400 | 102,400 | 0.00 | 0.01 | 0.13 | 0.13 | 0.14 | 792330.5 |
| None | 1 MB | 1,048,576 | 1,048,576 | 0.17 | 0.17 | 1.41 | 1.57 | 1.58 | 653459.0 |
| Caesar | 1 KB | 1,024 | 1,024 | 0.01 | 0.01 | 0.09 | 0.09 | 0.09 | 11798.5 |
| Caesar | 100 KB | 102,400 | 102,400 | 0.06 | 0.06 | 0.18 | 0.24 | 0.23 | 424949.2 |
| Caesar | 1 MB | 1,048,576 | 1,048,576 | 0.72 | 0.76 | 2.42 | 3.15 | 2.67 | 371938.5 |
| Playfair | 1 KB | 1,024 | 1,024 | 1.20 | 1.20 | 1.31 | 2.51 | 2.48 | 399.6 |
| Playfair | 100 KB | 102,400 | 102,400 | 101.84 | 99.61 | 100.88 | 202.71 | 202.28 | 493.9 |
| Playfair | 1 MB | 1,048,576 | 1,048,576 | 1054.82 | 1033.02 | 1034.39 | 2089.21 | 2082.93 | 490.2 |
| AES-128-CBC | 1 KB | 1,040 | 1,056 | 0.04 | 0.02 | 0.16 | 0.20 | 0.14 | 6256.7 |
| AES-128-CBC | 100 KB | 102,416 | 102,432 | 0.10 | 0.05 | 0.23 | 0.33 | 0.27 | 357717.0 |
| AES-128-CBC | 1 MB | 1,048,592 | 1,048,608 | 1.43 | 0.99 | 3.53 | 4.96 | 3.72 | 254892.0 |

## 3. Chi tiet muc su dung CPU va RAM (Chi tinh tren luot thanh cong)

| Thuat toan | Size | Sender CPU (%) | Receiver CPU (%) | Sender RAM (MB) | Receiver RAM (MB) | Sender Delta (KB) | Receiver Delta (KB) |
|---|---|---:|---:|---:|---:|---:|---:|
| None | 1 KB | 0.0% | 0.0% | 102.0 MB | 102.0 MB | 0.0 KB | 0.0 KB |
| None | 100 KB | 0.0% | 0.0% | 102.0 MB | 102.0 MB | 0.0 KB | 0.0 KB |
| None | 1 MB | 0.0% | 0.0% | 105.7 MB | 105.7 MB | 0.0 KB | 0.0 KB |
| Caesar | 1 KB | 0.0% | 0.0% | 102.0 MB | 102.0 MB | 0.0 KB | 0.0 KB |
| Caesar | 100 KB | 0.0% | 0.0% | 102.0 MB | 102.0 MB | 0.0 KB | 0.0 KB |
| Caesar | 1 MB | 6.7% | 0.0% | 105.7 MB | 105.8 MB | 0.0 KB | 0.0 KB |
| Playfair | 1 KB | 0.0% | 0.0% | 101.3 MB | 101.3 MB | 0.0 KB | 0.0 KB |
| Playfair | 100 KB | 95.4% | 97.0% | 100.8 MB | 100.8 MB | 317.5 KB | 139.7 KB |
| Playfair | 1 MB | 97.8% | 98.4% | 106.6 MB | 106.7 MB | 0.0 KB | 80.8 KB |
| AES-128-CBC | 1 KB | 0.0% | 0.0% | 102.3 MB | 102.3 MB | 0.0 KB | 0.1 KB |
| AES-128-CBC | 100 KB | 0.0% | 0.0% | 101.0 MB | 101.0 MB | 0.0 KB | 0.0 KB |
| AES-128-CBC | 1 MB | 6.7% | 0.0% | 107.8 MB | 107.9 MB | 0.0 KB | 0.0 KB |