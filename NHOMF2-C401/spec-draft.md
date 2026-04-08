# SPEC draft — NHOMF2-C401

## Track: A — VinFast

## Problem statement

Chủ xe điện VinFast đi đường dài không biết dừng sạc ở đâu, khi nào, bao lâu — lo hết pin giữa đường, không biết trạm nào phù hợp, không tính được thời gian sạc. AI nhận điểm xuất phát, điểm đến, mức pin hiện tại → đề xuất 1–2 lộ trình hợp lý (nhanh nhất trong điều kiện đảm bảo an toàn pin), vị trí trạm dừng sạc, thời lượng sạc dự kiến và cảnh báo rủi ro.

---

## Canvas draft

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Trả lời** | **User:** Chủ xe VinFast đi liên tỉnh, lo "range anxiety" — hết pin giữa đường. **Pain:** Phải tự tính quãng đường, tìm trạm sạc thủ công, không biết loại sạc nào phù hợp xe mình, không ước được thời gian sạc. **AI giải:** Nhận SoC hiện tại + điểm đến → tính tiêu thụ pin theo khoảng cách → đề xuất lộ trình đảm bảo SoC không rơi dưới buffer an toàn tại mọi điểm dừng, và đến đích vẫn còn mức pin chấp nhận được. | **Khi AI sai:** Tính sai tiêu thụ pin → xe đến trạm với SoC thấp hơn dự kiến → nguy hiểm. **User biết sai:** Pin cạn sớm hơn dự đoán hoặc đến trạm thấy SoC thực < SoC dự kiến. **User sửa:** Báo "pin thực tế khi đến trạm" → AI/heuristic hiệu chỉnh hệ số tiêu thụ cho các lần sau (về lâu dài). UI luôn hiển thị SoC dự kiến tại từng điểm dừng để user chủ động theo dõi và can thiệp. | **Cost:** Routing graph + LLM synthesize ~\$0.005–0.01/request. **Latency:** <5s chấp nhận được. **MVP (2 ngày hackathon):** Data trạm sạc tĩnh (mock, không real-time), 1 model xe VinFast, tiêu thụ pin tuyến tính theo khoảng cách, không model queue/time window — đủ để prototype nhanh. **Risk chính:** Mô hình tiêu thụ tuyến tính đơn giản — không xét tốc độ, địa hình, thời tiết → cần buffer an toàn đủ lớn và messaging rõ ràng. |

**Auto hay Augmentation?**  
Augmentation — AI đề xuất lộ trình + điểm sạc, user xem và quyết định đi theo. Không tự động điều hướng real-time, không tự động book slot sạc.

**Learning signal (tầm nhìn dài hạn):**  
- Explicit: user rate lộ trình sau chuyến đi.  
- Correction: user báo SoC thực tế khi đến trạm → hiệu chỉnh hệ số tiêu thụ `e` (kWh/km) hoặc tăng margin an toàn.  
- Implicit: user có chọn lộ trình AI gợi ý hay tự chỉnh tay / re-route giữa đường.

---

## User Stories — 4 paths

| Path | Scenario | UI xử lý |
|------|----------|----------|
| AI đúng | User nhập: Hà Nội → Đà Nẵng, SoC 85%. AI gợi ý dừng sạc tại trạm Vinh, SoC dự kiến khi đến 22%, sạc 45 phút lên 80%, tổng hành trình 7h30. | Bản đồ lộ trình + danh sách trạm + SoC dự kiến tại từng điểm + thời lượng sạc + tiện ích gần trạm. Banner "SoC luôn ≥ buffer an toàn" để user yên tâm. |
| AI không chắc | Đoạn đường có chặng dài, SoC buffer mỏng (SoC dự kiến khi đến trạm tiếp theo ~18–20%). | Cảnh báo vàng: "⚠️ SoC dự kiến khi đến trạm Hà Tĩnh chỉ còn ~18%. Nên sạc thêm tại Vinh hoặc tăng buffer an toàn." Cho phép user tăng slider buffer (SoC_comfort) rồi tính lại. |
| AI sai | Mô hình tính thiếu tiêu thụ → SoC thực thấp hơn dự đoán (ví dụ dự đoán 25%, thực tế 18%). | Nút "Báo SoC thực tế" → user nhập SoC trên đồng hồ xe → lưu correction (log) → ở MVP chỉ hiển thị message "Cảm ơn, chúng tôi sẽ dùng để cải thiện ước lượng sau hackathon". Tầm nhìn dài hạn: dùng correction để cập nhật `e`/margin. |
| User mất tin | User không tin con số SoC dự kiến (đã từng gặp lệch nhiều). | Cho phép kéo chỉnh SoC_comfort (buffer an toàn kế hoạch) lên cao hơn; AI tính lại lộ trình tức thì. Luôn hiển thị: "Xác nhận tình trạng trạm tại app VinFast trước khi khởi hành." và "Không dùng cho điều kiện đường đèo/thời tiết cực đoan trong MVP." |

