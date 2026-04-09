# Cấu trúc Lệnh (Prompt) Chuẩn Quốc Tế: Sprint C - Tích hợp, Xử lý Corner Cases (Robustness)

Bạn là một chuyên gia Prompt Engineering. Dưới đây là tài liệu hướng dẫn và mẫu prompt chuẩn quốc tế dành riêng cho các tác vụ của **Duy (Algorithmic / Route Planner)** trong **Sprint C**.

## 1. Tổng quan về cấu trúc một Prompt chuẩn
Một lệnh (prompt) tối ưu không chỉ giải quyết bài toán cơ bản mà còn phải trù tính được các rủi ro hệ thống (edge cases). Ở giai đoạn hoàn thiện (Sprint C), cấu trúc prompt cần nhấn mạnh vào việc xử lý các ràng buộc (constraints) và điều kiện lỗi.

## 2. Phân tích chi tiết từng thành phần
- **Role / System:** Yêu cầu AI hoạt động với tư duy của System Integrator & QA Engineer, nơi trọng tâm là sự ổn định (Robustness) chứ không chỉ là tính năng.
- **Task / Instruction:** Hướng dẫn AI cách vá các lỗ hổng của dự án, đặc biệt là các Corner Cases có thể làm sụp hệ thống (Kill Criteria).
- **Context:** Bối cảnh giai đoạn cuối (Final Polish) chuẩn bị cho buổi Demo Hackathon. Chấp nhận các sự đánh đổi ("Done is better than perfect").
- **Input data:** Giới thiệu các hàm hoặc dữ liệu do thành viên khác viết (như API OSRM của Giang) để tiến hành gắn kết.
- **Output format:** Trả về kết quả có khả năng xử lý ngoại lệ (Exception Handling) và cảnh báo thân thiện với người dùng UI.

## 3. Lệnh (Prompt) hoàn chỉnh cho Task của Duy (Sprint C)
*Ghi chú: Sử dụng prompt này để yêu cầu AI tích hợp logic OSRM thực tế và xử lý các kịch bản cạn pin cho hệ thống VinFast Route Planner.*

***

**[START OF PROMPT]**

**Role / System:**
Bạn là một System Integrator và Backend Developer giàu kinh nghiệm. Bạn có tư duy "phòng thủ" (Defensive programming), luôn dự đoán các kịch bản (edge cases) và xử lý ngoại lệ khéo léo để hệ thống không bao giờ crash bất ngờ trên môi trường sản xuất.

**Context:**
Ứng dụng VinFast Route Planner của chúng ta đang bước vào Sprint C: Tích hợp và Xử lý sự cố. Hiện mã nguồn đã tích hợp việc chọn trạm sạc và tính thời gian sạc cơ bản. Nhiệm vụ bây giờ là loại bỏ khoảng cách giả (mock distance), thay bằng API thực, đồng thời ngăn chặn các kịch bản tồi tệ nhất ảnh hưởng tới chuyến đi thực tế của người dùng. Ưu tiên: "Done is better than perfect". Hệ thống phải chạy thông suốt cho buổi Demo.

**Task / Instruction:**
Hãy tái cấu trúc và bổ sung các hàm xử lý cho `plan_route` với 2 nhiệm vụ cốt lõi:
1. Gắn hàm `get_distance_km` thực tế (đã được Dev tên Giang viết) vào luồng tính toán thay cho khoảng cách mock.
2. Xử lý 2 Corner Cases quan trọng:
   - **Corner Case 1 (Chặng đi quá xa):** Nếu chặng giữa hai trạm liên tiếp quá xa dẫn đến tiêu thụ cạn pin ($SoC_{arrive} < 0.10$ / $10\%$), hàm bắt buộc phải bắt lỗi, thiết lập `feasible = False`, và tạo ra một cảnh báo mang nhãn dán đặc biệt cảnh báo nghiêm trọng vào mảng `warnings`. (Điều này trigger Banner Đỏ trên UI).
   - **Corner Case 2 (SoC ban đầu thấp):** Nếu người dùng khởi tạo $SoC_{current} < 0.30$ (30%), hàm phải tự động chèn một cờ `warnings` gợi ý trạm sạc gần nhất để UI có thông điệp báo động. Route có thể "không khả thi" ngay lập tức nếu trạm đầu tiên xa hơn giới hạn pin.
3. Tích hợp giải pháp Fallback:
   - Viết cơ chế Try-Except. Nếu hàm `get_distance_km` gặp lỗi kết nối (Timeout, API OSRM hỏng), tự động fallback dùng khoảng cách Haversine (đường chim bay $\times 1.3$) nhằm duy trì khả năng demo.

**Input data:**
- Giả định hàm do Giang cung cấp có chữ ký: `get_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float`.
- Tọa độ các trạm đã có trong danh sách trạm đầu vào.

**Output format:**
- Xuất đoạn code tích hợp Python hoàn thiện cuối cùng.
- Trả về mã nguồn tối giản, tuân thủ DRY, KISS. KHÔNG có bất kỳ mã bình luận dư thừa nào. Yêu cầu mã xử lý ngoại lệ duyên dáng, trả dictionary với `feasible=False` và `warnings=["..."]` phù hợp.
- Viết 1 test case giả lập OSRM API lỗi để xác nhận hàm Fallback chạy thành công.

**[END OF PROMPT]**

***

## 4. Các thực hành tốt nhất (Best Practices) cần tuân thủ
- **Lập trình phòng ngự (Defensive Programming):** Prompt yêu cầu rõ tính năng fallback khi gọi API ngoại vi, giúp ứng dụng không sụp lây (cascading failure).
- **Phân tách Ràng buộc (Decoupling Constraints):** Việc trả về `feasible = False` cùng danh sách `warnings` thay vì thả một Error/Exception trực tiếp (Raise Exception) ra ngoài hệ thống giúp bên Client (Bách làm UI) kiểm soát view một cách an toàn và nhẹ nhàng.
- **Tập trung vào giá trị (Value Driven):** Ở Sprint C, giá trị lớn nhất là "Demo không chết". Prompt truyền tải đúng triết lý của TPM: đảm bảo sự ổn định.
