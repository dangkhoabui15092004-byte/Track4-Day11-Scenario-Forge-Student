MSSV: 2A202602617

# Lab 11 · Scenario Forge — báo cáo

Thị trấn của bạn (`meta.json: _run.town`): A

## 1. Phát lại log có trung thực không? (bước A)

Theo số liệu từ `replay.json`:
- Số kịch bản bị loại do người lái thật tự gây va chạm (`dropped_human_crash_logs`): **1** (trên tổng số n = 400 kịch bản, sử dụng `n_used`: **399**).
- Số va chạm khi planner chạy trên **log phát lại** (`replay.crashes`): **98** vụ. Phân loại theo tiếp xúc:
  - `rear` (bị đâm đuôi): **85** vụ (chiếm 86.7%)
  - `side` (va chạm sườn): **13** vụ (chiếm 13.3%)
  - `front`: **0** vụ
- Số va chạm trong **thế giới phản ứng** (`reactive.crashes`): **0** vụ (không có va chạm nào).
- Số kịch bản va chạm ở cả hai môi trường (`crash_in_both`): **0**.

**Giải thích:**
- Phần lớn va chạm trong log phát lại là va chạm từ phía sau (`rear`) vì các tác nhân khác trong log được "phát lại cứng" (open-loop playback) theo đúng hành vi người lái gốc đã ghi nhận. Khi planner của xe tự lái phanh sớm hoặc thận trọng hơn người lái thật, xe bám đuôi (TG - tailgater) trong log không biết điều này nên không hề phanh theo, dẫn đến đâm vào đuôi xe ta.
- Đây hoàn toàn là **va chạm giả (phantom crash)**: Trong môi trường phản ứng (`reactive`), xe bám đuôi quan sát thấy xe ta phanh và cũng đạp phanh giảm tốc theo quy tắc IDM, do đó thực tế không xảy ra bất kỳ va chạm nào (`reactive.crashes = 0`).
- **Kịch bản cụ thể (`replay_only`):** Chọn kịch bản `scenario: 1`. Trong log phát lại, xe ta bị đâm đuôi (`contact: rear`). Tuy nhiên trong môi trường phản ứng, khoảng cách thời gian nhỏ nhất tới va chạm `min_ttc_reactive = 2.49 s` (rất an toàn, xe sau phản ứng kịp thời và không có va chạm).

---

## 2. Kịch bản bất khả thi (bước B)

**Các luật trong `is_feasible` và căn cứ vật lý:**
1. $\left(\frac{\pi}{\text{cutDur}}\right)^2 \cdot \frac{3.5}{2} \le \mu \cdot g$: Gia tốc ngang cực đại của cú chuyển làn theo quỹ đạo hình cosin rộng 3.5 m trong thời gian `cutDur` không được vượt quá lực bám ma sát ngang của lốp xe $\mu g$.
2. $\text{cutBrake} \le \mu \cdot g$: Gia tốc phanh sau khi nhập làn không được vượt quá giới hạn gia tốc ma sát trượt dọc của mặt đường $\mu g$.
3. $\text{pedV} \le 2.5\text{ m/s}$: Tốc độ đi bộ của người không vượt quá $2.5\text{ m/s}$ (vượt quá tốc độ này là chạy nước rút, không khả thi cho người đi bộ bình thường).
4. $0 < \text{cutV} \le 22\text{ m/s}$ ($\approx 79.2\text{ km/h}$): Vận tốc xe cắt làn phải dương và nằm trong giới hạn vận tốc tối đa của đường phố đô thị.

**Phân tích từ `hunt.json`:**
- Số kịch bản bất khả thi bị loại bỏ trong từng cuộc săn:
  - `bus_bypass`: **1**
  - `cut_in`: **4**
  - `crosswalk_block`: **5**
  - `rear_ended`: **15** (cuộc săn sinh nhiều kịch bản bất khả thi nhất)