---

## Eval metrics

(Định nghĩa cho tầm nhìn sản phẩm; MVP chủ yếu dùng để sanity-check.)

- **Feasibility rate (hard safety):**  
  % route AI generate thỏa hard constraint SoC ≥ SoC_hard tại mọi node = 100%. Nếu vi phạm (SoC dự kiến < SoC_hard) → bug nghiêm trọng, không được release.
- **SoC estimation error (trung hạn):**  
  \|SoC_dự_kiến − SoC_thực_tế\| khi đến trạm ≤ 10% dung lượng pin (median). MVP: chỉ log được vài case nếu có manual input.
- **User correction rate:**  
  % lượt user bấm "Báo SoC thực tế" hoặc báo route không giống thực tế → target < 20% sau khi product trưởng thành.
- **Threshold review:**  
  SoC estimation error > 20% liên tục → review hệ số `e` và margin an toàn.
- **Kill criteria (safety):**  
  Có incident xe hết pin do route AI generate vi phạm SoC_hard → dừng ngay, audit toàn bộ mô hình tiêu thụ & constraint.

---

## Failure modes

| Failure | Xác suất (MVP) | Impact | Mitigation (MVP) |
|---------|----------------|--------|------------------|
| SoC thực thấp hơn dự kiến (tiêu thụ thực > mô hình tuyến tính) | Trung bình | Rất cao | Dùng `e` hơi conservative cho tuyến demo, SoC_hard = 10%, SoC_comfort mặc định 20%. Cảnh báo vàng khi buffer < 20%. Messaging rõ: không dùng cho điều kiện cực đoan. |
| Không có route khả thi (chặng quá dài, không đủ trạm) | Thấp–Trung bình | Cao | Báo rõ "Route không khả thi với mức pin hiện tại & buffer an toàn" + gợi ý: (1) xuất phát với SoC cao hơn; (2) chọn điểm đến gần hơn. Không cố gắng hack route nguy hiểm. |
| Trạm trong dataset đã đóng/offline (data tĩnh, mock) | Trung bình | Cao | Disclaimer rõ trên UI: "Dữ liệu trạm trong bản demo là mock/tĩnh — vui lòng xác nhận trạm còn hoạt động trên app chính thức trước khi xuất phát." MVP cho phép user report trạm sai. |
| User over-trust AI, không theo dõi SoC thực | Trung bình | Cao | UI luôn hiển thị SoC dự kiến tại từng điểm + nhắc user kiểm tra đồng hồ xe. Không dùng wording kiểu "đảm bảo", mà là "ước lượng". |
| Lộ trình sát nút SoC_hard tại nhiều chặng liên tiếp | Thấp | Cao | Rule MVP: nếu có ≥2 chặng liên tiếp mà buffer < SoC_comfort, ưu tiên route thay thế "an toàn hơn" (dừng sạc sớm hơn), hoặc gắn cảnh báo đỏ "Hành trình sát giới hạn, cân nhắc chia nhỏ chuyến đi." |

---

## ROI 3 kịch bản

(Định hướng sau pilot nội bộ; không yêu cầu chứng minh trong MVP.)

| | Conservative | Realistic | Optimistic |
|---|------------|-----------|-----------|
| User/tháng | 2,000 | 15,000 | 80,000 |
| Giá trị/user | Tiết kiệm 30 phút tìm trạm thủ công | Tránh 1 lần hết pin giữa đường (~2–3 triệu cứu hộ) | Tăng tin tưởng xe điện, giảm range anxiety toàn thị trường |
| Cost inference | ~\$20/tháng | ~\$150/tháng | ~\$800/tháng |
| Benefit | Tăng NPS, giảm hotline ~10% | Giảm incident ~30%, tăng retention | Trở thành tính năng flagship VinFast app |
| Net | Hòa vốn | Dương rõ | Rất dương |

