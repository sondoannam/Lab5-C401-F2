# Individual reflection — Duy (Algorithmic)

## 1. Role
Thuật toán (Algorithmic / Planner). Phụ trách engine định tuyến cốt lõi, tìm trạm đổ thỏa mãn giới hạn pin cứng & mềm.

## 2. Đóng góp cụ thể
- Code logic tính toán trong `core/route_planner.py`.
- Áp dụng công thức tiêu thụ: $SoC_{arrive} = SoC_{prev} - \frac{e \times d}{Q}$ với mức tiêu thụ tuyến tính.
- Làm vòng lặp giải thuật Greedy để nhảy trạm sạc kế tiếp mà vẫn thỏa mãn mức $SoC > SoC_{hard}$.
- Tính toán thời gian sạc ước tính $t_{charge}$ theo công suất tương đối giữa điểm sạc và phương tiện.

## 3. SPEC mạnh/yếu
- Mạnh nhất: Hệ thống rào cản pin `soc_hard` và `soc_comfort` được phân lớp rõ ràng. Điều kiện Dừng (Infeasible) rất chặt, từ chối ngay phương án gây kẹt trên đường.
- Yếu nhất: Giải thuật hiện tại là Greedy (Tham lam), chỉ tìm trạm vừa đủ tốt gần nhất, không sinh ra con đường "Tối ưu toàn cục" (Global optimal) như thuật toán Dijkstra/A*.

## 4. Đóng góp khác
- Kết nối mã nguồn cũ của Planner với cấu trúc OOP Data mới do Sơn phát triển sau quá trình hợp nhất.

## 5. Điều học được
Viết thuật toán cho Production không chỉ là ra Output. Thuật toán cần trả về đủ Metadata (warning, distance, charge_min) để phục vụ cho các layers UI và AI đứng trên nó biểu diễn tốt UI đính kèm cảnh báo.

## 6. Nếu làm lại
Sẽ thử cài đặt một Node-graph thực thụ kết hợp A* + Weight = Thời gian sạc để tìm ra cách trạm hoàn hảo nhất so với đi bằng Greedy thông thường.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Viết base structure cho giải thuật lặp và loop invariant lẹ hơn nhiều.
- **Sai:** AI đã từng cố chèn cả các thông số như "chiều cao địa hình" hay "điều hòa độ F" vào công thức khiến scope bị phình to. Phải gạt đi để giữ đúng Linear Model MVP.