- **Vì sao CEM bị kéo về phía đó:** Thuật toán Cross-Entropy Method (CEM) tối ưu hóa theo hàm điểm nguy hiểm (danger score). Để tạo ra va chạm đâm đuôi `rear_ended`, hàm mục tiêu thúc đẩy thời gian chuyển làn `cutDur` cực ngắn và gia tốc phanh `cutBrake` cực lớn trên mặt đường ma sát thấp $\mu = 0.5$. Những kịch bản vi phạm vật lý này tạo ra điểm nguy hiểm cao nhất, khiến phân phối đề xuất $q$ bị kéo mạnh vào vùng bất khả thi.
- **Hậu quả nếu đếm chúng là va chạm:** Xác suất tai nạn sẽ bị thổi phồng giả tạo (overestimated), báo cáo sai những vụ tai nạn "bóng ma" mà quy luật vật lý và lốp xe thực tế không thể xảy ra.

---

## 3. Monte Carlo cho bạn biết gì (bước C1)

Theo `mc.json`:
- Số va chạm quan sát được: $k = 5$ vụ trên tổng số $n = 3000$ lần chạy tự nhiên.
- Tỉ lệ ước lượng điểm: $\hat{p} = 1.67 \times 10^{-3}$ (0.167%).
- Khoảng tin cậy Wilson 95%: $[7.12 \times 10^{-4}, 3.90 \times 10^{-3}]$ ($[0.071\%, 0.390\%]$).
- Số lần chạy $n$ cần thiết để khoảng tin cậy hẹp lại còn $\pm 20\%$ của $p$:
  $$\text{Margin of error} = 1.96 \sqrt{\frac{p(1-p)}{n}} \le 0.20 \cdot p \implies n \approx \frac{1.96^2}{0.20^2 \cdot p} \approx \frac{96.04}{p}$$
  Với $\hat{p} = 1.67 \times 10^{-3}$, cần:
  $$n \approx \frac{96.04}{0.001667} \approx 57,600\text{ lần chạy.}$$
- **Kiểu thất bại chưa xuất hiện:** Trong 3.000 lần chạy, toàn bộ 5 vụ va chạm đều thuộc kiểu `bus_bypass`. Các kiểu `cut_in`, `crosswalk_block`, `rear_ended`, và `other` có $k = 0$.
- **Con số đúng cần báo:** Không được báo xác suất bằng 0. Con số đúng phải là cận trên 95% của khoảng tin cậy Wilson: $\text{hi} = 1.28 \times 10^{-3}$ (tương đương cận quy tắc số ba: $3/n = 3/3000 = 1.0 \times 10^{-3}$).

---

## 4. Importance sampling, ESS và độ suy biến (bước C3)

**Bảng kết quả ước lượng Importance Sampling từ `estimate.json` ($n = 600$ mỗi kiểu, $z = 1.96$):**

| Seed | Kiểu thất bại | $p$ | hits | ess | top_share |
|---|---|---|---|---|---|
| **0** | `bus_bypass` | $9.02 \times 10^{-4}$ | 34 | 136.4 | 0.526 |
| | `cut_in` | 0.00 | 0 | 133.5 | 0.000 (upper: 0.025) |
| | `crosswalk_block` | $1.86 \times 10^{-7}$ | 53 | 133.5 | 0.474 |
| | `rear_ended` | 0.00 | 0 | 121.1 | 0.000 (upper: 0.025) |
| | **Total seed 0** | **$9.02 \times 10^{-4}$** | — | — | 95% CI: $[0.0, 3.14 \times 10^{-3}]$ |
| **1** | `bus_bypass` | $1.53 \times 10^{-3}$ | 33 | 127.8 | 0.257 |
| | `cut_in` | 0.00 | 0 | 142.1 | 0.000 (upper: 0.025) |
| | `crosswalk_block` | $5.54 \times 10^{-7}$ | 56 | 117.7 | 0.714 |
| | `rear_ended` | 0.00 | 0 | 115.1 | 0.000 (upper: 0.025) |
| | **Total seed 1** | **$1.53 \times 10^{-3}$** | — | — | 95% CI: $[3.47 \times 10^{-4}, 3.99 \times 10^{-3}]$ |
| **2** | `bus_bypass` | $5.52 \times 10^{-4}$ | 29 | 141.4 | 0.200 |
| | `cut_in` | 0.00 | 0 | 113.8 | 0.000 (upper: 0.025) |
| | `crosswalk_block` | $1.53 \times 10^{-7}$ | 54 | 120.2 | 0.225 |
| | `rear_ended` | 0.00 | 0 | 117.4 | 0.000 (upper: 0.025) |
| | **Total seed 2** | **$5.52 \times 10^{-4}$** | — | — | 95% CI: $[2.00 \times 10^{-4}, 2.18 \times 10^{-3}]$ |

