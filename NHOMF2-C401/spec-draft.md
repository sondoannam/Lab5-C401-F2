# SPEC draft — NHOMF2-C401

## Track: A — VinFast

## Problem statement

Chủ xe điện VinFast đi đường dài không biết dừng sạc ở đâu, khi nào, bao lâu — lo hết pin giữa đường, không biết trạm nào phù hợp, không tính được thời gian sạc. AI nhận điểm xuất phát, điểm đến, mức pin hiện tại → đề xuất lộ trình tối ưu (nhanh nhất trong điều kiện đảm bảo an toàn pin), vị trí trạm dừng sạc, thời lượng sạc dự kiến và cảnh báo rủi ro.

---

## Canvas draft

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Trả lời** | **User:** Chủ xe VinFast đi liên tỉnh, lo "range anxiety" — hết pin giữa đường. **Pain:** Phải tự tính quãng đường, tìm trạm sạc thủ công, không biết loại sạc nào phù hợp xe mình, không ước được thời gian sạc. **AI giải:** Nhận SoC hiện tại + điểm đến → tính tiêu thụ pin theo khoảng cách → đề xuất lộ trình đảm bảo SoC không rơi dưới buffer an toàn (15%) tại mọi điểm dừng. | **Khi AI sai:** Tính sai tiêu thụ pin → xe đến trạm với SoC thấp hơn dự kiến → nguy hiểm. **User biết sai:** Pin cạn sớm hơn dự đoán hoặc đến trạm thấy SoC thực < SoC dự kiến. **User sửa:** Báo "pin thực tế khi đến trạm" → AI hiệu chỉnh hệ số tiêu thụ. UI luôn hiển thị SoC dự kiến tại từng điểm dừng để user chủ động theo dõi và can thiệp. | **Cost:** Routing graph + LLM synthesize ~$0.005–0.01/request. **Latency:** <5s chấp nhận được. **MVP:** Data trạm sạc tĩnh (không real-time), 1 model xe VinFast, tiêu thụ pin tuyến tính theo khoảng cách — đủ để prototype 2 ngày hackathon. **Risk chính:** Mô hình tiêu thụ tuyến tính đơn giản — không xét tốc độ, địa hình, thời tiết → cần buffer an toàn đủ lớn. |

**Auto hay Augmentation?** Augmentation — AI đề xuất lộ trình + điểm sạc, user xem và quyết định đi theo. Không tự động book slot, không điều hướng real-time.

**Learning signal:**
- Explicit: user rate lộ trình sau chuyến đi
- Correction: user báo SoC thực tế khi đến trạm → hiệu chỉnh hệ số tiêu thụ `e` (kWh/km)
- Implicit: user có chọn lộ trình AI gợi ý hay tự chỉnh tay

---

## User Stories — 4 paths

| Path | Scenario | UI xử lý |
|------|----------|----------|
| AI đúng | User nhập: Hà Nội → Đà Nẵng, SoC 85%. AI gợi ý dừng sạc tại trạm Vinh, SoC dự kiến khi đến 22%, sạc 45 phút lên 80%, tổng hành trình 7h30 | Bản đồ lộ trình + danh sách trạm + SoC tại từng điểm + thời lượng sạc + tiện ích gần trạm |
| AI không chắc | Đoạn đường có chặng dài, SoC buffer mỏng (<20% khi đến trạm tiếp) | Cảnh báo vàng: "⚠️ SoC dự kiến khi đến trạm Hà Tĩnh chỉ còn ~18%. Nên sạc thêm tại Vinh." |
| AI sai | Mô hình tính thiếu tiêu thụ → SoC thực thấp hơn dự đoán | Nút "Báo SoC thực tế" → user nhập → lưu correction → AI hiệu chỉnh hệ số `e` cho lần sau |
| User mất tin | User không tin con số SoC dự kiến | Cho phép kéo chỉnh SoC\_min (buffer an toàn) lên cao hơn; AI tính lại lộ trình tức thì. Luôn hiển thị: "Xác nhận tình trạng trạm tại app VinFast trước khi khởi hành." |

---

## Eval metrics

- **Feasibility rate:** % route AI generate thỏa hard constraint SoC ≥ SoC\_min tại mọi node ≥ 100% (nếu vi phạm = bug nghiêm trọng)
- **SoC estimation error:** |SoC\_dự\_kiến − SoC\_thực\_tế| khi đến trạm ≤ 10% dung lượng pin
- **User correction rate:** % lượt user phải báo sai SoC → target < 20%
- **Threshold dừng:** SoC estimation error > 20% liên tục → review hệ số `e`
- **Kill criteria:** Có incident xe hết pin do route AI generate vi phạm SoC\_min → dừng ngay, audit toàn bộ

---

## Failure modes

