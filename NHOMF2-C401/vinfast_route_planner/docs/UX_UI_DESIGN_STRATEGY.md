# Chiến lược UI/UX & Phân tích Dự án: VinFast EV Route Planner

*Được thực hiện bởi: Chuyên gia Thiết kế Sản phẩm & Nghiên cứu UX (20+ năm kinh nghiệm) tham khảo chuẩn Google Material, Apple HIG và WCAG.*

---

## GIAI ĐOẠN 1: PHÂN TÍCH DỰ ÁN (PROJECT ANALYSIS)

### 1. Tóm tắt dự án (Project Summary)
**VinFast EV Route Planner** là một giải pháp AI tự động hóa việc lên kế hoạch lộ trình và tìm trạm sạc cho chủ xe điện đi đường dài. 
**Giá trị cốt lõi (Core Value):** Xóa bỏ nỗi sợ "hết pin giữa đường" (Range Anxiety), giảm tải công sức tự tính toán quãng đường và thời lượng sạc. Hệ thống đảm nhận vai trò định hướng an toàn, từ đó gia tăng niềm tin và sự an tâm khi sử dụng xe điện VinFast.

### 2. Chân dung người dùng (User Personas)
*   **Đối tượng:** Chủ xe VinFast (model VF8 trong phạm vi MVP) thường phải di chuyển liên tỉnh.
*   **Hành vi:** Có thói quen tự ước tính quãng đường, phải sử dụng nhiều app cùng lúc (Google Maps + App VinFast) để xem trạm sạc.
*   **Điểm đau (Pain points):** 
    *   Sợ xe hết pin sập nguồn, nằm đường giữa khu vực vắng vẻ.
    *   Không nắm rõ trạm sạc phía trước có sạc nhanh/chậm, mất bao lâu để đầy.
    *   Cảm giác quá tải nhận thức khi phải suy sét liên tục lượng tiêu hao pin.

### 3. Tính năng chính & Luồng chức năng (Key Features)
*   **Đầu vào (Input):** Điểm xuất phát, Điểm đến, % Pin hiện tại (SoC), Ngưỡng an toàn (Comfort Buffer).
*   **Xử lý cốt lõi:**
    *   Thuật toán OSRM / Haversine (Fallback) tính khoảng cách.
    *   Heuristic duyệt các trạm sạc sao cho SoC luôn > 10% (Hard limit).
*   **Đầu ra (Output):**
    *   Bản đồ lộ trình ghép nối với mạng lưới trạm sạc.
    *   Chi tiết chặng: SoC dự kiến khi đến/rời, thời gian sạc, công suất điện.
    *   Trợ lý thông minh (LLM) thay mặt hệ thống tóm tắt chuyến đi và phát đi cảnh báo rủi ro (lời khuyên, cảnh báo buffer).

### 4. Rủi ro UX & Các vấn đề (UX Risks & Issues)
*   **Trải nghiệm ngắt quãng với cơ chế Fallback:** Khi API OSRM bảo trì hoặc lag, việc chuyển sang đường chim bay (Haversine) nếu thiếu thông báo giao diện khéo léo sẽ khiến user cảm thấy "sản phẩm bị lỗi" thay vì "sản phẩm tự động xử lý lỗi tốt".
*   **Sự ỷ lại vào AI (Over-trusting):** Người dùng có thể quá tin tưởng vào `SoC_arrive` dự tính mà quên theo dõi thực tế, vì MVP chưa liên kết với điều kiện thời tiết/giao thông khắc nghiệt.
*   **Hạn chế của UI Framework:** Phụ thuộc vào Streamlit có thể khiến tương tác kém mượt so với Native App, gây tình trạng nhảy layout (layout shift) nếu không khóa kích thước các component render.
*   **Trình bày dạng bảng (Table Formats):** Output dạng bảng dữ liệu có thể dễ test ở console nhưng rất khó xem trên thiết bị di động.

### 5. Cơ hội cải thiện (Opportunities for Improvement)
*   **Học lệnh cá nhân (Machine Learning Profile):** Cập nhật hệ số tiêu thụ `e` dựa vào phản hồi hoặc thói quen lái thực tế của mỗi xe thay vì hằng số bảo thủ (conservative).
*   **Bối cảnh thời gian thực (Real-time Context):** Kết nối API báo trạng thái bận/rảnh của pillar sạc.
*   **Hành trình phi tuyến tính (Timeline UX):** Chuyển từ giao diện báo cáo dạng bảng sang trải nghiệm Step-by-Step dọc màn hình (Vertical Navigator).

---

