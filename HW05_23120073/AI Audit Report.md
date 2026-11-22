# BÁO CÁO PHÊ BÌNH AI & NHẬT KÝ KIỂM TOÁN AI (AI CRITIQUE & AI AUDIT REPORT — HW05)

> **Họ và tên sinh viên:** Nguyễn Nam Phước — **MSSV:** `23120073`  
> **Mã bài tập:** `HW05-AI` (Performance Testing)  
> **Phạm vi kiểm thử (Scope):** Luồng quản trị trên `frontend-admin`: **Đăng nhập Admin (`POST /api/login`) → Xem danh sách sản phẩm (`GET /api/products`) → Import sản phẩm từ file CSV (`POST /api/admin/import-products`)**  
> **Hệ thống & Phần cứng thực thi:** EShop Backend (`node server.js` trên `localhost:3000`), Máy `PC-ADMIN` (Intel Core i7-1355U, 16 GB RAM, Windows 11)

---

## 1. Khai báo Công cụ và Cấp độ Bloom-AI (Allowed Tools and Bloom-AI Level — Mục 8)

Theo quy định tại Mục 8 của đề bài, các công cụ được sử dụng trong bài tập này bao gồm:
- **Công cụ kiểm thử hiệu năng:** Apache JMeter 5.6.3 (chạy trên OpenJDK 17.0.21) với 3 loại Listener khác nhau: `Aggregate Report` (Load), `Summary Report` (Stress), `Response Time Graph` (Spike).
- **Công cụ AI:** Antigravity AI Agent (Claude / Google Gemini) — hỗ trợ thiết kế kịch bản `.jmx` theo từng bước, sinh dữ liệu CSV, phân tích log `.jtl`, đề xuất tối ưu và thiết kế mô hình Continuous Performance Testing.
- **Công cụ giám sát tài nguyên & phần cứng:** Windows Task Manager (giám sát CPU & RAM của tiến trình `Node.js JavaScript Runtime` – `node.exe`) và DirectX Diagnostic Tool (`dxdiag`).
- **Cấp độ năng lực Bloom-AI đạt được:** **G9.2 (Apply)**, **G9.3 (Analyse)**, **G9.4 (Collaborate)** và **G9.6 (Disrupt)**.

---

## 2. Phê bình AI (AI Critique — Mandatory, 200–300 Words — Mục 10)

<!-- CRITIQUE_START -->
Trong bài tập kiểm thử hiệu năng HW05 cho luồng Đăng nhập Admin, Xem danh sách sản phẩm và Import CSV, công cụ AI đã bộc lộ những sai sót, thiên lệch và thiếu sót ở cả khâu thiết kế kịch bản lẫn phân tích log. Khi thiết kế kịch bản JMeter ban đầu, AI sao chép máy móc toàn bộ hàm tải dữ liệu của trang quản trị, đưa thêm bốn API dư thừa gồm người dùng, đơn hàng, danh mục và mã giảm giá khiến kịch bản phình lên mười hai bước; đồng thời giả định sai rằng hệ thống gửi file CSV dạng multipart và khóa tài khoản sau ba lần sai, trong khi mã nguồn gửi mảng JSON và cộng hai điểm phạt mỗi lần sai. Khi phân tích kết quả và đề xuất tối ưu, AI dễ đọc nhầm đơn vị thông lượng theo phút thành theo giây, đánh đồng lỗi vượt ngưỡng năm giây mã HTTP 200 với lỗi sập máy chủ, cũng như đề xuất ảo giác về việc dùng Connection Pool cho SQLite đơn file hay tối ưu hàm băm bcrypt dù code so sánh mật khẩu văn bản thuần. Nguyên nhân cốt lõi là do AI suy luận theo các mẫu kiến trúc phổ biến mà không tự đối chiếu với mã nguồn thực tế và hiện tượng bảng sản phẩm phình to không phân trang. Qua bài tập này, nguyên tắc quan trọng nhất tôi rút ra khi cộng tác với AI là: luôn coi AI là trợ lý cần kiểm chứng, chủ động đọc mã nguồn để cắt bỏ chi tiết thừa và luôn đối chiếu mọi nhận định của AI với dữ liệu log thô.
<!-- CRITIQUE_END -->

