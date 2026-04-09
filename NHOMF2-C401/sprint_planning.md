
-----

## 🕒 Sprint A: Core Engine & Data Contract (11:00 - 13:00)

**Mục tiêu:** Xây dựng "xương sống" cho hệ thống. Mọi người phải thống nhất được Data Schema.

| Thành viên | Vai trò | Atomic Tasks (30-60m mỗi task) | Definition of Done (DoD) |
| :--- | :--- | :--- | :--- |
| **Sơn** | **Data Eng** | 1. Viết `utils/data_loader.py` để parse `mock_stations.json`. <br> 2. Implement hàm `filter_active_stations()` loại bỏ các trạm bảo trì. | Hàm trả về `list[dict]` sạch, không lỗi khi thiếu trường dữ liệu. |
| **Giang** | **API/Dev** | 1. Viết `services/osrm_client.py` gọi OSRM public API. <br> 2. Xử lý timeout và try-catch cho API (đề phòng mạng lag). | Hàm `get_route_info(p1, p2)` trả về `(distance_km, duration_min)`. |
| **Duy** | **Algorithmic**| 1. Implement công thức tiêu thụ: $SoC_{arrive} = SoC_{prev} - \frac{e \times d}{Q}$. <br> 2. Build vòng lặp Greedy chọn trạm kế tiếp thỏa mãn $SoC > SoC_{hard}$. | `plan_route()` chạy thông suốt với dữ liệu giả định (mock distance). |
| **Quí** | **AI/LLM** | 1. Viết `templates/prompt_v1.txt` (System Prompt) chứa Vehicle Params (VF8). <br> 2. Build hàm `format_planner_output_for_llm(data)` để chuyển đổi Dict thành String sạch. | LLM nhận được một đoạn text mô tả chặng đi cực kỳ súc tích. |
| **Bách** | **Frontend** | 1. Dựng Layout 2 cột: Sidebar (Inputs) và Main (Map/Results placeholder). <br> 2. Setup `st.session_state` để lưu trữ lộ trình giữa các lần re-render. | UI hiển thị được các Slider và nút "Tính toán" mà không crash. |

-----

## 🕒 Sprint B: Intelligence & Visualization (14:00 - 16:00)

**Mục tiêu:** Chuyển đổi dữ liệu thô thành thông tin có ích cho người dùng.

  * **Duy (Planner):** Thêm logic tính thời gian sạc tuyến tính: $t_{charge} = \frac{(SoC_{target} - SoC_{arrive}) \times Q}{P_{effective}}$, trong đó $P_{effective} = \min(P_{vehicle}, P_{station})$.
  * **Quí (AI):** Cấu hình LLM trả về JSON format (hoặc Markdown chuẩn) để hiển thị các "Safety Warnings" nổi bật.
  * **Bách (UI):** \* Tích hợp `streamlit-folium` để vẽ Marker cho các trạm dừng.
      * Vẽ đồ thị diện tích (Area Chart) thể hiện SoC giảm dần theo km và "nhảy" lên khi sạc.
  * **Sơn (Data):** Trích xuất `amenities` từ JSON để làm nội dung bổ trợ cho Quí (Ví dụ: "Dừng ở đây có Coffee cho bạn nghỉ ngơi").

-----

## 🕒 Sprint C: Robustness & Final Polish (16:00 - 18:00)

**Mục tiêu:** Xử lý lỗi (Edge cases) và chuẩn bị kịch bản Demo.

### 🛡️ Corner Case Checklist (The "Kill Criteria")

1.  **Chặng đường quá xa:** Nếu khoảng cách giữa 2 trạm \> tầm hoạt động của xe ($SoC < 10\%$), UI phải hiện **Banner Đỏ** cảnh báo ngay lập tức.
2.  **SoC ban đầu thấp:** Nếu User nhập $SoC < 20\%$, LLM phải gợi ý trạm sạc gần nhất ngay trong bán kính 5-10km.
3.  **OSRM Down:** Giang chuẩn bị sẵn hàm fallback dùng **Haversine Distance** (khoảng cách đường chim bay $\times 1.3$) để demo không bị gián đoạn.

### 🎨 Final Polish

  * **Bách:** Thêm `st.expander` cho các thông số kỹ thuật để UI gọn gàng.
  * **Sơn:** Rà soát lại tọa độ các trạm trong `stations.json` đảm bảo không có trạm nào "nằm giữa biển".
  * **Quí:** Kiểm tra Tone of Voice của AI, đảm bảo dùng đúng thuật ngữ VinFast (ví dụ: "Siêu trạm sạc", "Trạm sạc nhanh").

-----

**TPM Note:** Chúng ta chỉ còn vài tiếng. Ưu tiên **"Done is better than perfect"**. Nếu logic sạc quá phức tạp, hãy giữ nó tuyến tính (Linear) như Spec đã định.