- **Đồng thuận giữa 3 seed và với Monte Carlo:**
  - 3 seed ước lượng tổng xác suất lần lượt là $9.02 \times 10^{-4}$, $1.53 \times 10^{-3}$, và $5.52 \times 10^{-4}$. Trung vị qua 3 seed là $\approx 9.02 \times 10^{-4}$ (chênh lệch giữa các seed trong khoảng $\times 2.7$ lần).
  - Cả 3 khoảng tin cậy đều giao thoa mạnh và hoàn toàn nhất quán với khoảng Wilson 95% của Monte Carlo ($[7.12 \times 10^{-4}, 3.90 \times 10^{-3}]$, tâm tại $1.67 \times 10^{-3}$).
- **Vị trí `top_share` lớn (> 0.5):**
  - Xuất hiện ở Seed 0 kiểu `bus_bypass` (`top_share = 0.526`) và Seed 1 kiểu `crosswalk_block` (`top_share = 0.714`).
  - **Lý do:** Khi phân phối đề xuất $q$ săn sâu vào vùng hiếm, trọng số $w = p/q$ của một mẫu cá biệt rơi vào vùng đuôi phân phối tự nhiên $p$ lớn hơn hẳn các mẫu khác, khiến riêng mẫu này đóng góp hơn 50–70% tổng giá trị ước lượng, làm suy biến tính đại diện thống kê.
- **So sánh ngân sách (`budget`):**
  - Ngân sách IS trong bài là `budget = 16,800` lần chạy.
  - Để tìm thấy và ước lượng được kiểu siêu hiếm như `crosswalk_block` ($p \approx 3 \times 10^{-7}$) với Monte Carlo thông thường, cần cỡ $100 / p \approx 300,000,000$ lần chạy. IS giúp giảm hàng chục nghìn lần chi phí tính toán.
- **Phần `other`:** Lấy từ `mc.json: other` ($k=0, n=3000, p=0, hi = 1.28 \times 10^{-3}$). Ta không săn `other` vì đây là tập hợp phân tán của mọi va chạm không định hình trước, không có một hàm điểm nguy hiểm (danger score) duy nhất để thuật toán CEM hội tụ.

---

## 5. Các kiểu thất bại (bước C2 + 3D)

**Các kiểu tìm thấy trong `hunt.json`:**
1. **`bus_bypass` (136 ca va chạm tìm thấy):**
   - *Chuỗi sự kiện:* Xe buýt đỗ ở làn bên cạnh che khuất hoàn toàn tầm nhìn. Xe C2 đi chậm ($< 6\text{ m/s}$) lách qua sườn xe buýt. Xe ta tiến tới với vận tốc hành trình và không có tầm nhìn xuyên qua thân xe buýt, khi C2 nhô đầu ra thì khoảng cách đã quá gần, xe ta phanh không kịp và đâm vào C2.
   - *Ảnh 3D lúc va chạm:*
   ![Chương 9: va chạm bus_bypass](shots/ch9-lab-bus-bypass.jpg)

2. **`crosswalk_block` (28 ca chặn lối người đi bộ):**
   - *Chuỗi sự kiện:* Người đi bộ P1 bước qua đường từ phía sau đuôi xe buýt. Do xe buýt cao che tầm mắt, xe ta chỉ nhận diện được P1 khi người đã bước gần tim đường. Planner phanh gấp tối đa: xe dừng lại kịp thời trước người đi bộ (không tông người), nhưng thân xe đã dừng lấn lên vạch sang đường khiến người đi bộ phải đứng lại chờ.
   - *Ảnh 3D lúc chặn lối:*
   ![Chương 9: chặn lối crosswalk_block](shots/ch9-lab-crosswalk-block.jpg)

