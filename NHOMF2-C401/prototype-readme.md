# Prototype — VinFast EV Trip Planning Assistant

## Mô tả

Hệ thống lập kế hoạch hành trình xe điện VinFast VF8 tích hợp AI Agent. Giao diện split-view: bên trái là bản đồ tương tác (chọn điểm đi/đến, hiển thị toàn bộ trạm sạc, vẽ lộ trình), bên phải là AI Dashboard (chatbot tự nhiên, timeline trạm dừng, tóm tắt chiến lược sạc). Backend FastAPI xử lý route planning và agentic loop — AI Agent tự gọi tool tính lộ trình tối ưu, trả về SoC tại từng trạm, thời gian sạc, cảnh báo rủi ro.

## Level: Working Prototype ✅

- React + Vite frontend với dark mode automotive-inspired UI
- FastAPI backend với AI Agent loop (Function Calling qua OpenRouter API)
- Route planner engine thuật toán DP tối ưu — không mock, chạy thật
- Interactive Leaflet map với tất cả trạm sạc làm POI, polyline lộ trình on-demand
- Demo live được với ChatbotUI + Timeline + RouteMap split view

---

## Links

| Mục | Link |
|-----|------|
| **Frontend source** | `NHOMF2-C401/vinfast_route_planner/frontend/` |
| **Backend source** | `NHOMF2-C401/vinfast_route_planner/app/api.py` |
| **AI Agent** | `NHOMF2-C401/vinfast_route_planner/services/agent_service.py` |
| **SPEC final** | `spec_final.md` trong repo nhóm |

---

## Demo nhanh

### 1. Backend (FastAPI)
```bash
cd NHOMF2-C401/vinfast_route_planner
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # điền OPENROUTER_API_KEY
uvicorn app.api:app --reload --port 8001
```

### 2. Frontend (React + Vite)
```bash
cd NHOMF2-C401/vinfast_route_planner/frontend
npm install
npm run dev
```

Mở **`http://localhost:5173`** trên Chrome/Edge. Thử ngay: chọn **Hà Nội → Đà Nẵng**, pin **85%**, bấm **Lập Lộ Trình** — hoặc gõ vào chat AI bên phải.

---

## Tools & API đã dùng

| Thành phần | Tool / API |
|---|---|
| LLM | OpenRouter API (configurable model trong `.env`) |
| Function Calling | OpenAI-compatible tool schema qua OpenRouter |
| Route geometry | OSRM public API (`router.project-osrm.org`) + Haversine fallback |
| Map render | React-Leaflet + CARTO dark tile layer |
| UI | React 18 + Vite + Tailwind CSS + Lucide React |
| Backend API | FastAPI + Uvicorn + Pydantic |
| Data trạm | Mock JSON tĩnh (`data/mock_stations.json`) |
| Distance | Haversine (route planning) + OSRM (geometry on-demand) |

---

## Kiến trúc

```
frontend/src/
├── App.jsx                  # Split-view layout (RouteMap 50% + AIAssistant 50%)
└── components/
    ├── RouteMap.jsx          # Leaflet map + input form (origin, destination, SoC slider)
    ├── AIAssistant.jsx       # AI strategy banner + Timeline + ChatbotUI
    ├── Timeline.jsx          # Timeline trạm dừng dọc lộ trình
    └── ChatbotUI.jsx         # Chatbot tương tác tự nhiên

app/api.py                   # FastAPI endpoints: /api/plan, /api/stations, /api/chat
services/
├── agent_service.py         # AI Agent Loop (ReAct + Tool Executor)
└── agent_tools.py           # Tool schema (Function Calling) cấp cho LLM
core/route_planner.py        # Route planning engine (DP optimal)
data/mock_stations.json      # Mock dataset trạm sạc VinFast
```

**API flow:** `POST /api/plan` → `agent_service` → tool calls → `route_planner.py (DP)` → JSON response  
**Chatbot flow:** `POST /api/chat` → `agent_service` → LLM (tool_choice=auto) → execute tool nếu cần → LLM synthesize → response

---

## Tính năng đã có

| Tính năng | Trạng thái |
|---|---|
| Split-view: bản đồ trái + AI dashboard phải | ✅ |
| Interactive Leaflet map (dark mode, CARTO tile) | ✅ |
| Hiển thị tất cả trạm sạc dưới dạng POI trên map | ✅ |
| Popup chi tiết trạm: trạng thái, công suất, chỗ trống | ✅ |
| Form nhập điểm đi/đến (dropdown) + SoC slider | ✅ |
| Route polyline + auto-fit bounds | ✅ |
| Marker điểm xuất phát, điểm đến, trạm dừng sạc | ✅ |
| Popup trạm dừng: SoC dự kiến, thời gian sạc | ✅ |
| AI strategy banner: số lần sạc, tổng thời gian | ✅ |
| Timeline danh sách trạm dừng dọc lộ trình | ✅ |
| Chatbot AI tương tác tự nhiên | ✅ |
| Route planner (DP optimal) + cảnh báo rủi ro | ✅ |
| Toggle AI Dashboard panel (Observation Mode) | ✅ |
| Disclaimer mock data | ✅ |

---

## Giới hạn (MVP assumptions)

- Dữ liệu trạm **mock/tĩnh** — không phản ánh trạng thái thực tế
- 1 model xe duy nhất: VinFast VF8 (`Q=82kWh`, `e=0.22kWh/km`)
- Energy consumption **tuyến tính** — không xét tốc độ, địa hình, thời tiết
- Chỉ tối ưu **Fastest-safe** — chưa có multi-objective (cost, comfort)
- Không model time window, capacity, hàng chờ trạm
- **Không dùng để lập kế hoạch hành trình thực tế** — chỉ minh họa

---

## Phân công

| Thành viên | Phần | Output cụ thể |
|---|---|---|
| **Đoàn Nam Sơn** | Canvas · Constraints · Failure modes · Mock dataset | `spec_final.md` phần 1,4 · `data/mock_stations.json` |
| **Hoàng Vĩnh Giang** | User stories 4 paths · UX flow · Distance function | `spec_final.md` phần 2 · `services/distance_service.py` |
| **Nhữ Gia Bách** | Eval metrics · ROI · Timeline component | `spec_final.md` phần 3,5 · `frontend/src/components/Timeline.jsx` |
| **Trần Quang Quí** | Mini AI spec · Prompt design · Agent tools | `spec_final.md` phần 6 · `services/agent_tools.py` |
| **Vũ Đức Duy** | Route planner · Vehicle params · FastAPI backend · RouteMap | `core/route_planner.py` · `core/config.py` · `app/api.py` · `frontend/src/components/RouteMap.jsx` |

---

*NHOMF2-C401 — Track A VinFast — VinUni A20 — AI Thực Chiến · 2026*
