# VinFast EV Trip Planning Assistant
## SPEC FINAL — NHOMF2-C401

**Đề tài / Topic:** Hệ thống hỗ trợ lập kế hoạch hành trình và trạm sạc cho chủ xe điện VinFast
**Cuộc thi:** Track A — VinFast · VinUni A20 · AI Thực Chiến 2026

**Thành viên thực hiện:**
- Đoàn Nam Sơn
- Hoàng Vĩnh Giang
- Nhữ Gia Bách
- Trần Quang Quí
- Vũ Đức Duy

---

## 1. Problem Statement

Chủ xe điện VinFast đi đường dài không biết dừng sạc ở đâu, khi nào, bao lâu — lo hết pin giữa đường, không biết trạm nào phù hợp, không tính được thời gian sạc.

**Giải pháp:** Hệ thống AI Agent nhận điểm xuất phát, điểm đến, mức pin hiện tại → lập lộ trình tối ưu (nhanh nhất trong điều kiện đảm bảo an toàn pin), hiển thị danh sách trạm dừng, SoC dự kiến, thời gian sạc, và cảnh báo rủi ro trên giao diện bản đồ tương tác. Người dùng có thể giao tiếp bằng ngôn ngữ tự nhiên qua chatbot tích hợp.

---

## 2. AI Product Canvas

| | Value | Trust | Feasibility |
|---|---|---|---|
| **Phân tích** | **User:** Chủ xe VinFast đi liên tỉnh, lo "range anxiety". **Pain:** Tự tính quãng đường, tìm trạm thủ công, không biết thời gian sạc. **AI giải:** Nhận SoC + điểm đến → tính tiêu thụ → đề xuất lộ trình đảm bảo SoC không dưới buffer tại mọi trạm. | **Khi sai:** Tính thiếu tiêu thụ → xe đến trạm với SoC thấp hơn dự kiến → nguy hiểm. **User phát hiện:** Pin cạn sớm hơn dự đoán. **Mitigation:** Cảnh báo vàng khi buffer mỏng; disclaimer cứng trên mọi màn hình; không dùng wording "đảm bảo" — chỉ dùng "ước tính", "dự kiến". | **Chi phí inference:** ~$0.005–0.01/request. **Latency:** <5s chấp nhận được. **MVP done:** Data trạm tĩnh (mock), 1 model xe VinFast VF8, tiêu thụ pin tuyến tính, không model queue/time window. |

**Auto hay Augmentation?**
Augmentation — AI đề xuất lộ trình, user xem bản đồ và quyết định. Không tự động điều hướng real-time, không book slot sạc.

**Learning signal (tầm nhìn dài hạn):**
- Explicit: user rate lộ trình sau chuyến đi.
- Correction: user báo SoC thực tế khi đến trạm → hiệu chỉnh hệ số tiêu thụ `e`.
- Implicit: user có chọn lộ trình AI gợi ý hay tự chỉnh.

---

## 3. User Stories — 4 Paths

| Path | Scenario | Hệ thống xử lý |
|------|----------|----------------|
| **AI đúng** | User chọn Hà Nội → Đà Nẵng, kéo slider pin 85%, nhấn "Lập Lộ Trình". AI tính 2–3 trạm dừng, tổng ~7h30. | Bản đồ hiện polyline + marker trạm, popup hiện SoC dự kiến + thời gian sạc. AI Dashboard hiện banner tổng quan + timeline chi tiết. Chatbot sẵn sàng trả lời câu hỏi tiếp theo. |
| **AI không chắc** | SoC buffer mỏng tại 1 chặng: SoC dự kiến đến trạm tiếp theo ~18%. | Route planner gắn cảnh báo vàng vào kết quả. AI Dashboard và chatbot đều highlight warning. User có thể chat "Buffer 30% thì sao?" để thử ngay. |
| **AI sai** | Mô hình tính thiếu tiêu thụ → SoC thực thấp hơn dự đoán. | Disclaimer cứng hiển thị tại mọi kết quả: "Dữ liệu demo là mock/tĩnh, các con số là ước tính." Chatbot nhắc kiểm tra đồng hồ xe tại mỗi trạm. |
| **User mất tin** | User không tin số liệu SoC sau nhiều lần lệch. | Slider SoC_comfort trên form cho phép tăng buffer ngay. Chatbot cho phép thử với các mức pin/buffer khác nhau trong hội thoại. Disclaimer cố định ở mọi kết quả. |