## GIAI ĐOẠN 2: CHIẾN LƯỢC THIẾT KẾ UI/UX (UI/UX DESIGN STRATEGY)

### 1. UX Strategy Overview
Thiết kế tập trung vào tiêu chí **"Phòng ngừa lỗi (Error-proof) & An tâm tối đa"**. Vì bối cảnh sử dụng là trên xe ô tô (màn HUD/taplo) hoặc thiết bị di động cầm tay, giao diện phải đáp ứng thao tác một ngón (One-hand Operation), tối giản hóa chi tiết rườm rà và sử dụng thị giác (Màu sắc, Icon) để tác động thần kinh não bộ nhanh nhất (nhận diện độ an toàn).

### 2. Kiến trúc thông tin (Information Architecture - IA)
Ứng dụng nguyên lý **Progressive Disclosure (Hé lộ tuần tự)** nhằm giữ UI sạch sẽ:
*   **Tầng 1 (Cơ bản - Input):** Điểm đi, Điểm đến, % Pin hiện tại. 
    *   *(Phần tinh chỉnh Buffer an toàn nên giấu dưới dạng nút "Thiết lập nâng cao")*.
*   **Tầng 2 (Nhìn tổng quan):** Bản đồ tuyến đường (Hero Section) & Tổng thời lượng di chuyển bao gồm cả sạc.
*   **Tầng 3 (Chi tiết theo chặng):** Tóm tắt AI (LLM Alert) & Dòng thời gian cuộn dọc (Vertical Timeline) chứa chi tiết của mỗi lần dừng.

### 3. Luồng người dùng (User Flows)
*   **Bước 1: Khởi động.** Màn hình mặc định hiển thị Box nhập liệu (có thể có auto-detect GPS làm điểm đi).
*   **Bước 2: Ra quyết định.** User nhập thông tin lộ trình và kéo lượng Pin hiện có → Bấm Call-to-action (Vd: "Tối ưu lộ trình").
*   **Bước 3: Chờ xử lý (Processing).** Hiển thị màn hình Loading kèm Microcopy: *"Đang quét cấu trúc trạm sạc..."* (Giảm áp lực khoảng trắng).
*   **Bước 4A (Luồng Thành Công):** Split View - Bản đồ ở trên, dưới là Tóm lược AI và Các trạm dừng theo chi tiết trục dọc.
*   **Bước 4B (Luồng Rủi ro/Chạm Buffer):** Bản đồ đi kèm **Banner Vàng** nổi bật. Thông báo AI nhấn mạnh rủi ro. Có nút CTA nhỏ: "Chỉnh lại mức pin an toàn dự phòng".
*   **Bước 4C (Luồng Block/Thất bại):** Input chặng không khả thi → Báo lỗi (Error) với Banner Đỏ. Đề xuất: "Sạc đầy thêm trước khi xuất phát" hoặc "Giảm cự ly di chuyển". Luôn có lối ra (Exit door), không tạo Dead-end UX.

### 4. Cấu trúc Wireframe chữ (Text-based Low-fidelity)
*   **[Header]** VinFast AI Route Planner
*   **[Panel Nhập liệu]** (Sticky trên mobile)
    *   📍 Từ: [ Input text ]
    *   🏁 Đến: [ Input text ]
    *   🔋 Pin hiện tại: [ Slider / Input number % ] 
    *   [ Button: 🚀 Lên lộ trình sạc ]
*   **[Khu vực Bản đồ]** 
    *   Màu đường đi: Xanh ngọc (An toàn). Đỏ (Nếu Fallback timeout hoặc chạm hard buffer).
    *   Icon trạm sạc: Biểu tượng tia chớp lớn (có badge DC/AC góc nhỏ).
*   **[Khu vực Thông điệp AI]** 
    *   Box màu nổi bật nhẹ có bo góc. 
    *   *VD: "✨ Lộ trình an toàn, sẽ mất tổng cộng 45 phút sạc tại 2 trạm. Hãy chú ý giữ ga ổn định ở đoạn Vinh - Hà Tĩnh nhé!"*
*   **[Trục thời gian chặng đường]**
    *   [Icon Xe] Bắt đầu: Hà Nội (85%)
    *   [Icon Trụ sạc xanh lơ] Dừng ở trạm Vincom Vinh
        *   Tới với: 22% | Sạc 45 phút (DC) | Tiếp tục với: 80%
    *   [Icon Cờ đích] Kết thúc: Đà Nẵng (Pin còn: 30%)