**Kill criteria (business):**  
SoC estimation error > 20% sau 1 tháng pilot nội bộ → dừng, cải thiện mô hình tiêu thụ & constraint trước khi tiếp tục rollout.

---

## Constraints & Assumptions

### 1. Định hướng dài hạn (EVRPTW-inspired, không build trong hackathon)

- Nhiều model xe VinFast, mỗi model có:
  - Dung lượng pin Q riêng, profile tiêu thụ theo tốc độ/địa hình/thời tiết.
  - Giới hạn công suất sạc khác nhau.
- Trạm sạc có:
  - Time windows (giờ mở cửa), capacity (số cổng sạc), ước lượng hàng chờ real-time.
  - Giá điện, chính sách pricing khác nhau.
- Trip planning nhiều mode: Fastest / Cheapest / Safest / Comfort (amenities).
- Về lâu dài có thể tiến tới routing cho nhiều điểm dừng / nhiều xe (EVRPTW đơn giản hóa).

### 2. Scope MVP hackathon

| # | Assumption (MVP) | Lý do / Ghi chú |
|---|------------------|-----------------|
| C1 | Chỉ 1 model xe VinFast, tham số cố định `Q, e, P_vehicle`. | Đơn giản hóa implement, dễ mock dữ liệu, phù hợp 2 ngày. |
| C2 | Energy consumption tuyến tính: `E = e × d` với 1 hằng số `e` cho mọi chặng. | Giữ mô hình SoC 1 chiều, dễ code. MVP dùng `e` hơi conservative cho tuyến demo. |
| C3 | Battery & safety buffer: SoC ∈ [0, Q]. Có 2 ngưỡng: SoC_hard = 10% (không vi phạm), SoC_comfort mặc định = 20% (planner cố giữ). | Tăng safety so với 1 ngưỡng duy nhất, nhưng vẫn dễ implement (chỉ thêm 1 lần fallback). |
| C4 | Dataset trạm sạc tĩnh, mock (JSON/CSV) — coi như trạm hoạt động 24/7, không hỏng, không hàng chờ. | Hackathon, không có data real-time. Ghi rõ đây là mock data. |
| C5 | Connector type luôn tương thích vì MVP chỉ có 1 model xe VinFast. | Loại bỏ dimension connector khỏi MVP. |
| C6 | Thời gian sạc tuyến tính theo năng lượng nạp, dùng `P_effective = min(P_vehicle, P_station)`. Không model charging curve non-linear >80%. | Đơn giản hóa, đủ cho demo nếu không đẩy SoC đến 100%. |
| C7 | Thời gian lái `t_drive` lấy từ API (hoặc mock), coi là cố định, không phụ thuộc giờ trong ngày. | Bỏ qua traffic/time window trong MVP. |
| C8 | Không model time windows cho trạm, không model capacity/hàng chờ. | Chấp nhận rủi ro, bù bằng disclaimer trong UI. |
| C9 | SoC và vị trí xe coi như chính xác (hoặc nhập tay trong demo). Không model sai số cảm biến. | Đơn giản hóa; bù bằng việc dùng `e` conservative và SoC_hard. |
| C10 | Chỉ tối ưu theo "Fastest-safe" (thời gian hành trình), chưa tối ưu cost/amenities. Cost chỉ hiển thị cho user tham khảo. | Focus rõ vào 1 objective trong MVP. |
| C11 | Hệ thống cần internet (để gọi map API và tải dataset trạm). Không có offline routing. | Scope 2 ngày hackathon. |
| C12 | Mọi demo sẽ được chạy trên 2–3 tuyến được team chuẩn bị trước, trong vùng có mật độ trạm tương đối tốt. | Đảm bảo MVP không lộ những edge case chưa xử lý. |

---

## Mini AI spec

> **Scope MVP:** 1 model xe VinFast, energy tuyến tính, data trạm tĩnh (mock), mode duy nhất = Fastest-safe, với 2 ngưỡng SoC_hard và SoC_comfort.

### Input

| Tham số | Mô tả | MVP |
|---------|-------|-----|
| SoC hiện tại | % pin hiện tại (0–100%) | Bắt buộc (nhập tay hoặc mock từ xe) |
| Điểm xuất phát + đích | Địa chỉ text hoặc chọn trên map | Bắt buộc |
| Model xe | VinFast (1 model duy nhất trong MVP) | Cố định, không cho chọn |
| SoC_comfort | Buffer an toàn kế hoạch (mặc định 20%) | Slider cho user; SoC_hard = 10% cố định, ẩn |