---

## 3. Nhật ký Kiểm toán AI (AI Audit Report — Mandatory Appendix — Mục 9)

**Tuyên bố sử dụng AI (Mandatory Declaration):**  
> *"I use AI tools for the following tasks,"*

### 3.1. Bảng Tóm tắt Các Tương tác với Công cụ AI

| STT | Tên công cụ AI (`Name of the AI tool`) | Ngày & Giờ (`Date and time`) | Nhiệm vụ áp dụng (`Task`) | Mức độ Bloom-AI |
|:---:|----------------------------------------|:----------------------------:|---------------------------|:---------------:|
| **1** | Antigravity AI Agent (Claude / Gemini) | `2026-11-21 14:16` | Phân tích đề bài HW05, khảo sát mã nguồn `backend/server.js` & `frontend-admin/src/App.jsx` và lập kế hoạch thực hiện cho luồng `Đăng nhập Admin -> Xem danh sách sản phẩm -> Import CSV` | `G9.2 (Apply)` |
| **2** | Antigravity AI Agent (Claude / Gemini) | `2026-11-21 14:27` | Thiết kế tham số kiểm thử, sinh 2 file dữ liệu CSV (`admin_credentials.csv`, `products_import.csv`) và tạo 3 file kịch bản JMeter (`Load`, `Stress`, `Spike`) kèm kiểm thử khói (Smoke Test) | `G9.2 (Apply)` |
| **3** | Antigravity AI Agent (Claude / Gemini) | `2026-11-21 15:09` – `17:53` | Hướng dẫn bố cục quay video (JMeter + Task Manager + `dxdiag`), cách đọc bảng `Aggregate Report`, cấu hình 3 loại báo cáo khác nhau và diễn giải kịch bản | `G9.4 (Collaborate)` |
| **4** | Antigravity AI Agent (Claude / Gemini) | `2026-11-22 15:07` – `17:19` | Rà soát minh chứng ảnh chụp màn hình, viết báo cáo `Report.md` cấu trúc theo `Task 1 – Task 2 – Task 3` của mục `6. Requirements` | `G9.3 (Analyse)` & `G9.6 (Disrupt)` |
| **5** | Antigravity AI Agent (Claude / Gemini) | `2026-11-22 19:35` | **Human Review & Fix kịch bản:** Cắt bỏ 4 API dư thừa (`users`, `orders`, `categories`, `coupons`), rút gọn cả 3 file `.jmx` và báo cáo về đúng 4 bước cốt lõi | `G9.4 (Collaborate)` |
| **6** | Antigravity AI Agent (Claude / Gemini) | `2026-11-22 21:18` | Phân tích bộ 3 file log thô `.jtl` 4 bước ngày `22/11/2026`, săn lỗi đọc sai chỉ số (Misinterpretation Hunt), phân loại đề xuất tối ưu (Feasible/Hallucinated) và xác lập ngưỡng hiệu năng | `G9.3 (Analyse)` & `G9.4 (Collaborate)` |

---

### 3.2. Chi tiết từng Phiên Tương tác (Detailed Interaction Logs)

#### Interaction 1 — Lập kế hoạch kiểm thử hiệu năng và khảo sát mã nguồn SUT
- **Name of the AI tool:** Antigravity AI Agent (Claude Opus 5.5)
- **Date and time:** `2026-11-21 14:16:39 +07:00`
- **Your prompt:**
  > *"Lên kế hoạch thực hiện bài tập này. Ở mục Scope tôi chọn luồng đăng nhập admin -> xem danh sách sản phẩm -> import sản phẩm từ file csv"*
