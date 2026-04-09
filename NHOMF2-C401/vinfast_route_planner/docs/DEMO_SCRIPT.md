# Kịch bản Demo: VinFast EV Route Planner MVP

Kịch bản Demo này được thiết kế để nhóm trình bày sản phẩm hiệu quả nhất, đảm bảo show được toàn bộ các tính năng Robust (chống chịu lỗi), giao diện, và fallback. Thời lượng dự kiến: 5-7 phút. 

## 1. Giới thiệu (1 phút)
- **Người nói:** Sơn / Bách
- **Nội dung:** 
  - "Xin chào ban giám khảo, chúng em là NHÓM F2. Hôm nay, chúng em xin trình bày sản phẩm **VinFast EV Route Planner MVP** - giải pháp tự động lên kế hoạch và tìm trạm sạc tối ưu cho xe điện trên hành trình dài."
  - Nêu Pain-point: Nỗi lo "hết pin giữa đường" của người dùng xe điện.
  - Nhấn mạnh điểm sáng của sản phẩm: Hệ thống tính toán thông minh, dùng mô hình LLM để tóm tắt và đưa ra cảnh báo rủi ro về pin, đặc biệt là **khả năng chống chịu lỗi (Offline mode/Fallback)**.

## 2. Demo Ca Sử Dụng 1: Hành trình hoàn hảo (2 phút)
- **Thao tác UI (Giang):** 
  - Chọn Origin: `Hà Nội`
  - Chọn Destination: `Đà Nẵng`
  - Current SoC: `90%`, Comfort buffer: `20%`
  - Click `🚀 Plan route`.
- **Thuyết minh (Quí):** 
  - Đánh giá giao diện: "Giao diện tinh gọn, không có các nút thừa mứa thô kệch. Cảnh báo hiển thị rõ ràng trên đầu màn hình."
  - Bản đồ: "Giao diện dùng Folium tương tác thật. Đường nối liền mạch theo toạ độ OSRM, icon của trạm sạc được đổi sang chuẩn và rõ nét với thông tin công suất sạc."
  - Bảng dữ liệu: "Bảng bên dưới giúp hiển thị mức Pin Khi Đến và Khi Rời theo từng trạm. Các chặng nếu có pin dự kiến lúc tới dưới 20% sẽ được **tô viền đỏ báo động** tự động bằng DataFrame styling."
  - LLM Summary: "Tuân thủ chặt chẽ Response Format tối đa 60 từ. Siêu gọn nhẹ, mang tính chất tóm lược."

## 3. Demo Ca Sử Dụng 2: Hành trình cảnh báo rủi ro cao (1.5 phút)
- **Thao tác UI (Giang):**
  - Giữ vị trí nhưng kéo `Current SoC` xuống `10%`.
  - Click `🚀 Plan route`.
- **Thuyết minh (Duy):**
  - Màn hình sẽ từ chối Plan và báo Infeasible.
  - "Đây là điểm mạnh của thiết kế Robust của nhóm em. Không cố tình render bảng trống hoặc để app bị crash khi không thể nối trạm, hệ thống chặn đứng ngay lập tức với `st.error`."
  - Đọc hệ thống cảnh báo từ LLM: "LLM vẫn đưa ra lời báo lỗi lịch sự kèm hướng dẫn."

## 4. Demo Tính năng 3: Stress-Test / Fallback System (1.5 phút)
- **Thao tác UI:** (Chỉ cần chỉ tay vào phần đường chim bay nếu OSRM lỗi, hoặc mở source code phần `osrm_failed = True` trên chiếu).
- **Thuyết minh (Leader):**
  - "Trong thực tế, khi triển khai MVP ở các hội chợ công nghệ hoặc kết nối wifi kém, OSRM API có thể bị Timeout."
  - "Để Demo không chết giữa chừng, đội ngũ đã làm một thủ thuật **Fallback**. Nếu timeout > 3 giây, tự động vứt OSRM sang một bên và kẻ đường chim bay nối các toạ độ. Vẫn show được map, vẫn có tính toán toán học Haversine. App **không bao giờ Crash** trước mặt khách hàng."

## 5. Kết Lời & Q&A (1 phút)
- "Với chiến lược TDD (Test-Driven Development), bọn em tự tin logic tính toán SoC đạt tiêu chuẩn tối đa trước khi gắn lên UI. Cảm ơn anh/chị đã theo dõi."

---
*Tip khi run Demo:*
- **Luôn chạy `streamlit run app/showmap.py` một lần trước giờ pitch 5 phút** để model Load vào cache (`st.cache_data`) cho mượt, không bắt BGK chờ kết nối OpenRouter.
