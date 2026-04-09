# Individual reflection — Duy (Algorithmic)

## 1. Role
Thuật toán (Algorithmic / Planner) & dựng UX/UI (UX/UI Strategist).
Phụ trách engine định tuyến cốt lõi, tìm trạm đỗ thỏa mãn giới hạn pin cứng & mềm, đồng thời hoạch định chiến lược trải nghiệm người dùng, làm cầu nối đưa raw data thuật toán lên giao diện (UI) thân thiện, an toàn.

## 2. Đóng góp cụ thể
- Code logic tính toán trong `core/route_planner.py`.
- Xây dựng công thức tiêu thụ: $SoC_{arrive} = SoC_{prev} - \frac{e \times d}{Q}$ với mức tiêu thụ tuyến tính.
- Xây dựng vòng lặp giải thuật Greedy để nhảy trạm sạc kế tiếp mà vẫn thỏa mãn mức $SoC > SoC_{hard}$.
- Tính toán thời gian sạc ước tính $t_{charge}$ theo công suất tương đối giữa điểm sạc và phương tiện.
- Đóng vai trò Thiết kế Sản phẩm (Product Designer), biên soạn chiến lược `UX_UI_DESIGN_STRATEGY.md` phân tích Personas, luồng người dùng (User Flows), và xử lý triệt để rủi ro UX (ngăn ngừa sự ỷ lại AI, tránh layout shift).
- Viết Đặc tả giao diện `UI_DESIGN_SPECIFICATION.md` thiết lập Design System chuẩn sản xuất bao gồm: Split-View layout, màu sắc cảnh báo (Emerald 500, Amber 500, Red 600), trạng thái Loading/Error để xử lý chặn lỗi mượt mà.

## 3. SPEC mạnh/yếu
- Mạnh nhất: Hệ thống rào cản pin `soc_hard` và `soc_comfort` được phân lớp rõ ràng. Điều kiện Dừng (Infeasible) rất chặt, từ chối ngay phương án gây kẹt trên đường.
- Yếu nhất: Giải thuật hiện tại là Greedy (Tham lam), chỉ tìm trạm vừa đủ tốt gần nhất, không sinh ra con đường "Tối ưu toàn cục" (Global optimal) như thuật toán Dijkstra/A*.

## 4. Đóng góp khác
- Kết nối mã nguồn cũ của Planner với cấu trúc OOP Data mới do Sơn phát triển sau quá trình hợp nhất.

## 5. Điều học được
Viết thuật toán cho Production không chỉ là ra Output. Thuật toán cần trả về đủ Metadata (warning, distance, charge_min) để phục vụ cho các layers UI và AI đứng trên nó biểu diễn tốt UI đính kèm cảnh báo.
Trong mảng UX/UI, bài học lớn nhất là nguyên lý "Progressive Disclosure" và "Nhận thức cực nhanh (<2s)". Với tài xế, dữ liệu quá tải (bảng số liệu dry-data) là vô nghĩa và nguy hiểm. Cần dùng màu sắc, icon, lộ trình Split-View để truyền đạt cảnh báo (Warning/Infeasible) lập tức.

## 6. Nếu làm lại
Sẽ thử cài đặt một Node-graph thực thụ kết hợp A* + Weight = Thời gian sạc để tìm ra cách trạm hoàn hảo nhất so với đi bằng Greedy thông thường.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Viết base structure cho giải thuật lặp và loop invariant lẹ hơn nhiều.
- **Sai:** AI đã từng cố chèn cả các thông số như "chiều cao địa hình" hay "điều hòa độ F" vào công thức khiến scope bị phình to. Phải gạt đi để giữ đúng Linear Model MVP.
