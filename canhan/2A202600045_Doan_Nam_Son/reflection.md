# Individual reflection — Sơn (Data Eng)

## 1. Role
Data Engineer. Phụ trách thiết kế Data Schema, parse JSON thô (`mock_stations.json`) và chuẩn hóa mọi dữ liệu về tiện ích trạm sạc cho LLM.

## 2. Đóng góp cụ thể
- Viết `utils/data_loader.py` cùng hàm `filter_active_stations()` để loại bỏ các trạm bảo trì.
- Viết `utils/formatters.py` (`format_amenities_for_llm`) để tự động dịch/mapping mã tiện ích từ tiếng Anh sang tiếng Việt (vd: "coffee" -> "Cà phê", "wifi" -> "Wi-Fi miễn phí").
- Inject trực tiếp text tiện ích vào hàm `to_dict()` của model `Station`, giúp các module khác tiêu thụ data dễ dàng hơn.

## 3. SPEC mạnh/yếu
- Mạnh nhất: Contract-first design. Việc thống nhất Data Schema (`Station`, `RouteStop`) ngay từ đầu giúp kết nối giữa team Data, Planner và AI rất mượt mà.
- Yếu nhất: Dữ liệu hiện tại nằm tĩnh trong JSON thay vì được gọi từ DB/API chuẩn. Tương lai nên thêm logic caching/fetch async.

## 4. Đóng góp khác
- Hỗ trợ review tọa độ trạm sạc đảm bảo không trạm nào "nằm giữa biển".
- Hỗ trợ xử lý lỗi Streamlit liên quan đến set/reset PYTHONPATH môi trường chạy.

## 5. Điều học được
Thiết kế dữ liệu không chỉ là chuyển JSON thành Object. Chuyển đổi (transform) dữ liệu ngay từ đầu cuối (data layer) thông minh (như việc dịch amenity) sẽ chia sẻ gánh nặng xử lý và giảm ảo giác (hallucination) cho LLM so với việc bắt LLM tự dịch.

## 6. Nếu làm lại
Sẽ sử dụng Pydantic để validate types thay vì chỉ dùng Dataclasses chuẩn nhằm báo lỗi chặt chẽ hơn khi mock data bị thiếu key.

## 7. AI giúp gì / AI sai gì
- **Giúp:** AI viết hàm dictionary mapping tiện ích cực kì nhanh và đầy đủ cho các case phổ biến.
- **Sai:** Ban đầu AI định nhồi logic dịch tiện ích vào thuật toán Planner, dẫn đến phá vỡ tính Single Responsibility - may mắn đã kịp can thiệp đưa ra file formatter riêng.