- **The AI output:**
  - AI trích xuất yêu cầu từ file PDF đề bài HW05 và đọc trực tiếp mã nguồn `backend/server.js`, `backend/database.js`, `frontend-admin/src/App.jsx`.
  - AI ánh xạ luồng kiểm thử vào 3 nhóm endpoint bắt buộc:
    1. **Auth-heavy:** `POST /api/login`
    2. **Read-heavy:** `GET /api/products`
    3. **Transactional:** `POST /api/admin/import-products`
  - AI chỉ ra 5 đặc điểm kỹ thuật quan trọng trong code ảnh hưởng đến thiết kế test: (1) lỗi cộng `+2` vào `login_attempts` làm tài khoản bị khóa ngay sau lần sai thứ 2 trong 180 giây; (2) hệ thống chỉ có 1 tài khoản `admin@eshop.com` duy nhất; (3) `database.js` tự động `DROP` và seed lại bảng mỗi lần khởi động lại `node server.js`; (4) `GET /api/products` không có phân trang; (5) API `/api/admin/import-products` chỉ kiểm tra `authenticateToken` mà thiếu kiểm tra quyền `role === 'admin'`.
- **Human Review & Refinement:**
  - Sinh viên xem xét kế hoạch và chốt các quyết định thiết kế ở bước tiếp theo: chỉ dùng công cụ JMeter, dùng chung tài khoản `admin@eshop.com`, chạy backend trực tiếp bằng `node server.js` và lưu ý rõ giao diện mục tiêu là `frontend-admin`.

---

#### Interaction 2 — Sinh dữ liệu CSV và khởi tạo 3 kịch bản JMeter (`Load`, `Stress`, `Spike`)
- **Name of the AI tool:** Antigravity AI Agent (Claude Opus 5.5)
- **Date and time:** `2026-11-21 14:27:10 +07:00`
- **Your prompt:**
  > *"Chỉ dùng JMeter. Chỉ dùng chung admin@eshop.com. Backend chạy node server.js. Note: trang web chạy là frontend-admin chứ không phải frontend-web."*
- **The AI output:**
  - AI tạo script `tools/gen_data.py` sinh 2 file CSV dữ liệu đầu vào: `data/admin_credentials.csv` (tài khoản `admin@eshop.com`) và `data/products_import.csv` (500 dòng sản phẩm mẫu khớp định dạng `name,price,description,imageUrl,category_id` của `frontend-admin`).
  - AI tạo script `tools/build_plans.py` sinh 3 file kịch bản JMeter: `23120073_Load_20261122.jmx` (20 VU, ramp-up 60s, 600s, Listener `Aggregate Report`), `23120073_Stress_20261122.jmx` (5 bậc thang 10 → 25 → 50 → 100 → 200 VU, mỗi bậc 120s, Listener `Summary Report`), và `23120073_Spike_20261122.jmx` (nền 10 VU, vọt lên 150 VU trong 5s tại giây 120, giữ 60s rồi về 10 VU, Listener `Response Time Graph`).
  - AI chạy kiểm thử khói (Smoke Test) phát hiện và sửa lỗi phạm vi biến `User Defined Variables` (`PHASE=start/end` bị ghi đè toàn cục trong JMeter) bằng cách đổi sang đọc `prev.getSampleLabel()`.
- **Human Review & Refinement:**
  - Sinh viên mở các file `.jmx` trong JMeter GUI để kiểm tra trực quan, chạy thử kịch bản và sau đó phát hiện điểm dư thừa trong hàm `fetchData()` để yêu cầu tinh chỉnh ở Interaction 5.

---

#### Interaction 3 — Kiểm tra bố cục quay video, hướng dẫn đọc kết quả và 3 loại báo cáo JMeter
- **Name of the AI tool:** Antigravity AI Agent (Claude Sonnet 5.5 & Gemini 4 Argon)
- **Date and time:** `2026-11-21 15:09:08 +07:00` đến `2026-11-21 17:53:07 +07:00`
- **Your prompt:**
  > - *"1 file jmx chạy mất bao lâu, ví dụ Load. Dựa trên yêu cầu khi quay video thì để như hình đã hợp lí chưa"*
  > - *"Đã chạy xong script Load. Kết quả trong result có đúng không ? Hướng dẫn đọc kết quả từ hình ảnh chụp"*
  > - *"Về 3 loại báo cáo khác nhau thì View Results Tree, Summary Report, Aggregate Report làm như thế nào ?"*
  > - *"bạn có thể diễn đạt kịch bản đã tạo ra trong file jmx không ?"*