### Output

| Kết quả | Mô tả |
|---------|-------|
| Danh sách trạm dừng | Tên + địa chỉ + tọa độ + thứ tự trên lộ trình |
| SoC dự kiến khi đến trạm | `SoC_arrive = SoC_prev − (e × d) / Q` |
| SoC dự kiến khi rời trạm | `SoC_depart` sau khi sạc (target không vượt quá 80–90% trong MVP) |
| Loại sạc + công suất | AC/DC, `P_effective = min(P_vehicle, P_station)` |
| Thời lượng sạc | `t_charge = (SoC_depart − SoC_arrive) × Q / P_effective` (tuyến tính) |
| Tổng thời gian hành trình | Tổng `t_drive + t_charge` |
| Ước tính chi phí | kWh nạp × đơn giá (nếu mock) — chỉ hiển thị, chưa tối ưu |
| Tiện ích gần trạm | Coffee, nhà hàng, WC — dùng để highlight, không hard constraint |
| Cảnh báo rủi ro | Chặng không khả thi (SoC < SoC_hard), buffer < SoC_comfort, trạm critical duy nhất, v.v. |

### Architecture (MVP)

- **Routing layer:**
  - Dùng API (OSRM/Map) để tính khoảng cách và thời gian lái giữa các điểm.
  - Simple heuristic/greedy: lần lượt chọn trạm tiếp theo sao cho SoC_arrive ≥ SoC_hard, ưu tiên trạm gần nhất trên hướng đi.
- **Energy & charging layer:**
  - `SoC_out = SoC_in − (e × d) / Q` cho mỗi chặng.
  - Hard check: `SoC_out ≥ SoC_hard` tại mọi node.
  - Tính `t_charge` tuyến tính từ `P_effective`.
- **Station data layer:**
  - `stations.json`/`stations.csv` mock: vị trí, `P_station`, loại sạc, amenities, giá (optional).
- **LLM layer:**
  - Nhận output từ planner → synthesize thành ngôn ngữ tự nhiên (tóm tắt hành trình, giải thích điểm dừng, highlight cảnh báo).
- **Confidence handling (SoC buffer):**
  - SoC_arrive ≥ SoC_comfort: gợi ý bình thường.
  - SoC_hard ≤ SoC_arrive < SoC_comfort: cảnh báo vàng "buffer mỏng, cân nhắc dừng sớm hơn".
  - SoC_arrive < SoC_hard: hard block — bắt buộc thêm trạm hoặc báo route không khả thi.

### Future scope (không implement trong hackathon)

- Nhiều model xe, profile tiêu thụ theo tốc độ/địa hình/thời tiết.
- Time windows trạm, ước lượng hàng chờ real-time và station reliability score.
- Multi-objective: time + cost + comfort + safety, cho phép chọn mode.
- Offline routing & re-routing khi mất kết nối.
- Học mô hình consumption từ data (ML) với robust margin theo tuyến.

### Data cần (MVP)

- Database trạm sạc VinFast (mock, tĩnh) trên 1–2 tuyến demo.
- Thông số `Q, e, P_vehicle` của model xe VinFast được chọn.
- POI amenities gần trạm (có thể mock từ Google Maps/ghi tay).

---

## Phân công

### SPEC draft (hôm nay — 23:59 08/04)

| Thành viên | Phần phụ trách |
|------------|----------------|
| Đoàn Nam Sơn | Canvas + Constraints & Assumptions + Failure modes |
| Hoàng Vĩnh Giang | User stories 4 paths + UX flow |
| Nhữ Gia Bách | Eval metrics + Kill criteria + ROI |
| Trần Quang Quí | Mini AI spec + LLM prompt design |
| Vũ Đức Duy | Route planner heuristic + data research (trạm, vehicle params) |

---

### Prototype — Build to demo (09/04)

> **Mục tiêu demo:** User nhập Hà Nội → Đà Nẵng + SoC 85% → hệ thống trả về danh sách trạm dừng, SoC dự kiến tại từng trạm, thời gian sạc, cảnh báo nếu có — hiển thị trên Streamlit.

#### Phase 0 — Chốt shared contracts (tối 08/04) — *cả nhóm*

1. **Schema mock dataset** (`stations.json`) — Sơn chuẩn bị, cả nhóm confirm:

