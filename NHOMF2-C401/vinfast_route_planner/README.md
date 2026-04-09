# VinFast Route Planner & AI Assistant

Dự án này là hệ thống hoạch định lộ trình thông minh dành riêng cho xe điện VinFast, được tích hợp AI Agent chuyên biệt (sử dụng kiến trúc ReAct kết hợp Function Calling). Hệ thống giúp tính toán quãng đường, trạm sạc khả dụng, tính toán dung lượng pin và cung cấp Trợ lý ảo tư vấn trực tiếp cho người lái nhằm đảm bảo tính an toàn trong di chuyển (giữ SoC an toàn > 20%).

## 🎯 Tính năng nổi bật

- 🌍 **Bản đồ trực quan (Interactive Map)**: Ứng dụng bản đồ Leaflet theo dõi lộ trình và các điểm dừng trạm sạc thực tế.
- ⚡ **Hoạch định sạc pin thông minh (Route Planner Engine)**: Tính toán số điểm dừng, năng lượng tiêu thụ (giả lập) và lượng pin dự trữ tới từng trạm dọc đường.
- 🤖 **Trợ lý AI ReAct (Agentic Assistant)**: Chatbot tích hợp trực tiếp, có khả năng phân tích ngôn ngữ tự nhiên, tự động gọi API hệ thống để thiết lập lộ trình thay người dùng, và đưa ra cảnh báo nếu hành trình có rủi ro (pin quá thấp, không tìm thấy trạm sạc).
- 🧩 **UI/UX chuẩn Quốc tế**: Giao diện thiết kế theo chuẩn Dark Mode nguyên khối, thân thiện với màn hình trên xe (Automotive Display Interface).

## 🛠 Bộ công cụ (Tech Stack)

* **Frontend**: ReactJS, Vite, Tailwind CSS, Lucide React, Leaflet (React-Leaflet).
* **Backend**: FastAPI (Python), Uvicorn, Pydantic.
* **AI Agent**: OpenAI Standard API (hoạt động qua OpenRouter), LangChain-like Tooling implementation.
* **Architecture**: Client-Server, Agent-as-a-Service, RESTful API.

---

## 🚀 Hướng dẫn cài đặt và chạy ứng dụng

### 1. Chuẩn bị môi trường (Backend - Python)

Backend được viết bằng Python (FastAPI). Cần Node.js cho Frontend và Python 3.10+ cho Backend.

Mở Terminal và di chuyển vào thư mục dự án:
```bash
cd NHOMF2-C401/vinfast_route_planner
```

#### Tạo Môi trường Ảo (Khuyến nghị)
```bash
python3 -m venv .venv
source .venv/bin/activate  # (Với Windows sử dụng lệnh: .venv\Scripts\activate)
```

#### Cài đặt thư viện
```bash
pip install -r requirements.txt
```

#### Cấu hình Biến Môi Trường (API Keys)
Lặp bản sao file `.env.example` thành file `.env` và nhập API key của bạn:
```bash
cp .env.example .env
```
Mở file `.env` bằng Text Editor và điền `OPENROUTER_API_KEY` (hoặc cấu hình Base URL khác nếu dùng LLM cục bộ). 
Ví dụ:
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxx-xxx
OPENROUTER_MODEL=google/gemini-flash-1.5
```

#### Chạy Server Backend (FastAPI)
Đảm bảo bạn đang đứng ở thư mục `vinfast_route_planner`. Khởi động Uvicorn:
```bash
uvicorn app.api:app --reload --port 8001
```
*Backend sẽ chạy ở địa chỉ: `http://localhost:8001`. Tài liệu API Swagger kiểm thử có sẵn tại `http://localhost:8001/docs`.*

---

### 2. Khởi động Giao diện (Frontend - React)

Mở thêm một Tab Terminal mới và di chuyển vào thư mục Frontend:
```bash
cd NHOMF2-C401/vinfast_route_planner/frontend
```

#### Cài đặt gói NPM
```bash
npm install
```

#### Khởi động Server Vite
```bash
npm run dev
```
*Frontend sẽ chạy ở địa chỉ: `http://localhost:5173`. Bạn hãy mở link này trên Chrome/Edge để trải nghiệm ứng dụng.*

---

## 🏗 Kiến trúc thư mục

```text
vinfast_route_planner/
├── app/
│   └── api.py                   # Router & API Endpoints của hệ thống FastAPI
├── core/
│   ├── models.py                # Schema kiểm định dữ liệu Pydantic
│   └── route_planner.py         # Engine Thuật toán cốt lõi (tính pin, chặn trạm...)
├── data/
│   ├── mock_stations.json       # Cơ sở dữ liệu mô phỏng Trạm sạc VinFast
│   └── station_repository.py    # Tầng DAL đọc/ghi dữ liệu trạm sạc
├── services/
│   ├── agent_service.py         # AI Agent Loop (ReAct Logic + Tool Executor)
│   └── agent_tools.py           # Schema Tools (Function Calling) cấp cho LLM
├── frontend/                    # Thư mục chứa giao diện React + Vite
│   ├── src/
│   │   ├── components/          # Chứa ChatbotUI.jsx, RouteMap.jsx, AIAssistant.jsx
│   │   └── App.jsx              # Main Component gắn kết Layout
│   └── ...
├── requirements.txt             # Khai báo dependency backend
└── .env                         # Tệp cấu hình ẩn (Secret Keys)
```

## ⚠️ Lưu ý khi chạy Demo / Development

- Hãy đảm bảo bạn đã cung cấp đúng `OPENROUTER_API_KEY` ở file `.env`. Nếu không, AI Chatbot sẽ báo lỗi "Lỗi kết nối AI".
- Tính năng đo đạc khoảng cách vật lý của xe trên đường đang sử dụng các thông số khoảng cách Mockup tuyến tính phục vụ đánh giá UI/UX. Với môi trường Production, ứng dụng cần kết hợp Routing Component (như Mapbox Directions API hoặc Google Maps API).