| Failure | Xác suất | Impact | Mitigation |
|---------|----------|--------|------------|
| SoC thực thấp hơn dự kiến (tiêu thụ thực > mô hình tuyến tính) | Trung bình | Rất cao | Buffer SoC\_min 15% + cảnh báo vàng khi buffer < 20% |
| Không có route khả thi (chặng quá dài, không đủ trạm) | Thấp | Cao | Báo rõ "route không khả thi" + gợi ý điểm đến gần hơn hoặc xuất phát với SoC cao hơn |
| Trạm trong dataset đã đóng/offline (data tĩnh) | Trung bình | Cao | Disclaimer rõ "Xác nhận trạm còn hoạt động trước khi xuất phát" + user báo cáo trạm sai |
| User over-trust AI, không theo dõi SoC thực | Trung bình | Cao | UI luôn hiển thị SoC dự kiến tại từng điểm, nhắc user kiểm tra đồng hồ xe |

---

## ROI 3 kịch bản

| | Conservative | Realistic | Optimistic |
|---|---|---|---|
| User/tháng | 2,000 | 15,000 | 80,000 |
| Giá trị/user | Tiết kiệm 30 phút tìm trạm thủ công | Tránh 1 lần hết pin giữa đường (~2–3 triệu cứu hộ) | Tăng tin tưởng xe điện, giảm range anxiety toàn thị trường |
| Cost inference | ~$20/tháng | ~$150/tháng | ~$800/tháng |
| Benefit | Tăng NPS, giảm hotline ~10% | Giảm incident ~30%, tăng retention | Trở thành tính năng flagship VinFast app |
| Net | Hòa vốn | Dương rõ | Rất dương |

**Kill criteria:** SoC estimation error > 20% sau 1 tháng pilot → dừng, cải thiện mô hình tiêu thụ trước khi re-launch.

---

## Constraints & Assumptions (MVP)

| # | Assumption | Lý do |
|---|-----------|-------|
| C1 | Trạm sạc hoạt động **24/7**, waiting time = 0 (không model hàng chờ) | Hackathon, data tĩnh |
| C2 | Connector type tự tương thích — MVP chỉ có 1 model xe VinFast nên mặc định đúng chuẩn | 1 model cố định |
| C3 | Hệ thống cần **internet** để gọi OpenStreetMap và tra cứu dataset trạm; chưa xử lý offline | Scope 2 ngày |

---

## Mini AI spec

> **Scope MVP:** 1 model xe VinFast, tiêu thụ tuyến tính, data trạm tĩnh, mode duy nhất = Fastest-safe.

**Input:**

| Tham số | Mô tả | MVP |
|---------|-------|-----|
| SoC | % pin hiện tại | Bắt buộc |
| Điểm xuất phát + đích | Text hoặc tọa độ | Bắt buộc |
| Model xe | VinFast (1 model trong MVP) | Cố định, không chọn |
| SoC\_min | Buffer an toàn tối thiểu (mặc định 15%) | User có thể chỉnh |

**Output:**

| Kết quả | Mô tả |
|---------|-------|
| Danh sách trạm dừng | Tên + địa chỉ + thứ tự trên lộ trình |
| SoC dự kiến khi đến trạm | Tính từ `SoC_in − (e × d) / Q` |
| Loại sạc + công suất | AC/DC, `P_effective = min(P_vehicle, P_station)` |
| Thời lượng sạc | Tuyến tính: `t = (SoC_out − SoC_in) × Q / P_effective` |
| Ước tính chi phí | Hiển thị để so sánh, chưa tối ưu |
| Tiện ích gần trạm | Coffee, nhà hàng, WC — soft preference khi rank trạm |
| Cảnh báo rủi ro | SoC buffer thấp, chặng không khả thi |

**Architecture:**
- Routing: tính khoảng cách từng chặng (OpenStreetMap)
- Pin model: `SoC_out = SoC_in − (e × d) / Q`, hard check `SoC_out ≥ SoC_min` mọi node
- Trạm sạc: database tĩnh — vị trí, loại sạc, `P_station`, amenities
- LLM: synthesize kết quả thành ngôn ngữ tự nhiên + generate cảnh báo

**Confidence handling:**
- SoC buffer > 20%: gợi ý bình thường
- SoC buffer 15–20%: cảnh báo vàng "nên sạc thêm tại điểm trước"
- SoC buffer < SoC\_min: hard block — bắt buộc thêm điểm dừng hoặc báo không khả thi

**Future scope (không implement trong hackathon):**
- Nhiều model xe, profile tiêu thụ theo tốc độ/địa hình/thời tiết
- Time windows trạm, ước lượng hàng chờ real-time
- Multi-objective: time + cost + comfort
- Offline routing khi mất kết nối

**Data cần:** Database trạm sạc VinFast (tĩnh), thông số `Q, e, P_vehicle` của model xe, POI amenities gần trạm

---

## Phân công

### SPEC draft (hôm nay — 23:59 08/04)

