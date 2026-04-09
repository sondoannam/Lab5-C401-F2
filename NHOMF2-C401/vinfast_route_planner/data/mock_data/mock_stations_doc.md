# Tài liệu Cấu trúc Dữ liệu: `mock_stations.json`

## Tổng quan
Tệp `mock_stations.json` chứa dữ liệu tĩnh (mock dataset) mô phỏng các trạm sạc VinFast dọc theo tuyến đường Hà Nội - Đà Nẵng. File này phục vụ trực tiếp cho quá trình xây dựng bản demo MVP (Minimum Viable Product) giải quyết bài toán EV Trip Planning trong khuôn khổ 2 ngày Hackathon.

Theo các thỏa thuận trong `constraint_discussion.md` và `spec-draft.md`, cấu trúc dữ liệu này đã được tinh giản mức tối đa: loại bỏ các thông số không cần thiết gây phức tạp hóa cho bài toán MVP (như `type`, `connector`, giờ mở cửa), đồng thời nâng các thiết lập chung (như profile phương tiện) lên scope toàn cục.

---

## Kiến trúc Dữ liệu

Tệp JSON được cấu trúc thành 2 cụm thông tin chính: **`metadata`** (Các thiết lập toàn cục) và **`stations`** (Mảng dữ liệu các trạm sạc).

### 1. Nút `metadata`
Phần này định nghĩa các tham số hằng số (constants) và giả định (assumptions) sẽ được thuật toán Planner sử dụng chung, thay vì phải truyền lặp lại cho từng chặng.

| Khóa (Key) | Thuộc tính con | Kiểu | Ý nghĩa / Ghi chú theo Spec |
|:---|:---|:---|:---|
| **`project`** | - | String | Tên định danh dự án. |
| **`route_name`** | - | String | Tuyến đường demo mẫu ưu tiên. |
| **`generated_at`** | - | String | Thời điểm khởi tạo file dữ liệu giả lập (ISO 8601). |
| **`vehicle_config`** | `model` | String | Mặc định sử dụng xe "VinFast VF8" (*Assumption C1*). |
| | `battery_capacity_kwh` | Float | Dung lượng pin tối đa \(Q\) = 82 kWh. |
| | `avg_consumption_kwh_per_km`| Float | Mức tiêu thụ tuyến tính \(e\) = 0.22 kWh/km (*Assumption C2*). |
| | `max_charge_power_vehicle_kw`| Float | Công suất nhận sạc tối đa của xe \(P_{vehicle}\) = 150 kW. |
| | `default_setup_time_min` | Integer | Thời gian thiết lập/chờ sạc mặc định của xe (phút). |
| | `connector` | String | Chuẩn cổng sạc gộp chung, mặc định độ tương thích là 100% (*Assumption C5*). |
| **`global_pricing`**| `standard_kwh_price` | Integer | Đơn giá mặc định tính theo kWh (trên toàn mạng lưới). MVP chỉ để hiển thị, chưa đưa vào tối ưu Cost Mode (*Assumption C10*). |
| | `currency` | String | Đơn vị tiền tệ, mặc định `VND`. |
| **`safety_constraints`** | `soc_hard_min_percent` | Integer | Ngưỡng an toàn tuyệt đối (Hard limit) = 10%. Route Planner phải từ chối/cảnh báo nếu rớt xuống mốc này (*Assumption C3*). |
| | `soc_comfort_min_percent` | Integer | Ngưỡng đệm an toàn (Buffer limit) = 20%. |
| | `charging_model` | String | `"Linear"` - Xác nhận giả định tính toán thời gian sạc tuyến tính (*Assumption C6*). |


### 2. Mảng `stations`
Danh sách này đóng vai trò như một cơ sở dữ liệu các Node tĩnh để xây dựng đồ thị lộ trình. Mỗi phần tử (trạm sạc) chứa các khóa sau:

| Thuộc tính | Kiểu dữ liệu | Giải thích & Ràng buộc MVP |
|:---|:---|:---|
| `id` | String | ID định danh trạm (Ví dụ: `ST_HN_01`). |
| `name` | String | Tên hiển thị của trạm trên giao diện người dùng. |
| `lat` / `lon` | Float | Tọa độ địa lý. Dùng để tính toán khoảng cách OSRM hoặc Haversine. |
| `p_station_kw` | Integer | Công suất sạc tối đa của trạm (\(P_{station}\)). **Lưu ý:** Thuật toán tính toán thời gian sạc sẽ dùng \(P_{effective} = \min(P_{vehicle}, P_{station})\). |
| `available_slots` | Integer | Số cổng khả dụng. *Trong phạm vi MVP chỉ để mock giao diện*, hoàn toàn bỏ qua việc tính hàng chờ / time windows (*Assumption C8*). |
| `setup_time_min` | Integer | Tùy chọn thời gian setup/chờ cắm đầu sạc (phút). Bỏ qua yếu tố dòng xếp hàng. |
| `status` | String | Tình trạng ("active", "offline", "maintenance"). Planner chỉ duyệt các trạm mang cờ "active". |
| `amenities` | Array[String]| Danh sách tiện ích (coffee, restroom, shopping_mall...). Dùng làm Soft-preference hoặc làm tag Highlight trên UI hiển thị tóm tắt, không phải là Hard constraint trong MVP. |

---

## 3. Lý giải các Quyết định Lược bỏ (Design Rules)
Dựa theo `constraint_discussion.md` và góp ý tối ưu, cấu trúc hiện tại **không chứa** các trường sau:

- **`type` (AC/DC) & `connector` (Chuẩn cắm)** ở cấp độ trạm: Được coi là luôn tương thích 100% do hackathon chỉ giả định duy nhất 1 tập xe VinFast đầu cuối.
- **Giờ hoạt động (Opening Hours)**: MVP giả định tất cả các trạm hoạt động 24/7. Không tồn tại khái niệm "Time Windows".
- **Giá theo từng trạm (Specific Pricing / Peak hour pricing)**: Không sử dụng do thuật toán định tuyến chỉ tập trung vào Objective là "Fastest-safe", đẩy việc tính tiền lên Global Reference. Lược bỏ thuộc tính này giúp giảm nhẹ việc tính toán Cost function.