---

## 4. Eval Metrics

*(Định nghĩa cho tầm nhìn sản phẩm; MVP dùng để sanity-check.)*

| Metric | Ngưỡng | Mức độ |
|--------|--------|--------|
| **Feasibility rate (hard safety)** | SoC ≥ SoC_hard tại mọi node = 100% | **Kill criteria** — vi phạm là bug nghiêm trọng |
| **SoC estimation error** | \|SoC_dự_kiến − SoC_thực\| ≤ 10% (median) | Trung hạn — log manual trong MVP |
| **User correction rate** | < 20% lượt user báo route sai | Sau khi product trưởng thành |
| **Threshold review** | SoC error > 20% liên tục → review `e` và margin | Ongoing |
| **Kill criteria (safety)** | Có incident xe hết pin do route vi phạm SoC_hard → dừng ngay, audit toàn bộ | Hard stop |

---

## 5. Failure Modes

| Failure | Xác suất (MVP) | Impact | Mitigation |
|---------|----------------|--------|------------|
| SoC thực thấp hơn dự kiến (tiêu thụ > tuyến tính) | Trung bình | Rất cao | `e` conservative cho tuyến demo; SoC_hard = 10%; SoC_comfort mặc định 20%; cảnh báo vàng khi buffer < 20%; disclaimer rõ không dùng cho điều kiện cực đoan. |
| Không có route khả thi (chặng quá dài) | Thấp–Trung | Cao | Báo rõ "Route không khả thi với mức pin hiện tại" + gợi ý: (1) xuất phát pin cao hơn; (2) điểm đến gần hơn. Không hack route nguy hiểm. |
| Trạm trong dataset đã đóng/offline | Trung bình | Cao | Disclaimer cứng trên mọi kết quả: "Vui lòng xác nhận trạm còn hoạt động trên app VinFast chính thức trước khi xuất phát." |
| User over-trust AI | Trung bình | Cao | UI luôn hiển thị SoC dự kiến tại từng điểm + nhắc kiểm tra đồng hồ xe. Không dùng wording "đảm bảo". |
| Route sát SoC_hard ≥ 2 chặng liên tiếp | Thấp | Cao | Cảnh báo đỏ "Hành trình sát giới hạn, cân nhắc chia nhỏ chuyến đi." Ưu tiên route thay thế an toàn hơn nếu có. |
| OSRM public server timeout | Trung bình | Thấp (UX only) | `POST /api/plan` gọi OSRM để lấy geometry cho map. Nếu timeout → fallback Haversine straight-line coords. Route planner không phụ thuộc OSRM. |
| LLM out-of-domain response | Thấp | Thấp–Trung | System prompt domain restriction: AI từ chối câu hỏi không liên quan đến VinFast/EV, trả lời bằng tiếng Việt lịch sự. |

---

## 6. ROI — 3 Kịch bản

| | Conservative | Realistic | Optimistic |
|---|---|---|---|
| User/tháng | 2,000 | 15,000 | 80,000 |
| Giá trị/user | Tiết kiệm 30 phút tìm trạm thủ công | Tránh 1 lần hết pin (~2–3 triệu cứu hộ) | Tăng tin tưởng xe điện, giảm range anxiety toàn thị trường |
| Cost inference | ~$20/tháng | ~$150/tháng | ~$800/tháng |
| Benefit | Tăng NPS, giảm hotline ~10% | Giảm incident ~30%, tăng retention | Trở thành tính năng flagship VinFast app |
| Net | Hòa vốn | Dương rõ | Rất dương |

**Kill criteria (business):** SoC estimation error > 20% sau 1 tháng pilot nội bộ → dừng, cải thiện mô hình tiêu thụ trước khi rollout.

---

## 7. Constraints & Assumptions

### Vehicle Config (VinFast VF8)

```python
VEHICLE = {
    "model": "VinFast VF8",
    "Q_kwh": 82,
    "e_kwh_per_km": 0.22,       # conservative cho tuyến demo
    "p_vehicle_kw": 150,
    "soc_hard": 0.10,            # ngưỡng tuyệt đối — không vi phạm
    "soc_comfort_default": 0.20  # buffer kế hoạch mặc định
}
```