```json
{
  "id": "vinh_01",
  "name": "Trạm VinFast Vinh",
  "lat": 18.6796,
  "lon": 105.6813,
  "p_station_kw": 50,
  "type": "DC",
  "amenities": ["coffee", "wc"]
}
```

2. **Thông số xe VinFast VF8** — Duy điền, cả nhóm dùng:

```python
VEHICLE = {
  "Q_kwh": 82,          # dung lượng pin
  "e_kwh_per_km": 0.22, # tiêu thụ tuyến tính (conservative cho demo)
  "p_vehicle_kw": 150,  # công suất sạc tối đa
  "soc_hard": 0.10,     # buffer an toàn tuyệt đối
  "soc_comfort_default": 0.20
}
```

3. **Interface function Route planner → UI** — Duy + Bách confirm:

```python
def plan_route(origin, destination, soc_current, soc_comfort=0.20) -> dict:
    # returns:
    # {
    #   "stops": [
    #       {
    #         "station": {...},
    #         "soc_arrive": 0.22,
    #         "charge_min": 45,
    #         "soc_depart": 0.80
    #       },
    #       ...
    #   ],
    #   "total_time_min": 450,
    #   "feasible": True,
    #   "warnings": ["SoC thấp tại chặng Hà Tĩnh"],
    #   "soc_hard": 0.10,
    #   "soc_comfort": soc_comfort
    # }
```

---

#### Phase 1 — Build song song (sáng 09/04, target xong trước 14:00)

| Task | Thành viên | Output cụ thể | Dùng gì |
|------|-----------|---------------|---------|
| Mock dataset | Đoàn Nam Sơn | `stations.json` — 8–10 trạm dọc HN→Đà Nẵng (Vinh, Hà Tĩnh, Đồng Hới, Huế) + tọa độ + P_station + amenities | Google Maps tra tọa độ thủ công, không cần API key |
| Distance function | Hoàng Vĩnh Giang | `get_distance_km(lat1,lon1,lat2,lon2)` — dùng OSRM public API (`router.project-osrm.org`) hoặc Haversine nếu OSRM chậm | `requests` + OSRM |
| Route planner | Vũ Đức Duy | `plan_route()` trả đúng interface đã chốt — heuristic: duyệt trạm theo thứ tự dọc tuyến, chọn trạm tiếp theo sao cho SoC_arrive ≥ soc_hard, ưu tiên giảm tổng thời gian | Python thuần |
| LLM prompt | Trần Quang Quí | `generate_summary(plan_result) -> str` — nhận dict output của `plan_route()`, trả đoạn text tự nhiên + cảnh báo, giải thích ngắn gọn | Claude/OpenAI API, viết prompt + test với mock data |
| UI Streamlit | Nhữ Gia Bách | Form nhập (origin, destination, SoC%), slider SoC_comfort, hiển thị bảng trạm + SoC tại từng điểm + text LLM + warning banner + disclaimer | Streamlit, dùng mock `plan_route()` để dev song song |

---

#### Phase 2 — Tích hợp + fix (chiều 09/04, 14:00–18:00)

| Việc | Ai |
|------|----|
| Gắn `get_distance_km` vào `plan_route()` thay mock distance | Duy + Giang |
| Gắn `generate_summary()` vào UI | Quí + Bách |
| Test end-to-end: HN → Đà Nẵng, SoC 85% | Cả nhóm |
| Test edge case: SoC 30% → route không khả thi | Duy |
| Chỉnh wording cảnh báo + disclaimer | Sơn |
| Chạy thử demo script, chốt lời thuyết minh | Cả nhóm |

---

#### Checklist demo

- [ ] Nhập HN → Đà Nẵng, SoC 85% → ra lộ trình đúng, không vi phạm SoC_hard, buffer phần lớn ≥ SoC_comfort.
- [ ] Nhập SoC thấp (~25%) → hiện cảnh báo hoặc "route không khả thi" như spec.
- [ ] LLM output có ngôn ngữ tự nhiên, giải thích được vì sao dừng ở trạm đó, cảnh báo rủi ro rõ ràng.
- [ ] UI không crash với các input hợp lệ.
- [ ] Disclaimer hiển thị: "Bản demo sử dụng dữ liệu trạm và mô hình tiêu thụ đơn giản, chỉ dùng minh họa. Vui lòng không dùng để lập kế hoạch hành trình thực tế."

---

*SPEC draft — Track A VinFast — NHOMF2-C401 — VinUni A20 — AI Thực Chiến · 2026*