- **Kiểu không tìm thấy độc lập:** Cuộc săn `cut_in` chỉ tìm thấy 35 ca `bus_bypass` và 1 ca `crosswalk_block`; cuộc săn `rear_ended` chỉ tìm thấy 1 ca `bus_bypass` và 10 ca `crosswalk_block`. Các kiểu va chạm này không xảy ra độc lập trên đường thẳng thông thường mà chỉ phát sinh thứ cấp từ việc tránh xe buýt và người đi bộ.
- **Vì sao cần săn riêng từng kiểu:** Nếu chỉ chạy 1 cuộc săn chung gộp tất cả kiểu, thuật toán CEM sẽ nhanh chóng bị hút về kiểu va chạm dễ xảy ra nhất (`bus_bypass`), khiến phân phối $q$ co hẹp cục bộ tại đó và hoàn toàn bỏ lọt các kiểu thất bại hiếm khác như `crosswalk_block`.

---

## 6. Sửa planner (bước E + 3D)

Theo `fix.json`:
- **Policy được chọn:** `{'cutinLat': 3.0}` (nâng ngưỡng nhận diện xe cắt làn từ 2.15 m lên 3.0 m).
- **Kết quả trên tập TRAIN:**
  - Policy được chọn: `fail` = $4.14 \times 10^{-7}$, `fail_hi` = $1.00 \times 10^{-6}$, `progress` = 208.96 m, `harsh` = 8.28.
  - Policy gốc (baseline): `fail` = $5.82 \times 10^{-4}$, `fail_hi` = $1.04 \times 10^{-3}$, `progress` = 208.97 m, `harsh` = 8.76.
- **Kết quả kiểm định độc lập trên tập TEST (seed mới + săn lại):**
  - **Chosen policy:**
    - `fail` = $8.31 \times 10^{-7}$
    - `fail_hi_seen` = $1.36 \times 10^{-6}$
    - `fail_hi (valid)` = $3.88 \times 10^{-2}$ (0.0388)
    - `unseen` = `['bus_bypass']` (không có ca va chạm bus_bypass nào xuất hiện trên TEST)
    - `progress` = 214.9 m, `harsh` = 7.76
  - **Baseline policy:**
    - `fail` = $1.40 \times 10^{-3}$
    - `fail_hi_seen` = $3.07 \times 10^{-3}$
    - `fail_hi (valid)` = $4.35 \times 10^{-3}$
    - `unseen` = `[]`
    - `progress` = 214.9 m, `harsh` = 8.22

**Giải thích vì sao `fail_hi` của bản sửa ($0.0388$) lại lớn hơn `fail` của baseline ($0.0014$) dù bản sửa thực tế tốt hơn:**
- Bản sửa đã triệt tiêu hoàn toàn va chạm `bus_bypass` ($0$ vụ va chạm trong $n=400$ lần chạy TEST).
- Về mặt lý thuyết thống kê, khi một kiểu có 0 va chạm (`unseen`), ta không được phép kết luận xác suất bằng 0 mà phải cộng thêm cận trên Wilson $3 / (0.2 \cdot n) = 3 / (0.2 \times 400) = 0.0375$. Với ngân sách $n=400$, ta chưa đủ mẫu để chứng minh toán học một kiểu đã biến mất dưới ngưỡng $10^{-2}$.
- Tuy nhiên, trên những gì quan sát được (`fail_hi_seen`), bản sửa đạt $1.36 \times 10^{-6}$, tốt hơn baseline ($3.07 \times 10^{-3}$) hơn 2.000 lần.

- **Quãng đường và phanh gấp:** Quãng đường di chuyển được bảo toàn nguyên vẹn ($214.9\text{ m}$ vs $214.9\text{ m}$), trong khi số khung hình phanh gấp giảm từ 8.22 xuống 7.76.
- **Núm chỉnh "nghe thì an toàn" nhưng làm tăng thất bại:**
  - Ứng viên `[9] {'T': 2.0}` (tăng khoảng cách thời gian bám đuôi từ 1.6 lên 2.0 s) làm tỉ lệ thất bại trên TRAIN tăng vọt từ $5.82 \times 10^{-4}$ lên $1.72 \times 10^{-3}$.
  - *Giải thích:* Khi xe ta tăng khoảng cách an toàn, xe ta chạy chậm lại và mở ra một khoảng trống (gap) lớn hơn phía trước. Xe cắt làn C2 ở làn bên cạnh quan sát thấy khe hở hấp dẫn này liền lập tức lách sang tạt đầu xe ta, làm gia tăng xung đột giao thông. Thế giới luôn phản ứng lại chính sách lái của xe ta!