### MVP Assumptions

| # | Assumption | Lý do |
|---|------------|-------|
| C1 | 1 model xe VinFast VF8, tham số cố định | Đơn giản hóa, phù hợp hackathon |
| C2 | Energy tuyến tính: `E = e × d` | Model SoC 1 chiều, dễ implement |
| C3 | Hai ngưỡng: SoC_hard = 10%, SoC_comfort = 20% | Tăng safety, vẫn dễ implement |
| C4 | Dataset trạm mock/tĩnh — 24/7, không hỏng, không queue | Không có data real-time trong hackathon |
| C5 | Connector luôn tương thích (1 model xe) | Loại bỏ dimension connector |
| C6 | Thời gian sạc tuyến tính, `P_eff = min(P_vehicle, P_station)` | Không model charging curve >80% |
| C7 | `t_drive` tính từ Haversine hoặc OSRM khi có geometry | Bỏ qua traffic/time window |
| C8 | Không model time windows, capacity, queue | Bù bằng disclaimer UI |
| C9 | SoC và vị trí chọn từ form/chat trong demo | Bù bằng `e` conservative + SoC_hard |
| C10 | Tối ưu "Fastest-safe" duy nhất | Focus 1 objective trong MVP |

---

## 8. Mini AI Spec

### Input

| Tham số | Mô tả | MVP |
|---------|-------|-----|
| Điểm đi / đến | Tên thành phố | Dropdown trên form; hoặc tự nhiên qua chatbot |
| SoC hiện tại | 0–100% | Slider trên form; hoặc trích xuất từ tin nhắn |
| SoC_comfort | Buffer an toàn (default 20%) | Cố định trong form (dùng mặc định); điều chỉnh qua chat |

### Output

| Kết quả | Mô tả |
|---------|-------|
| Danh sách trạm dừng | Tên + tọa độ + thứ tự — hiển thị trên map marker và timeline |
| SoC dự kiến khi đến trạm | `SoC_arrive = SoC_prev − (e × d) / Q` — popup trên map |
| SoC dự kiến khi rời trạm | Sau khi sạc lên target — popup trên map |
| Thời gian sạc | `t_charge = (SoC_depart − SoC_arrive) × Q / P_eff` — popup + timeline |
| Tổng thời gian hành trình | `Σ(t_drive + t_charge)` — AI strategy banner |
| Tiện ích gần trạm | Coffee, nhà hàng, WC — mock data, popup trên map |
| Cảnh báo | Vàng (buffer mỏng) / Đỏ (route không khả thi) — chatbot + timeline |
| Bản đồ lộ trình | Polyline + marker trên React-Leaflet map, OSRM geometry hoặc Haversine fallback |

### Architecture (Đã implement)

```
[React Frontend] — Vite + TailwindCSS + React-Leaflet
├── RouteMap.jsx      — Form (origin, destination, SoC slider) + Interactive Map
│     POST /api/plan  ─────────────────────────────────────────────────────────┐
│                                                                               ↓
└── AIAssistant.jsx   — Strategy banner + Timeline + ChatbotUI             [FastAPI]
      POST /api/chat  ─────────────────────────────────────────────────────  app/api.py
                                                                               │
                                                        ┌──────────────────────┴──────────────────────┐
                                                        ↓                                             ↓
                                              /api/plan                                        /api/chat
                                    run_trip_planner_workflow()                         chat_with_agent()
                                    [tool_workflow.py]                                  [agent_service.py]
                                    ├── planner_tool()                                  ├── LLM (OpenRouter)
                                    │     └── route_planner.py (DP optimal)             │     tool_choice=auto
                                    ├── validate_plan_tool()                             └── execute_tool()
                                    └── summary_tool()                                        └── plan_ev_route
                                          └── LLM tóm tắt                                          → run_trip_planner_workflow()
```

**Plan flow:** `POST /api/plan` → `run_trip_planner_workflow` → `planner_tool → validate_plan_tool → summary_tool` → JSON response với geometry, stops, warnings  
**Chat flow:** `POST /api/chat` → `chat_with_agent` → LLM gọi `plan_ev_route` tool nếu cần → `run_trip_planner_workflow` → LLM synthesize → response text + `workflow_data`

