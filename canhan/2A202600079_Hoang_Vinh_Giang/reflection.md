# Individual reflection — Giang (API/Dev)

## 1. Role
Backend API Developer. Phụ trách tích hợp API tính khoảng cách (OSRM) và thiết kế hệ thống Fallback/Robustness tự cứu hộ.

## 2. Đóng góp cụ thể
- Viết client để gọi public API OSRM lấy thông định `distance_km` và `duration_min` trong `services/distance_service.py`.
- Xây dựng cơ chế vớt lỗi (Fallback system): Nếu API OSRM sập mạng hoặc timeout > 3 giây, ứng dụng sẽ không crash mà tự chuyển sang dùng công thức hình học Haversine.

## 3. SPEC mạnh/yếu
- Mạnh nhất: Fallback mechanism (cơ chế chống lỗi). Việc đảm bảo MVP luôn sống trong mọi buổi demo (kể cả no internet/API block) là điểm "cứu mạng" hoàn hảo.
- Yếu nhất: OSRM Public API thi thoảng bị rate-limit. Đáng ra nên setup thử một local OSRM server hoặc cache các requests trùng lặp dùng Redis.

## 4. Đóng góp khác
- Trực tiếp thao tác và điều khiển UI/Flow trong buổi test kịch bản Demo chính thức, mô phỏng các scenario happy-path và infeasible.

## 5. Điều học được
Trong làm sản phẩm thực tế, việc "Fail gracefully" (Xử lý lỗi một cách tinh tế) quan trọng không kém việc code happy-path. Trải nghiệm người dùng không bị gãy khi hệ thống bên dưới hạ tải.

## 6. Nếu làm lại
Sẽ làm thêm một cơ chế In-memory cache cho OSRM (lưu lại các cặp điểm đã tính trên dict) vì các trạm sạc là cố định, giúp tiết kiệm gần 90% call API thừa.

## 7. AI giúp gì / AI sai gì
- **Giúp:** AI support viết code xử lý bắt exception Timeout/ConnectionError gọn gàng và đưa ra công thức tính khoảng cách đường thẳng Haversine chính xác.
- **Sai:** AI không tính đến rate-limit của môi trường demo đông người, phải tự config lại timeout threshold.