- **The AI output:**
  - AI giải thích thời lượng chạy của từng kịch bản (Load ~10 phút, Stress ~10 phút, Spike ~6 phút), nhận xét ảnh chụp bố cục màn hình và nhắc sinh viên điền đường dẫn file `.jtl` vào ô `Filename` cũng như hiển thị rõ tiến trình `Node.js JavaScript Runtime` trên Task Manager.
  - AI hướng dẫn cách đọc các cột phân vị (`Average`, `Median`, `90% Line`, `95% Line`, `99% Line`, `Error %`, `Throughput`, `Received KB/sec`) và chỉ ra bẫy đơn vị `/min` của JMeter ở bước Import CSV.
  - AI giải thích sự khác biệt giữa 3 loại Listener (`Aggregate Report`, `Summary Report`, `Response Time Graph` / `View Results Tree`) và diễn đạt toàn bộ cấu trúc cây kịch bản `.jmx`.
- **Human Review & Refinement:**
  - Sinh viên kiểm tra lại cửa sổ `dxdiag`, Task Manager và JMeter trên màn hình để chuẩn bị chụp ảnh minh chứng và quay video.

---

#### Interaction 4 — Rà soát minh chứng ảnh chụp và cấu trúc hóa báo cáo `Report.md` theo đề bài
- **Name of the AI tool:** Antigravity AI Agent (Gemini 4 Argon & Claude Opus 5.5)
- **Date and time:** `2026-11-22 15:07:49 +07:00` đến `2026-11-22 17:19:18 +07:00`
- **Your prompt:**
  > - *"Bức ảnh này có đạt minh chứng không ?"*
  > - *"Viết 1 báo cáo Report.md: Nêu họ và tên, MSSV; Nêu luồng kiểm thử end-to-end đã chọn; Mô tả các file kịch bản kiểm thử; Chỉ vị trí file csv cho kiểm thử"*
  > - *"Tạo 1 bảng tổng hợp kết quả phân tích chỉ ngày 22112026 vào report.md. Viết mục 4 vào Report sau đó với tên mục là xem xét và sửa lỗi. Bỏ qua các báo cáo html hay các dữ liệu ngày 21112026"*
  > - *"Có 1 chút hiểu lầm ở đây. Bạn hãy sắp xếp lại các mục trong report.md ứng với task trong mục Requirement trong file đính kèm"*
- **The AI output:**
  - AI kiểm tra ảnh chụp màn hình của sinh viên, phát hiện cửa sổ `dxdiag` đang che khuất dòng `Node.js JavaScript Runtime` trên Task Manager và hướng dẫn gõ `node` vào ô tìm kiếm của Task Manager cũng như thu hẹp khung cây bên trái của JMeter để lộ rõ cột `Error %` và `Throughput`.
  - AI tổ chức lại toàn bộ file `Report.md` khớp 1-1 với từng mục của `6. Requirements` trong đề bài PDF: **Task 1** (1.1 Thiết kế với AI, 1.2 Data-driven CSV, 1.3 Ba loại báo cáo, 1.4 Xem xét và sửa lỗi kịch bản, 1.5 Thực thi & bằng chứng phần cứng, 1.6 Ngưỡng bền vững Endurance Threshold, 1.7 Video demo & Báo cáo lỗi), **Task 2** (2.1 Phân tích & đề xuất ngưỡng hiệu năng, 2.2 Săn lỗi đọc sai chỉ số, 2.3 Đánh giá đề xuất tối ưu Feasible/Hallucinated) và **Task 3** (Đề xuất mô hình Continuous Performance Testing kèm sơ đồ Flowchart và thảo luận đánh đổi Cost vs. False Alarms).
- **Human Review & Refinement:**
  - Sinh viên rà soát lại nội dung báo cáo và phát hiện kịch bản 12 bước vẫn đang chứa 4 API không nằm trong Scope đã chọn.

---