### Confidence Handling

| SoC_arrive | Trạng thái | UI |
|------------|------------|-----|
| ≥ SoC_comfort (20%) | OK | Popup trên map hiển thị bình thường |
| SoC_hard ≤ SoC_arrive < SoC_comfort | Yellow warning | Chatbot + banner "⚠️ Buffer mỏng, cân nhắc dừng sớm hơn" |
| < SoC_hard (10%) | Hard block | Route bị reject — báo không khả thi + gợi ý tăng SoC xuất phát |

---

## 9. What's Done vs. Not Done

### ✅ Đã hoàn thành (MVP)

- Core planning logic: DP optimal, đảm bảo SoC_hard tại mọi node
- Validate + cảnh báo tự động (vàng / đỏ / route không khả thi)
- React + FastAPI split-view UI: bản đồ trái + AI dashboard phải
- Interactive Leaflet map: tất cả trạm sạc làm POI, polyline lộ trình, marker start/end/stop
- Popup chi tiết trạm: trạng thái, công suất, chỗ trống, SoC dự kiến, thời gian sạc
- AI strategy banner + timeline danh sách trạm dừng
- Chatbot AI tích hợp — giao tiếp tự nhiên, gọi tool tự động khi cần
- OSRM geometry với Haversine fallback
- Toggle AI Dashboard panel (Observation Mode)
- Disclaimer cứng trên mọi kết quả

### ⚠️ Chưa làm (ngoài scope MVP)

- Nhiều lộ trình thay thế (fastest / safest / cheapest)
- Dữ liệu trạm real-time (trạng thái, hàng chờ, giờ mở cửa)
- Nhiều model xe VinFast
- Charging curve phi tuyến (>80% SoC)
- Feedback loop: user báo SoC thực → hiệu chỉnh `e`
- Multi-objective routing (time + cost + comfort)
- Offline routing / re-routing real-time

---

## 10. Demo Script (Tuyến chuẩn)

| Bước | Thao tác | Expected output |
|------|----------|----------------|
| 1 | Chọn Hà Nội → Đà Nẵng, kéo slider 85%, nhấn "Lập Lộ Trình" | Polyline xanh xuất hiện trên map, marker trạm dừng, AI banner hiện số lần sạc + tổng thời gian |
| 2 | Click marker trạm trên map | Popup hiện SoC dự kiến khi đến, thời gian sạc, tiện ích |
| 3 | Chat: "Trạm Vinh có tiện ích gì?" | AI trả lời bằng tiếng Việt, không mở form lại |
| 4 | Chat: "Nếu pin 30% thì sao?" | AI tính lại — có thể thêm trạm hoặc cảnh báo |
| 5 | Chọn Hà Nội → Đà Nẵng, kéo slider 20%, nhấn "Lập Lộ Trình" | Cảnh báo hoặc "Route không khả thi" |
| 6 | Nhấn nút Observation Mode | AI Dashboard ẩn đi, map fullscreen |

---

## 11. Phân công

| Thành viên | Đóng góp | Output cụ thể |
|------------|----------|---------------|
| **Đoàn Nam Sơn** | Canvas · Constraints & Assumptions · Failure modes · Mock dataset | `spec-final.md` phần 2,5,7 · `data/mock_stations.json` |
| **Hoàng Vĩnh Giang** | User stories 4 paths · UX flow · Distance function | `spec-final.md` phần 3 · `services/distance_service.py` |
| **Nhữ Gia Bách** | Eval metrics · Kill criteria · ROI · Timeline component | `spec-final.md` phần 4,6 · `frontend/src/components/Timeline.jsx` |
| **Trần Quang Quí** | Mini AI spec · Prompt design · Agent tools schema | `spec-final.md` phần 8 · `services/agent_tools.py` |
| **Vũ Đức Duy** | Route planner · Vehicle params · FastAPI API · RouteMap · Tool workflow | `core/route_planner.py` · `core/config.py` · `app/api.py` · `services/tool_workflow.py` · `frontend/src/components/RouteMap.jsx` |

---

*SPEC final — Track A VinFast — NHOMF2-C401 — VinUni A20 — AI Thực Chiến · 2026*
