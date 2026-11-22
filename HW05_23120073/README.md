# HW05 – Performance Testing on EShop (MSSV: 23120073)

| Thông tin | Nội dung |
|---|---|
| **Họ và tên sinh viên** | Nguyễn Nam Phước |
| **MSSV** | `23120073` |
| **Mã bài tập** | `HW05-AI` – Performance Testing |
| **Hệ thống kiểm thử (SUT)** | EShop (`backend/server.js` trên `localhost:3000`, giao diện `frontend-admin` trên `localhost:5174`) |
| **Public GitHub Repository** | https://github.com/phuocnguyennam/hw05 |
| **Unlisted YouTube Demo Video** | https://youtu.be/02OU7ZmZcBQ |

---

## 1. Bảng Tự Đánh Giá Điểm Số (Assessment Template — Mục 15)

| No. | Criteria | Grade | Self-Assessed Grade |
|:---:|---|:---:|:---:|
| **1** | Task 1 — Load testing | 30 | **30** |
| **2** | Task 1 — Stress testing | 20 | **20** |
| **3** | Task 1 — Spike testing | 20 | **20** |
| **4** | Task 2 — AI analysis + misinterpretation hunt (with correct values from raw logs) | 10 | **10** |
| **5** | Task 3 — Continuous Performance Testing proposal (G9.6) | 10 | **10** |
| **6** | Agent Skills | 10 | **0** |
| | **Total** | **100** | **90** |

---

## 2. Báo Cáo Tóm Tắt Kiểm Thử (Test Summary Report — Mục 14)

### 2.1. Các nhóm Endpoint được bao phủ (Endpoint Groups Covered)
Luồng kiểm thử end-to-end gồm **4 bước cốt lõi** trên giao diện quản trị `frontend-admin` (**Đăng nhập Admin → Xem danh sách sản phẩm → Import sản phẩm từ file CSV → Tải lại danh sách sản phẩm**), bao phủ đầy đủ 3 nhóm endpoint theo yêu cầu:
1. **Auth-heavy:** `POST /api/login` (`01_Auth_POST_login`) — xác thực tài khoản từ `data/admin_credentials.csv`, kiểm tra điều kiện khoá tài khoản (`locked_until`), ghi `UPDATE users SET login_attempts = 0` và ký chuỗi JWT.
2. **Read-heavy:** `GET /api/products` (`02_Read_GET_products` và `04_Read_GET_products_after_import`) — truy vấn toàn bộ bảng sản phẩm (`SELECT * FROM products`, không phân trang) trước và sau khi import CSV.
3. **Transactional:** `POST /api/admin/import-products` (`03_Txn_POST_import_products`, thực thi ở 20% số phiên) — đọc từng lô 5 sản phẩm từ `data/products_import.csv` (500 dòng) qua `JSR223 PreProcessor` và thực hiện 5 lệnh `INSERT INTO products` mỗi request.

### 2.2. Các kịch bản đã thực thi (Scenarios Run — Ngày 22/11/2026)

| Kịch bản | File Test Plan (`.jmx`) | Loại báo cáo (JMeter Listener) | Cấu hình tải | Samples chính | Throughput TB | Avg / p50 (ms) | p95 / p99 (ms) | Max (ms) | Error % (Số lỗi) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| **1. Load** | [23120073_Load_20261122.jmx](test_plans/23120073_Load_20261122.jmx) | **Aggregate Report** | 20 VU, ramp-up 60s, chạy 600s (think-time 2–8s) | **5.089** | **8,54 req/s** | 296,8 / 229 | **705 / 1.025** | 1.755 | **0,00%** (`0` lỗi) |
| **2. Stress** | [23120073_Stress_20261122.jmx](test_plans/23120073_Stress_20261122.jmx) | **Summary Report** | 5 bậc thang (120s/bậc): 10 → 25 → 50 → 100 → 200 VU (think-time 0,5–1,5s) | **5.263** | **8,42 req/s** | 8.299,8 / 5.021 | **26.698 / 30.003** | 30.020 | **50,29%** (`2.647` lỗi: `2.435` HTTP 200 > 5s + `212` Socket ở 200 VU) |
| **3. Spike** | [23120073_Spike_20261122.jmx](test_plans/23120073_Spike_20261122.jmx) | **Response Time Graph** | Nền 10 VU (360s) + vọt thêm 140 VU trong 5s tại `t = 120s` (đỉnh 150 VU trong 60s) | **2.118** | **5,93 req/s** *(đỉnh: 15,2 req/s)* | 4.172,9 / 234 | **16.345 / 27.539** *(nền & hồi phục: 279–429)* | 30.005 | **31,82%** (`674` lỗi ở đỉnh Spike; **hồi phục về 0,00% lỗi sau 30s**) |