---

## 7. Từ mô phỏng ra đường thật

Ba giả định then chốt trong `space.py`:
1. **Khoảng chấp nhận chuyển làn của xe hàng xóm (`cutGap`):**
   - *Dữ liệu thay thế:* Trích xuất phân phối chấp nhận khe hở thực tế từ tập dữ liệu xe tự lái quy mô lớn (nuScenes, Waymo Open Dataset) theo từng mật độ giao thông.
   - *Hướng sai lệch:* Ngoài đời thực (đặc biệt trong đô thị đông đúc), các tài xế thường tạt đầu với khe hở nhỏ hơn nhiều. Nếu giả định mô phỏng quá lịch sự, xác suất va chạm thực tế sẽ **cao hơn** số liệu lab báo cáo.
2. **Tỷ lệ người đi bộ ngó nhìn qua xe buýt (`pedLook`):**
   - *Dữ liệu thay thế:* Khảo sát video giám sát thực tế tại các trạm dừng xe buýt về tỉ lệ người đi bộ cúi đầu xem điện thoại hoặc đi nhanh không quan sát trước khi bước qua đầu xe buýt.
   - *Hướng sai lệch:* Mô phỏng đang gán xác suất nhìn cao ($p=0.6$). Ngoài đời, nếu người đi bộ thiếu tập trung hơn, số vụ tai nạn thực tế sẽ **cao hơn**.
3. **Hệ số ma sát mặt đường ướt (`mu`):**
   - *Dữ liệu thay thế:* Dữ liệu đo đạc trực tiếp từ cảm biến gia tốc bánh xe khi thử nghiệm phanh trên mặt đường nhựa Việt Nam trong điều kiện mưa ngập, rêu trơn.
   - *Hướng sai lệch:* Mô phỏng dùng $\mu = 0.5$ và $0.8$. Nếu đường thực tế dính bùn đất hoặc dầu trơn có $\mu < 0.4$, quãng đường phanh thực tế dài hơn đáng kể, làm số vụ va chạm **tăng cao**.

---

## 8. Giới hạn

**Ba điều mà xác suất báo cáo KHÔNG phản ánh:**
1. *Hình học tuyến đường:* Mô phỏng chỉ có một đoạn phố thẳng hai làn với một trạm xe buýt và một vạch qua đường; chưa có ngã tư, vòng xuyến, hay đèn tín hiệu giao thông.
2. *Hành vi tác nhân khác:* Các xe khác chỉ lái theo mô hình IDM 1D cứng nhắc và chuyển làn theo đường cong cosin định sẵn, không biết đánh lái né tránh hay nháy đèn bấm còi như tài xế thực.
3. *Mô hình nhận thức hoàn hảo:* Cảm biến xe tự lái trong lab nhận diện vị trí và kích thước vật thể tức thời và chính xác 100% (chỉ bị che bởi góc khuất hình học), bỏ qua độ trễ nhận diện (perception latency ~100–200 ms), nhiễu hạt Lidar, hay nhận diện nhầm vật thể.

*Nếu có thêm một tuần:* Em sẽ tích hợp mô hình cảm biến thực tế có độ trễ nhận thức (perception delay) và độ rung sai số vị trí vật thể, đồng thời mở rộng mô phỏng cho nút giao thông có đèn tín hiệu.

---

## 9. Rắc rối của bạn (bước G + chương 10)