#### Interaction 5 — Human Review phát hiện và cắt bỏ 4 API dư thừa khỏi kịch bản `.jmx`
- **Name of the AI tool:** Antigravity AI Agent (Gemini 4 Argon)
- **Date and time:** `2026-11-22 19:35:41 +07:00`
- **Your prompt:**
  > *"Tôi vừa mới phát hiện 1 chi tiết đáng giá đấy. Ở luồng xác định ngay từ đầu chỉ xem danh sách sản phẩm, những thứ khác như danh mục, đơn hàng, người dùng, mã giảm giá là dư thừa. Bạn có thể cắt bỏ những phần liên quan đến nó không kể cả file jmx, lát nữa tôi sẽ chạy lại test nên phiền bạn thực hiện lại task 2 sau"*
- **The AI output:**
  - AI ghi nhận phát hiện phản biện của sinh viên vào mục #1 của bảng **1.4. Xem xét và sửa lỗi kịch bản do AI sinh ra (Human Review)** trong `Report.md` và `test_design.md`.
  - AI sửa `tools/build_plans.py` và sinh lại cả 3 file `.jmx` (`23120073_Load_20261122.jmx`, `23120073_Stress_20261122.jmx`, `23120073_Spike_20261122.jmx`), loại bỏ toàn bộ 4 API phụ (`admin/users`, `admin/orders`, `categories`, `coupons`) ở cả trước và sau khi import, chỉ giữ lại đúng **4 bước cốt lõi**:
    1. `01_Auth_POST_login` (`POST /api/login`)
    2. `02_Read_GET_products` (`GET /api/products`)
    3. `03_Txn_POST_import_products` (`POST /api/admin/import-products`)
    4. `04_Read_GET_products_after_import` (`GET /api/products`)
- **Human Review & Refinement:**
  - Sinh viên mở lại 3 file `.jmx` 4 bước trong JMeter GUI và trực tiếp chạy lại toàn bộ 3 kịch bản `Load`, `Spike`, `Stress` để thu thập bộ log thô `.jtl` mới.

---

#### Interaction 6 — Phân tích bộ file `.jtl` 4 bước mới và hoàn thiện Task 2 trong `Report.md`
- **Name of the AI tool:** Antigravity AI Agent (Gemini 4 Argon)
- **Date and time:** `2026-11-22 21:18:58 +07:00`
- **Your prompt:**
  > *"Đã xong, hãy chạy lại task 2 và điền số liệu mới vào report"*
- **The AI output:**
  - AI chạy script `tools/analyze_jtl.py` trên 3 file `.jtl` 4 bước mới vừa được sinh viên thực thi (`23120073_Load_20261122.jtl` gồm 5.089 mẫu chính, `23120073_Spike_20261122.jtl` gồm 2.118 mẫu chính, `23120073_Stress_20261122.jtl` gồm 5.263 mẫu chính) và đối chiếu với `jmeter.log` (`12.800 → 14.900 → 15.670 → 17.725` sản phẩm).
  - AI cập nhật toàn bộ bảng tổng hợp kết quả, ngưỡng chịu tải bền vững (`Max Stable RPS = 8,54–9,20 req/s` tương đương trần băng thông JSON `~10,2–11,5 MB/s`, trần RAM `node.exe` `~371–420 MB`), 6 mục săn lỗi đọc sai chỉ số kèm trích dẫn giá trị đúng từ raw `.jtl` (như phân biệt `2.435` lỗi HTTP 200 quá hạn 5s với `212` lỗi Socket ở bậc 200 VU, kiểm chứng `411/416` lô import vẫn được ghi vào SQLite bất chấp client timeout 30s, và quy luật bão hòa thông lượng theo Định luật Little) cùng bảng đánh giá 8 đề xuất tối ưu (5 Feasible, 3 Hallucinated) vào `Report.md` và `task2_analysis.md`.
- **Human Review & Refinement:**
  - Sinh viên kiểm tra lại toàn bộ bảng số liệu trong `Report.md` để đảm bảo khớp 100% với 3 file `.jtl` thực tế trong thư mục `results/`.