- **File raw logs (`.jtl`):** [results/23120073_Load_20261122.jtl](results/23120073_Load_20261122.jtl), [results/23120073_Stress_20261122.jtl](results/23120073_Stress_20261122.jtl), [results/23120073_Spike_20261122.jtl](results/23120073_Spike_20261122.jtl)
- **Thư mục báo cáo HTML (`reports/`):** [reports/23120073_Load_20261122/index.html](reports/23120073_Load_20261122/index.html), [reports/23120073_Stress_20261122/index.html](reports/23120073_Stress_20261122/index.html), [reports/23120073_Spike_20261122/index.html](reports/23120073_Spike_20261122/index.html)

### 2.3. Ngưỡng chịu tải bền vững trên phần cứng (Endurance Threshold — Máy `PC-ADMIN`, Core i7-1355U, 16 GB RAM)
- **Số người dùng đồng thời ổn định tối đa (Max Stable Concurrency):** **`20 VU`** (với think-time chuẩn 2–8s, `0,00%` lỗi, `p95 = 705 ms`) hoặc **`10–15 VU`** (với think-time ngắn 0,5–1,5s, `0,00%` lỗi, `p95 = 1.067 ms`). Điểm gãy (Knee Point) xuất hiện tại **`25 VU`** (think-time ngắn, `p95 = 4.719 ms`, tỷ lệ lỗi vượt 5s là `3,70%`) và điểm sập kết nối Socket xuất hiện tại **`150–200 VU`**.
- **Thông lượng ổn định tối đa (Maximum Stable RPS & JSON Bandwidth Ceiling):** **`8,54 – 9,20 requests/sec`**, tương đương trần băng thông serialize và truyền dữ liệu JSON **`~10,24 – 11,55 MB/sec`** (khi bảng `products` tích lũy từ `12.800` lên `17.725` sản phẩm, mỗi phản hồi `GET /api/products` nặng `2,40 – 3,15 MB`).
- **Trần bộ nhớ tiến trình Backend (Memory Ceiling của `node.exe`):** **`~371 MB – 420 MB` Working Set** (tăng từ `~73 MB` ban đầu lên `~400 MB` khi giữ bộ đệm chuỗi JSON 3 MB cho các kết nối đồng thời, không xảy ra lỗi tràn bộ nhớ OOM).

### 2.4. Số lượng vấn đề hiệu năng phát hiện được (Number of Performance Issues)
Phát hiện **03 vấn đề hiệu năng cốt lõi** trên SUT (chi tiết tại Mục `1.7` của [Report.md](Report.md)):
1. **Thiếu phân trang ở `GET /api/products`:** Trả về toàn bộ bảng (`SELECT * FROM products`, nặng `2,40 – 3,15 MB/request`), khóa cứng trần thông lượng toàn hệ thống ở mức `~8,5 – 9,2 req/s`.
2. **Chèn từng dòng ngoài Transaction ở `POST /api/admin/import-products`:** Mỗi dòng CSV gọi `stmt.run()` rời rạc không bọc trong `BEGIN...COMMIT`, gây khóa ghi SQLite lặp lại (`p95 = 1.178 ms` ở Load và chạm timeout `30.003 ms` ở Spike/Stress).
3. **Ghi SQLite dư thừa ở `POST /api/login`:** Mọi lần đăng nhập thành công đều chạy lệnh ghi `UPDATE users SET login_attempts = 0` kể cả khi `login_attempts` đã bằng `0`, gây tranh chấp khóa ghi SQLite (`1.146` lỗi quá hạn ở Stress).

### 2.5. Liên kết Video Demo & Tài liệu chính
- **Unlisted YouTube Demo Video ($\ge 6$ phút):** https://youtu.be/02OU7ZmZcBQ ([youtube_link.txt](youtube_link.txt))
- **Báo cáo chính (Task 1, Task 2, Task 3):** [Report.md](Report.md)
- **Nhật ký kiểm toán AI & Phê bình AI (287 từ):** [AI Audit Report.md](AI%20Audit%20Report.md)
- **Lịch sử Git Commit:** [git_commit_log.txt](git_commit_log.txt)
