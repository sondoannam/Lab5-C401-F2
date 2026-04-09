
**[START OF PROMPT]**

**Role / System:**
Bạn tiếp tục đóng vai trò là Senior Backend & Algorithmic Engineer. Bạn thành thạo ứng dụng toán học vào lập trình, luôn viết mã không nợ kỹ thuật (technical debt), dễ tích hợp và bảo trì.

**Context:**
Chúng ta đang phát triển MVP hệ thống VinFast Route Planner. Ở Sprint trước, hệ thống đã biết chọn trạm thỏa mãn mức năng lượng an toàn (SoC). Ở Sprint B (Intelligence & Visualization), chúng ta cần chuyển đổi dữ liệu thô thành thông tin thời gian thực sự hữu ích. Mục tiêu là viết logic tính toán chính xác thời gian sạc cho từng lần dừng.

**Task / Instruction:**
Hãy cập nhật hàm `plan_route` hoặc viết thêm một hàm helper `calculate_charging_stats()` nhằm tính toán thời gian sạc tuyến tính tại mỗi trạm mà xe dừng lại.
Yêu cầu thuật toán:
1. Xe cần sạc đủ pin để đến trạm kế tiếp + duy trì bộ đệm an toàn. Tạm giả định xe sẽ luôn được yêu cầu sạc lên một mức `SoC_target` (ví dụ: 80% hoặc một mức vừa đủ cho hành trình tiếp).
2. Xây dựng công thức tính Công suất thực tế (Effective Power):
   - $P_{effective} = \min(P_{vehicle}, P_{station})$
   - Trong đó: $P_{vehicle} = 150 (kW)$ đối với xe VF8.
3. Cập nhật thời gian sạc tuyến tính ($t_{charge}$ tính bằng giờ, sau đó đổi ra phút):
   - $t_{charge} = \frac{(SoC_{target} - SoC_{arrive}) \times Q}{P_{effective}}$
   - Chú ý: $Q = 82 (kWh)$ cho VF8. Lượng năng lượng cần nạp là độ chênh lệch phần trăm SoC nhân với tổng dung lượng.

**Input data:**
- Đầu vào gồm một từ điển (dictionary) các trạm với thông tin công suất sạc của trạm ($P_{station}$), mức $SoC_{arrive}$ mà tính toán ở chặng trước.
- Giả định $SoC_{target}$ trong chuẩn MVP là 80% (`0.8`), trừ khi cần ít hơn.

**Output format:**
- Xuất ra mã nguồn Python hoàn chỉnh. Không thêm bình luận không cần thiết trong code.
- Định dạng Output dictionary của `plan_route` bắt buộc phải trả về các khóa (keys) bổ sung cho từng trạm: `charge_min` và `soc_depart`.
- Bổ sung 1 ca kiểm thử (test case) cho hàm tính thời gian sạc này.

**[END OF PROMPT]**

***

## 4. Các thực hành tốt nhất (Best Practices) cần tuân thủ
- **Đóng gói Logic (Encapsulation):** Đề xuất tách phần tính toán năng lượng (Energy/Charge Calculation) ra hàm riêng nhằm đáp ứng quy chuẩn KISS và DRY, thay vì dồn tất cả vào `plan_route`.
- **Ràng buộc đầu ra tường minh (Explicit Contract):** Việc chỉ định cụ thể các keys `charge_min`, `soc_depart` đảm bảo code này sẽ lập tức ráp nối được với đội Frontend (Bách).
- **Mở rộng tương lai (Future Proofing):** Việc dùng $P_{effective} = \min(P_{vehicle}, P_{station})$ cho thấy sự chặt chẽ, khi sau này hệ thống mở rộng đa xe, đa loại trạm, thuật toán vẫn đứng vững.