- **Rắc rối:** Dựng tình huống người đi bộ tự phát băng cắt qua đường (`type: ped`) ngoài vạch qua đường từ lề phía nam khu dân cư tại vị trí $x \in [180, 260]$ m, vận tốc $v \in [1.2, 2.0]$ m/s, kích hoạt khi xe còn cách $trig \in [12, 28]$ m. Tương ứng với tình huống người dân bất ngờ bước xuống lòng đường từ điểm mù giữa các xe đỗ ven đường.
- **Căn cứ:** Planner của xe ta chỉ có logic giảm tốc thận trọng quanh vạch qua đường (`cautionRange`, `cautionV`). Khi gặp người băng ngang ở đoạn đường thẳng thông thường, planner không giảm tốc độ từ xa mà chỉ phản ứng khi người đã bước vào làn đường.
- **Giả định:** Khoảng biến thiên `space` tuân thủ nghiêm ngặt `LIMITS["ped"]` (`h0_x`: [180, 260], `h0_v`: [1.2, 2.0], `h0_trig`: [12, 28]); `exposure = 0.012` dựa trên thống kê va chạm người đi bộ đô thị NHTSA/FARS (~1.2% số chuyến đi gặp tình huống người băng cắt ngoài vạch).
- **Kết quả (theo `mine.json`):**
  - Số mẫu kiểm định: 1.497 kịch bản khả thi trên 1.500 lần rút (`accepted = 99.8%`, `infeasible = 3`).
  - **Baseline policy:**
    - Tổng va chạm: **2** vụ = **0** avoidable + **0** unavoidable + **2** unattributed (0 vụ ở $< 1\text{ m/s}$).
    - $P(\text{planner failure} \mid \text{hazard}) = 0.00$ (khoảng Wilson: $[0.00, 2.56 \times 10^{-3}]$).
    - Tần suất mỗi chuyến đi: $0.00$ (cận trên: $3.07 \times 10^{-5}$).
  - **Chosen policy (`cutinLat: 3.0`):**
    - Tổng va chạm: **0** vụ = **0** avoidable + **0** unavoidable + **0** unattributed.
    - $P(\text{planner failure} \mid \text{hazard}) = 0.00$ (khoảng Wilson: $[0.00, 2.56 \times 10^{-3}]$).
    - Tần suất mỗi chuyến đi: $0.00$ (cận trên: $3.07 \times 10^{-5}$).
  - *Nhận xét kết quả:* Toàn bộ va chạm của baseline đều là `unattributed` (2 vụ xảy ra do xe C2 cắt làn ở $t = 12.55\text{ s}$ và $t = 12.65\text{ s}$, không liên quan đến rắc rối người đi bộ). Planner đã xử lý tốt rắc rối này nhờ quy tắc an toàn của người đi bộ (dừng lại khi thân xe chắn lối) kết hợp biên khoảng cách `pedBuffer = 2.5 m` đủ để xe dừng kịp thời.
- **Hình ảnh minh họa:**
  ![Chương 10: Xưởng kịch bản](shots/ch10-studio.jpg)
- **Bạn tự lái thì sao:** Khi tự cầm lái, người lái nhìn thấy người đi bộ từ xa trên lề đường nên chủ động nhả chân ga và rà nhẹ phanh từ khoảng cách 35–40 m để hạ tốc độ xuống 8 m/s, giúp việc dừng xe diễn ra êm ái hơn nhiều so với việc planner duy trì tốc độ tối đa rồi phanh gấp.
- **Vì sao "tránh được" là chuẩn lạc quan:**
  Chuẩn `avoidable` giả định một "oracle" lý tưởng: ngay khung hình đầu tiên rắc rối kích hoạt và lọt vào tầm nhìn, một bộ phanh hoàn hảo phanh hết cỡ ở giới hạn ma sát $\mu g$ không có độ trễ nhận thức hay trễ thủy lực. Do đó, `avoidable` **đếm nhiều hơn** số va chạm mà một planner thực tế có thể tránh. Ngược lại, chuẩn này chỉ thử phanh mà không cho phép đánh lái tránh né, khiến nó đếm ít đi các trường hợp có thể cứu vãn bằng cách chuyển làn.
- **Cách sửa planner:**
  Để xử lý triệt để các tình huống người băng cắt ngoài vạch, planner cần bổ sung **logic mới**: giám sát mép đường (curbside pedestrian intent prediction). Khi phát hiện người đi bộ ven đường có vector vận tốc hướng vào lòng đường, planner cần tự động giảm tốc độ mục tiêu $v_0$ xuống mức thận trọng (ví dụ 8 m/s) tương tự như khi qua vạch kẻ đường, thay vì chỉ phản xạ khi người đi bộ đã đặt chân vào lòng đường.