| Thành viên | Phần phụ trách |
|------------|----------------|
| Đoàn Nam Sơn | Canvas + Failure modes |
| Hoàng Vĩnh Giang | User stories 4 paths + UX flow |
| Như Gia Bách | Eval metrics + Kill criteria |
| Trần Quang Quí | ROI 3 kịch bản + Mini AI spec |
| Vũ Đức Duy | Constraints & Assumptions + data research |

---

### Prototype — Build to demo (09/04)

> **Mục tiêu demo:** User nhập Hà Nội → Đà Nẵng + SoC 85% → hệ thống trả về danh sách trạm dừng, SoC dự kiến tại từng trạm, thời gian sạc, cảnh báo nếu có — hiển thị trên Streamlit.

#### Phase 0 — Chốt shared contracts (tối nay, trước 24:00 08/04) — *cả nhóm*

Trước khi ai code, cần thống nhất 3 thứ để mọi người làm song song:

**1. Schema mock dataset** (`stations.json`) — Sơn chuẩn bị, cả nhóm confirm:
```json
{
  "id": "vinh_01",
  "name": "Trạm VinFast Vinh",
  "lat": 18.6796, "lon": 105.6813,
  "p_station_kw": 50,
  "type": "DC",
  "amenities": ["coffee", "wc"]
}
```

**2. Thông số xe VinFast VF8** — Duy điền, cả nhóm dùng:
```python
VEHICLE = {
  "Q_kwh": 82,          # dung lượng pin
  "e_kwh_per_km": 0.2,  # tiêu thụ tuyến tính
  "p_vehicle_kw": 150,  # công suất sạc tối đa
  "soc_min": 0.15       # buffer an toàn
}
```

**3. Interface function Route planner → UI** — Duy + Bách confirm:
```python
def plan_route(origin, destination, soc_current, soc_min=0.15) -> dict:
    # returns:
    # {
    #   "stops": [{"station": {...}, "soc_arrive": 0.22, "charge_min": 45, "soc_depart": 0.80}],
    #   "feasible": True,
    #   "warnings": ["SoC thấp tại chặng Hà Tĩnh"]
    # }
```

---

#### Phase 1 — Build song song (sáng 09/04, target xong trước 14:00)

| Task | Thành viên | Output cụ thể | Dùng gì |
|------|-----------|---------------|---------|
| **Mock dataset** | Đoàn Nam Sơn | `stations.json` — 8–10 trạm dọc HN→Đà Nẵng (Vinh, Hà Tĩnh, Đồng Hới, Huế) + tọa độ + P_station + amenities | Google Maps tra tọa độ thủ công, không cần API |
| **Distance matrix** | Hoàng Vĩnh Giang | `get_distance_km(lat1,lon1,lat2,lon2)` — dùng OSRM public API (`router.project-osrm.org`) hoặc Haversine nếu OSRM chậm | `requests` + OSRM |
| **Route planner** | Vũ Đức Duy | `plan_route()` trả đúng interface đã chốt — greedy: duyệt trạm theo thứ tự, chọn trạm đầu tiên thỏa SoC_min | Python thuần |
| **LLM prompt** | Trần Quang Quí | `generate_summary(plan_result) -> str` — nhận dict output của `plan_route()`, trả đoạn text tự nhiên + cảnh báo | Claude API / OpenAI, viết prompt + test với mock data |
| **UI Streamlit** | Như Gia Bách | Form nhập (origin, destination, SoC%), hiển thị bảng trạm + SoC tại từng điểm + text LLM + warning banner | Streamlit, dùng mock `plan_route()` để dev song song |

> Giang: dùng **OSRM public** (`http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}`) — free, không cần API key. Fallback: Haversine (tính đường chim bay × 1.2).

---

#### Phase 2 — Tích hợp + fix (chiều 09/04, 14:00–18:00)

| Việc | Ai |
|------|-----|
| Gắn `get_distance_km` vào `plan_route()` thay mock distance | Duy + Giang |
| Gắn `generate_summary()` vào UI | Quí + Bách |
| Test end-to-end: HN → Đà Nẵng, SoC 85% | Cả nhóm |
| Test edge case: SoC 30% → route không khả thi | Duy |
| Chạy thử demo script, chốt lời thuyết minh | Cả nhóm |

---

#### Checklist demo (trước khi lên sân khấu)

- [ ] Nhập HN → Đà Nẵng, SoC 85% → ra lộ trình đúng, không vi phạm SoC_min
- [ ] Nhập SoC thấp (~25%) → hiện cảnh báo hoặc "route không khả thi"
- [ ] LLM output có ngôn ngữ tự nhiên, có cảnh báo rủi ro
- [ ] UI không crash với các input hợp lệ
- [ ] Disclaimer hiển thị: "Xác nhận trạm còn hoạt động trước khi xuất phát"

---

*SPEC draft — Track A VinFast — NHOMF2-C401 — VinUni A20 — AI Thực Chiến · 2026*