### 5. Nguyên tắc thiết kế giao diện (UI Design Guidelines)
*   **Cấu trúc nền (Background) & Thể hiện hình ảnh (Aesthetics):**
    *   Sử dụng thiết kế **Dark mode sâu** với phông nền xanh đen nguyên khối (`bg-slate-950`), chữ màu sáng (`text-slate-200`). Bố cục tràn viền tối đa (`min-h-screen w-full`) và ẩn thanh cuộn thừa (`overflow-hidden`).
    *   **Hiệu ứng ánh sáng nền (Ambient Glowing Blobs):** Đặt các hình khối ảo nổi (*absolute positioning*) bằng các dải màu như Emerald (Xanh ngọc) và Amber (Hổ phách) kết hợp hiệu ứng làm mờ mạnh mẽ (`blur-[120px]`, `blur-[100px]`). Chi tiết này tạo ra các quầng sáng dịu lan tỏa (glowing gradients) thể hiện chất công nghệ AI hiện đại cao cấp và không bị nhàm chán.
*   **Màu sắc chức năng (Feedback Colors):**
    *   Safe (Tốt): Xanh Mint (#10B981)
    *   Warning (Chú ý): Hổ phách (#F59E0B)
    *   Critical (Nguy hiểm): Đỏ nhung (#EF4444)
*   **Typography:** Phông chữ San-Serif không chân (Inter, Roboto hoặc SF Pro). Trọng lượng font chữ tương phản tốt giúp mắt quét số liệu cực nhanh. Số % pin cần dùng font chữ to, in đậm (Bold).
*   **Thiết kế tương tác Khung (Interactive Transitioning):** Mọi sự thay đổi về kích thước và vị trí mở/đóng layout đều phải có hiệu ứng trượt chuyển đổi, tạo lực trễ bằng thuộc tính CSS (`transition-all duration-500 ease-in-out`), không sử dụng kiểu bật/tắt (blink) đột ngột.
*   **Không gian & Kích thước chạm (Spacing & Target):** Thiết kế "Breathing space" - khoảng cách khối rành mạch (`gap-6`). Khoảng cách chạm (CTA button, Toggle Control) đảm bảo tối thiểu **48x48px** cho ngón tay người lái xe.
*   **Accessibility (Đạt WCAG 2.1):** Độ tương phản văn bản và nút nhấn phải đạt 4.5:1. Màu sắc cảnh báo phải luôn đi kèm với Icon đại diện (VD: Dấu chấm than, Tia sét) vì màu sắc giảm ý nghĩa đối với người dùng mù màu.

### 6. Đề xuất chuẩn thiết kế Hệ thống Component (Design System)
*   `BatteryGauge_Component`: Đồ thị pin hình vòng cung hoặc thanh ngang đổi màu linh động. (Dưới 20% -> Cam, Dưới 10% -> Đỏ).
*   `SmartContextBanner`: Component cảnh báo. Nó nhạy cảm với context (Chỉ hiện khi LLM trả về cảnh báo, không hiện nếu hành trình tối ưu hoàn hảo tỷ lệ 100%).
*   `StepTracking_Component`: Module dòng thời gian thay thế cho HTML Table. Có thể bấm mở (Accordion) dể xem thêm tiện ích như Cafe, WC tại trạm sạc đó.

### 7. Phân tích đối chiếu toàn cầu (Global Benchmark Analysis)
1.  **A Better Routeplanner (ABRP):**
    *   *Ưu điểm:* Công cụ "nặng đô", tuỳ chỉnh cực kỳ mạnh mẽ (Gió, nhiệt độ, kiểu xe, lốp xe).
    *   *Hạn chế (Tránh học theo):* Giao diện quá ngợp thông số, dành cho kỹ sư (nerdy). UX khó hiểu cho người lái xe bình thường.
    *   *Bài học MVP VinFast:* Phải giấu sự phức tạp kỹ thuật dưới nắp xe; hiển thị kết quả cuối cùng một cách ăn liền hơn.
2.  **Hệ thống điều hướng Tesla (Navigation):**
    *   *Ưu điểm:* Cực kì liền mạch. Giao diện trực quan tự gài điểm sạc Supercharger vào. Số % còn lại khi đến nơi dự báo cực chính xác gây ấn tượng tới tâm lý dùng.
    *   *Bài học MVP VinFast:* Học hỏi việc kết hợp liền mạch map với thời gian di chuyển, coi chuyện sạc xe tự nhiên như việc lái đi, không tạo rào cản thao tác.
3.  **Google Maps - Chế độ xe điện:**
    *   *Ưu điểm:* UI quen thuộc. Tìm kiếm trạm sạc dễ dàng bằng icon phân biệt loại cổng trên bản đồ.
    *   *Bài học MVP VinFast:* Cách thiết kế icon trạm phải "nổi khối" trên Map (Layer riêng biệt).

---

### 8. Thiết kế Tương tác Khung nhìn & Mã sườn (Advanced Layout Pattern)
Lấy cảm hứng từ các nền tảng AI Tooling hiện đại, kiến trúc ứng dụng trên Native Web áp dụng kiểu thiết kế **Song song (Split-view Interactive)** giữa "Khung Bản Đồ/Giao Tiếp Chính" và "Khung Thông Số Kỹ Thuật/AI Log". Hệ thống sử dụng Flexbox (`gap-6`) và biến trạng thái `isObservationMode` làm cốt lõi điều hướng không gian.

**1. Tương tác Trạng thái Kép:**
*   **Tắt chế độ quan sát (Tự động mở không gian):** Khung chính (Main view) tự động mở rộng theo định dạng chuẩn, không bị kéo dãn dàn trải tới hai mép nhờ giới hạn kích thước (`max-w-4xl`) và tự căn giữa (`mx-auto`). Khung Log hiển thị Dữ liệu nội bộ được ẩn dần bằng độ trong suốt (`opacity-0`), chiều rộng thu rạp về mức `w-0` và trượt hoàn toàn ra lề ở biên phải (`translate-x-full overflow-hidden`).
*   **Bật chế độ quan sát (Chia đôi màn hình):** Layout chia đều chuẩn 50%. Khung chính co rút về bên nửa trái (`w-1/2`). Khung Log hiện thực ở phía phải chiếm 50% (`w-1/2`), lấy lại mức hiển thị chuẩn nét `opacity-100` và trả về vị trí tọa độ tĩnh `translate-x-0`.
*   **Animation Transform:** Mọi sự chuyển pha cấu trúc khung đều sử dụng thông số chung: `transition-all duration-500 ease-in-out` tạo ra động tác trượt đẩy hai luồng thông tin song song mượt mà.
*   **Toggle Nổi (Cụm Công Cụ):** Nút công tắc được định vị treo ở góc phải cao phía trên tách biệt các layer cuộn trang (`absolute top-4 right-4 z-50`).

**2. Skeleton Cấu trúc Mẫu (React / Tailwind CSS):**
Mã nguồn cấu trúc React chuẩn này dành sẵn cho việc kiến thiết không gian ứng dụng giám sát AI hoặc phân tích Log trạm sạc khi chuyển mình từ Streamlit lên Web App chính thức:

```tsx
<div className="relative min-h-screen w-full bg-slate-950 overflow-hidden text-slate-200 font-sans">
  {/* Hiệu ứng Layer Ánh sáng Nền (Ambient Glowing) */}
  <div className="absolute top-0 -left-64 w-[500px] h-[500px] bg-emerald-700/20 rounded-full blur-[120px] pointer-events-none" />
  <div className="absolute top-1/2 right-0 w-[400px] h-[600px] bg-emerald-900/10 rounded-full blur-[100px] pointer-events-none" />
  
  {/* Nút Bật/Tắt Khung ẩn nổi */}
  <div className="absolute top-4 right-4 z-50">
    <button 
      onClick={() => setIsObservationMode(!isObservationMode)}
      className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-md shadow-lg transition"
    >
       Bật/Tắt Khung Log (Observation Mode)
    </button>
  </div>
  
  {/* Phân vùng Box Content Chính Flexbox cân bằng khoảng cách*/}
  <div className="flex h-screen w-full p-6 pt-24 gap-6">
    
    {/* Khung Nhập Liệu & Bản Đồ Trung Tâm (Trái/Main View) */}
    <div className={`transition-all duration-500 ease-in-out ${
      isObservationMode ? 'w-1/2' : 'w-full max-w-4xl mx-auto'
    }`}>
      {/* <RouteMapAndInputComponent /> */}
    </div>

    {/* Khung Chi Tiết Kỹ Thuật, Log Data & Trạng Thái Trạm (Phải) */}
    <div className={`transition-all duration-500 ease-in-out ${
      isObservationMode ? 'w-1/2 opacity-100 translate-x-0' : 'w-0 opacity-0 translate-x-full overflow-hidden'
    }`}>
      {/* <SystemLogAndTimelineComponent /> */}
    </div>
  </div>
</div>
```
Việc ứng dụng mô hình này đặc biệt tương thích với người dùng phân luồng: Hành khách/Tài xế thì theo dõi màn hình chính rộng lớn, tối giản. Các Kỹ sư dịch vụ có thể nhấn mở module Log dữ liệu bên phía tay phải ra đối chiếu real-time mà hoàn toàn giữ nguyên ngữ cảnh phân tích cốt lõi (Current UI Thread).
