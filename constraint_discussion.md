# Constraints & Assumptions – EV Trip Planning Assistant

Thiết kế này bám theo các ràng buộc phổ biến trong bài toán Electric Vehicle Routing Problem with Time Windows & Recharging Stations (EVRPTW). [web4.ensiie](https://web4.ensiie.fr/~faye/mpro/MPRO_reseau/Projet_2020/The%20electric%20vehicle%20routing%20problem%20with%20time%20windows%20and%20recharging%20stations.pdf)

***

## 1. Vehicle Constraints

### 1.1 Battery capacity & State of Charge (SoC)

- Xe có dung lượng pin tối đa \(Q\) kWh (fixed cho mỗi model trong hệ thống).  
- Tại mọi thời điểm, trạng thái pin SoC thỏa: \(0 \leq \text{SoC} \leq Q\).  
- **Hard constraint – Safety buffer:**  
  - Planner chỉ generate route nếu SoC tại mọi điểm dừng (trạm sạc hoặc điểm đến cuối) luôn ≥ SoC\_min (ví dụ: 15% dung lượng pin).  
  - Nếu không có route nào thỏa SoC\_min, hệ thống phải báo “route không khả thi” và gợi ý fallback (ví dụ: chọn điểm đến gần hơn).  

### 1.2 Energy consumption model

- **MVP assumption:**  
  - Tiêu thụ năng lượng được mô hình hóa bằng một hằng số \(e\) kWh/km cho cả hành trình (không xét độ dốc, thời tiết, tắc đường, tải trọng…). [onlinelibrary.wiley](https://onlinelibrary.wiley.com/doi/10.1155/2020/3030197)
- Năng lượng cần để đi từ điểm A → B với khoảng cách \(d\) (km) là \(E = e \times d\).  
- **Feasibility check:**  
  - Với mỗi chặng giữa hai node liên tiếp, planner phải đảm bảo SoC hiện tại − \(E\) ≥ SoC\_min.  

### 1.3 Charging behavior

- Mỗi lần sạc, SoC tăng từ SoC\_in lên SoC\_out, bị giới hạn bởi:  
  - Dung lượng pin tối đa \(Q\).  
  - Công suất sạc tối đa của xe: \(P_{\text{vehicle}}\).  
- **MVP assumption – Linear charging time:**  
  - Thời gian sạc \(t_{\text{charge}}\) được giả định **tuyến tính** với lượng năng lượng cần nạp:  
    - \(t_{\text{charge}} \propto (\text{SoC\_out} - \text{SoC\_in})\).  
  - Chưa mô hình hóa đường cong sạc thực tế (sạc nhanh đến 70–80% rồi chậm dần). [sciencedirect](https://www.sciencedirect.com/science/article/pii/S2192437620300637)

### 1.4 Vehicle model

- **MVP scope:**  
  - Hệ thống chỉ hỗ trợ **1 model xe VinFast** ở phiên bản đầu (1 bộ tham số \(Q, e, P_{\text{vehicle}}\)).  
  - Thông số model được cấu hình sẵn, người dùng không chỉnh tay.  
- **Future scope (không implement trong hackathon):**  
  - Nhiều model xe khác nhau, mỗi model có:  
    - Dung lượng pin riêng.  
    - Profile tiêu thụ năng lượng riêng theo tốc độ/địa hình.  
    - Giới hạn công suất sạc khác nhau.  

***

## 2. Charging Station Constraints

### 2.1 Availability & connector type

Mỗi trạm sạc được mô hình hóa bởi các thuộc tính:

- Vị trí địa lý: tọa độ (lat, lon).  
- Loại sạc: AC/DC, fast/slow.  
- Công suất sạc tối đa của trạm: \(P_{\text{station}}\) (kW).  
- Chuẩn đầu cắm (connector type) phải tương thích với xe (ví dụ: CCS, Type 2).  

**Effective charging power:**  
- Công suất sạc thực tế mà xe nhận được là:  
  - \(P_{\text{effective}} = \min(P_{\text{vehicle}}, P_{\text{station}})\).  
- Thời gian sạc trong MVP sử dụng \(P_{\text{effective}}\) để ước lượng.  

### 2.2 Time & access windows

- **MVP assumption:**  
  - Tất cả trạm trong dataset đều **hoạt động 24/7** (không có opening hours).  
  - **Waiting time (thời gian chờ đến lượt)** được giả định = 0 (không model hàng chờ/độ bận trạm). [sciencedirect](https://www.sciencedirect.com/science/article/pii/S2192437620300637)
- **Future scope:**  
  - Thêm ràng buộc “opening hours” cho từng trạm.  
  - Ước lượng thời gian chờ dựa trên data sử dụng trạm theo giờ/ngày.  

### 2.3 Price & cost model

- Mỗi trạm có metadata về giá, ví dụ:  
  - Giá sạc theo kWh.  
  - Hoặc flat fee mỗi lần cắm sạc.  
- **MVP behavior:**  
  - Planner chưa tối ưu tổng chi phí sạc.  
  - Hệ thống chỉ hiển thị ước lượng chi phí cho route (để user thấy khác biệt giữa các phương án).  
- **Future scope:**  
  - Thêm mục tiêu “minimize total charging cost” song song với “minimize total travel time/distance”. [diva-portal](https://www.diva-portal.org/smash/get/diva2:1797108/FULLTEXT01.pdf)

### 2.4 Amenities & services around station

- Mỗi trạm có thể có thêm metadata về dịch vụ xung quanh, ví dụ:  
  - Nhà vệ sinh, quán ăn, café, trung tâm thương mại, khu vui chơi…  
- **MVP usage:**  
  - Amenities **không** là hard constraint.  
  - Được dùng như yếu tố **soft preference** để rank route/trạm khi các phương án tương đương về thời gian/an toàn.  
- **Future scope:**  
  - Kết hợp preference của user (ví dụ: “ưu tiên trạm có café/siêu thị”).  

***

## 3. User Preference & Safety Constraints

> Phần này không phải kỹ thuật thuần túy nhưng ảnh hưởng trực tiếp đến cách áp dụng các constraint trên vào UX.

### 3.1 Safety & range anxiety

- Planner **luôn đảm bảo**:  
  - Không có chặng nào khiến SoC rơi xuống dưới SoC\_min.  
  - Nếu một chặng tiềm năng vi phạm, planner phải:  
    - Thêm trạm sạc trung gian; hoặc  
    - Tuyên bố route không khả thi.  
- UI hiển thị rõ SoC dự kiến tại mỗi chặng/trạm để giảm “range anxiety” cho user. [fareye](https://fareye.com/au/en/resources/blogs/ev-trip-planner-expanding-ev-ecosystem)

### 3.2 Objective mode (chưa tối ưu đầy đủ trong MVP)

- Các mode tiềm năng:  
  - Fastest (ít thời gian nhất).  
  - Safest (SoC buffer cao, nhiều trạm dự phòng).  
  - Cheapest (tối ưu chi phí điện).  
- **MVP assumption:**  
  - Chỉ hỗ trợ một mode mặc định:  
    - “Fastest **trong điều kiện vẫn thỏa safety buffer**”.  
  - Các mode khác được mô tả trong SPEC như future extension.  

***

## 4. System & Data Constraints

### 4.1 Data quality & freshness

- Dữ liệu trạm sạc được coi là **tĩnh** trong phiên bản hackathon:  
  - Không cập nhật real‑time trạng thái trạm (busy, offline, bảo trì).  
- SoC và vị trí xe lấy từ hệ thống xe/ứng dụng được coi là **chính xác** (không model sai số cảm biến).  

### 4.2 Online vs offline behavior

- **MVP:**  
  - Planner chạy khi có internet để lấy bản đồ và danh sách trạm.  
  - Chưa xử lý đầy đủ kịch bản mất kết nối giữa đường; user có thể “replan” khi có mạng trở lại.  
- **Future scope:**  
  - Cache route và danh sách trạm offline, cho phép re‑routing cơ bản mà không cần internet.  

***

## 5. Scope: In-scope vs Out-of-scope (MVP vs Future)

### 5.1 In-scope (MVP – 2 ngày hackathon)

- Một model xe VinFast, thông số \(Q, e, P_{\text{vehicle}}\) cố định.  
- Mô hình tiêu thụ năng lượng tuyến tính theo khoảng cách.  
- Trạm sạc tĩnh, hoạt động 24/7, không hàng chờ.  
- Mỗi trạm có loại sạc và công suất tối đa, tính thời gian sạc tuyến tính theo năng lượng cần nạp.  
- Hard constraint: SoC tại mọi node ≥ SoC\_min (buffer an toàn).  
- Chưa tối ưu cost, chỉ hiển thị ước lượng chi phí.  
- Amenities dùng để hiển thị/ranking nhẹ, không bắt buộc.  

### 5.2 Out-of-scope (Future versions – vẫn mô tả trong SPEC)

- Nhiều model xe với profile sạc/tiêu thụ chuyên biệt.  
- Energy model phụ thuộc tốc độ, độ dốc, thời tiết, phong cách lái.  
- Time windows cho trạm, estimate hàng chờ, dữ liệu real‑time traffic & station occupancy.  
- Multi‑objective optimization: time + cost + comfort + safety.  
- Offline routing & re‑routing khi mất kết nối.  

***