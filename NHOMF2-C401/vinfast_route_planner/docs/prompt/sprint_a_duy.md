***

**[START OF PROMPT]**

**Role / System:**
Bạn là một Kỹ sư thuật toán (Algorithmic Engineer) và Python Developer cực kỳ xuất sắc với tư duy tối ưu hóa hàng đầu. Mã của bạn luôn đạt chuẩn production, tuân thủ nguyên tắc DRY, KISS và có type hinting nghiêm ngặt. Không bao giờ bao gồm các bình luận trong mã. Bạn phải viết mã tự ghi chú (self-documenting) thông qua cách đặt tên biến và hàm. Trả về giải pháp tối giản, chức năng đầy đủ và không trừu tượng hóa không cần thiết.

**Context:**
Chúng tôi đang xây dựng ứng dụng MVP: VinFast Route Planner cho một cuộc thi Hackathon 2 ngày. Ứng dụng giúp định tuyến đường sạc cho xe điện VinFast dựa trên thuật toán Greedy (chiết xuất từ bài toán EVRPTW).
Hiện tại là Sprint A: Xây dựng Core Engine - Logic Chọn Trạm. Hành vi tính toán thời gian sạc sẽ được thực thi tại Sprint B.

**Task / Instruction:**
Hãy viết một hàm `plan_route(origin_coord: tuple, destination_coord: tuple, soc_current: float, stations: list[dict], soc_comfort: float = 0.20) -> dict` trong Python dựa trên nhánh thuật toán Greedy.

Các yêu cầu kỹ thuật chi tiết theo Spec:
1. Thông số hệ thống xe VinFast VF8:
   - $Q$ (Dung lượng pin): 82 kWh
   - $e$ (Mức tiêu thụ năng lượng tuyến tính): 0.22 kWh/km
   - Tham số an toàn tuyệt đối ($SoC_{hard}$): 0.10 (10%)
2. Logic tiêu thụ năng lượng (Energy Consumption):
   - Phương trình cập nhật SoC tại điểm đến: $SoC_{arrive} = SoC_{prev} - \frac{e \times d}{Q}$
   - Hàm khoảng cách: Tạo một hàm giả lập `get_distance_km(coord1, coord2) -> float` tính khoảng cách đường chim bay (vd Haversine).
3. Thuật toán chọn trạm (Greedy Node Selection):
   - Đầu vào `stations` là mảng các dictionary thông tin trạm sạc.
   - Trạng thái trạm (Availability Filter): Bỏ qua các trạm có `status` là "maintenance" hoặc "offline". Chỉ duyệt trạm có `status == "active"`.
   - Chiến lược: Từ điểm xuất phát `origin_coord`, chọn trạm kế tiếp khả dụng nằm xa nhất (khoảng cách lớn nhất) trên tuyến đường sao cho tại ngưỡng đến nơi phải đảm bảo $SoC_{arrive} \ge SoC_{hard}$. Điểm xuất phát của lần lặp tiếp theo sẽ chính là trạm vừa chọn. Tiến trình diễn ra cho tới khi có thể đi thẳng tới đích `destination_coord` với $SoC_{arrive} \ge SoC_{hard}$.
   - Khả thi: Nếu chặng đi không tìm được trạm thoả mãn, cập nhật giá trị trả về `feasible = False`.
4. Hệ thống cảnh báo (Warning System):
   - Trên mỗi chặng tiến tới điểm dừng tiếp theo, nếu ngưỡng pin dự kiến đến nơi rơi vào $SoC_{hard} \le SoC_{arrive} < soc_{comfort}$, hãy thêm cảnh báo vào danh sách: `"SoC thấp tại chặng đến <Tên trạm / Điểm đích>"`.

**Input data:**
- `soc_current`: Nằm trong khoảng 0.0 đến 1.0 (ví dụ 0.85 = 85%).
- `stations`: Chuẩn xác với format từ `mock_stations.json` (VD: `{"id": "ST_HN_01", "name": "VinFast Vinhomes Ocean Park", "lat": 20.9941, "lon": 105.9458, "status": "active"}`).
- Luôn giả định mảng `stations` đã được sắp xếp thuận chiều tiến tới đích trên đường đi.

**Output format:**
- Kết quả xử lý phải trả về đúng 100% dictionary Interface sau đây:
```python
{
  "stops": [
      {
        "station": { ... }, 
        "soc_arrive": 0.20,
        "charge_min": 0,    
        "soc_depart": 0.80  
      }
  ],
  "total_time_min": 0,      
  "feasible": True,
  "warnings": ["SoC thấp tại chặng đến VinFast Vinhomes Ocean Park"],
  "soc_hard": 0.10,
  "soc_comfort": 0.20
}
```
*(Lưu ý: Mọi phép tính gán giá trị `charge_min`, `total_time_min` cho mặc định 0 ở Sprint A).*
- Yêu cầu xuất ra DUY NHẤT một khối mã (code block) Python chứa toàn vẹn giải pháp.
- Không tự động sử dụng icon/emoji. Xoá mọi mã mẫu không cần thiết.
- Phải tích hợp Unit Test dùng `pytest` hoặc `unittest` kiểm thử 1 trường hợp khả thi (feasible route) và 1 không khả thi (unfeasible route) làm Definition of Done.

**[END OF PROMPT]**

***

## 4. Các thực hành tốt nhất (Best Practices) đã áp dụng
- **Zero-Guessing Configurations:** Đưa tham số thực tiễn ($Q$, $e$, $SoC$) kèm theo công thức tuyến tính bảo vệ LLM khỏi việc bị "ảo giác" (hallucinate) chế tác theo các models ngoài Spec. Đồng thời đảm bảo cơ chế data filter đối với trường `status="active"`.
- **Micro-Scoping (Divide & Conquer):** Ngăn block output giải quyết ngay các thông số của chu trình EVRPTW hoàn chỉnh (khóa time windows hay charging duration, `charge_min`, `total_time_min` về mock value) nhằm ép LLM dùng toàn lực cấu trúc đúng nhánh truy xuất trạm bằng Greedy Loop. 
- **Contract Driven Development & Evaluation:** Áp đặt đúng Data Contract (`interface function` xác nhận ở Phase 0) giữa Core Engine và UI Layer, bắt buộc lập Unit Test xác thực kết quả ngay sau file.
