# Đặc tả Thiết kế Hệ thống Giao diện: VinFast EV Route Planner

*Dựa trên Phân tích UX/UI và Chiến lược Sản phẩm, tài liệu này cung cấp Hệ thống Thiết kế (Design System) chuẩn sản xuất và đặc tả giao diện chi tiết.*

---

## 1. Product Understanding (Nhận thức Sản phẩm)
**Tầm nhìn (Vision):** Xóa bỏ rào cản cự ly hoạt động (Range Anxiety) thông qua trí tuệ nhân tạo, tự động tối ưu hóa lộ trình xe điện VinFast, mang đến trải nghiệm liền mạch và an tâm tuyệt đối.
**Hành trình trọng tâm (Key User Journeys):**
1. **Khởi tạo:** Nhanh chóng đưa vào Đích đến, Điểm xuất phát và trạng thái Pin (SoC).
2. **Ra quyết định & Chờ:** Giảm áp lực chờ đợi bằng các thông điệp Processing thông minh.
3. **Giám sát lộ trình:** Dễ dàng liếc nhìn (glanceable) mức pin dự kiến, trạm sạc trên bản đồ.
4. **Tương tác chủ động:** Trợ lý AI báo hiệu kịp thời khi vi phạm ngưỡng an toàn (Buffer) hay khi fallback tuyến đường.
**Rủi ro UX Cốt lõi:**
- Người dùng quá tin tưởng số liệu (Over-trusting) quên theo dõi thực tế.
- Layout bị nhảy cấu trúc (Layout shift) khi AI trả về cục dữ liệu lớn.
- Bối rối khi hệ thống fallback sang định vị thẳng (Haversine) nếu mất API nền tế.

## 2. UX Strategy (Chiến lược Trải nghiệm)
**Nguyên tắc UX cho Xe điện:**
- **Nhận thức trong 2 giây (< 2s):** Ưu tiên màu sắc và ICON thay cho văn bản đọc.
- **Chống lỗi (Error-proof):** Không bao giờ tạo "Ngõ cụt" (Dead-end). Mọi cảnh báo rủi ro phải đi kèm với lựa chọn hành động (CTA).
**Ràng buộc Thiết kế (Constraints):**
- Mục tiêu chạm (Touch Target) tối thiểu 48x48px (đảm bảo bấm chuẩn xác khi xe đang chạy).
- Độ tương phản WCAG 2.1 tỷ lệ 4.5:1 nhằm tránh khó nhìn khi màn hình hắt sáng ban ngày.
- Đám mây thông tin phân rã: Không nhồi nhét, dùng Progressive Disclosure (Từ Bản đồ tổng quan -> Click để xem trạm chi tiết).

## 3. Layout System (Hệ thống Bố cục)
- **Hệ thống Lưới (Grid):** Sử dụng hệ 8pt cho Web/In-Car (khoảng cách gap-4, gap-6, p-4, p-6).
- **Hành vi Responsive:**
  - *Duyệt trên Mobile:* Giao diện dạng thẻ xếp lớp. Thông tin AI hiển thị dạng Bảng kéo đáy (Bottom Sheet).
  - *Màn hình Táp-Lô / Tablet:* Sử dụng **Split View (Chia đôi song song)**. Bản đồ ưu tiên chiếm khoảng 60%, Phần Dữ liệu tĩnh/Timeline AI chiếm 40%.
- **Thứ bậc ưu tiên chữ:** Context lái xe (Bản đồ) > Context lộ trình sạc (Timeline) > Dữ liệu phân tích Debug.

## 4. Full UI Screens (Các màn hình Trạng thái)
1. **Planning Input:** Box Form nổi trên bản đồ, hỗ trợ điền nhanh. Nút "🚀 Tối ưu Lộ trình".
2. **Loading/Processing:** Bản đồ hiển thị bộ xương (Skeleton) mờ, hiệu ứng shimmer loading đồng thời đưa microcopy *"AI đang kết nối & kiểm tra 350+ trụ sạc..."*.
3. **Success State:** Chia nửa. Đường dẫn màu lục/xanh ngọc. Bên Sidebar rũ xuống Vertical Timeline rất rõ mức pin Nạp/Xả.
4. **Warning State:** Banner trên đầu dải Vàng Cam. AI Alert khuyên nâng mức dung lượng an toàn (Buffer) lên 20%.
5. **Error/Block State:** Banner cảnh báo màu Đỏ Nhung. Lộ trình báo khoảng trống không thể nối trạm, Kèm nút đề xuất: *"Sạc bổ sung tại nhà trước khi đi"*.

## 5. Design System (Hệ thống Thiết kế chuẩn)
Tương thích hoàn toàn với TailwindCSS Tokens:
- **Color System:**
  - **Tốt/An toàn:** `emerald-500` (#10B981) - Màu chuẩn cho Sạc điện.
  - **Khẩn cấp/Thương hiệu:** `red-600` (#DC2626) - Sử dụng điểm xuyết theo DNA của VinFast và cảnh báo rủi ro lớn.
  - **Cảnh báo/Chú ý:** `amber-500` (#F59E0B).
  - **Nền Giao diện:** `slate-950` (#020617) - Dark mode siêu sâu làm nổi bật giao diện điện tử. UI Surface dùng `slate-900`.
- **Typography:** Ưu tiên `Inter` hoặc `SF Pro Display`. Số % Pin hiển thị ngoại cỡ (Text-4xl/5xl, Font-bold). Text bổ trợ dùng Text-sm.
- **Elevation & Ánh sáng (Glow):**
  - Hiệu ứng đổ bóng mờ: `shadow-2xl shadow-emerald-500/10`
  - Blob phát sáng: `blur-[100px] bg-emerald-600/10` tạo cảm giác Tech/Future.

## 6. Component System (Mô-đun Thành phần phần Mềm)
*   **BatteryGauge:** Thanh chỉ thị lượng pin uốn lượn: >50% (Emerald), 20-50% (Amber), <20% (Red).
*   **StationCard:** Thẻ trạm sạc gồm tên, badge loại sạc (AC/DC). Gạch chân ba chỉ số dứt khoát: *% Lúc tới / Thời gian dừng / % Rời đi*.
*   **VerticalTimeline:** Thiết kế trục thẳng dọc. Các điểm dừng (Nodes) tương ứng chấm tròn, có Dropdown hiện thêm tiện ích ăn uống/WC kế bên.
*   **AIBanner:** Khối Box bo tròn 12px viền mềm, làm nền thông báo tóm tắt của NLP.

## 7. Interaction & Motion Design
- Chuyển pha mượt mà `transition-all duration-500 ease-in-out` giúp không giật cục lúc bật/tắt Panel.
- Phản hồi từ Input/Buton: Hover nhấc nổi nhẹ thẻ trạm sạc `translate-y-[-2px]` và phủ mảng sáng khi Click.

## 8. Frontend Implementation (React + Tailwind Blueprint)
Bản phác thảo khung React App theo chiến lược Split-View:

```tsx
import React, { useState } from 'react';

export default function RoutePlannerUI() {
  const [isObservationMode, setIsObservationMode] = useState(true);

  return (
    <div className="relative min-h-screen w-full bg-slate-950 text-slate-200 overflow-hidden font-sans">
      {/* Nền ánh sáng AI Glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] bg-emerald-700/15 rounded-full blur-[120px] pointer-events-none" />
      
      <div className="relative z-10 flex h-screen w-full p-6 gap-6">
        {/* Phần 1: Bản đồ & Box Nhập liệu */}
        <div className={`flex flex-col gap-4 border border-slate-800 bg-slate-900/40 rounded-2xl shadow-2xl transition-all duration-500 ease-in-out ${
          isObservationMode ? 'w-1/2' : 'w-full max-w-4xl mx-auto'
        } overflow-hidden backdrop-blur-xl`}>
          
          {/* Header Map */}
          <div className="flex-1 relative w-full h-full">
            <div className="absolute inset-x-4 top-4 z-20 flex gap-4 bg-slate-950/90 p-4 rounded-xl border border-slate-800 backdrop-blur-md shadow-lg">
               <div className="flex-1 text-sm text-slate-400">Từ: Hà Nội</div>
               <div className="flex-1 text-sm text-slate-400">Đến: Vinh</div>
               <div className="w-16 text-emerald-400 font-bold text-right pt-1">85%</div>
            </div>
            
            {/* Map Area Placeholder */}
            <div className="w-full h-full flex items-center justify-center bg-slate-900/50">
               Interactive Map Container
            </div>
          </div>
        </div>

        {/* Phần 2: AI Agent & Vertical Timeline */}
        <div className={`flex flex-col gap-4 transition-all duration-500 ease-in-out ${
          isObservationMode ? 'w-1/2 opacity-100 translate-x-0' : 'w-0 opacity-0 translate-x-full'
        }`}>
          {/* AI Strategy Banner */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-900/40 to-slate-900 border border-emerald-800/50 shadow-[0_0_20px_rgba(16,185,129,0.1)]">
             <div className="flex items-center gap-2 mb-2">
                <span className="text-emerald-400 text-sm font-semibold uppercase tracking-widest">✨ Trợ lý VinFast AI</span>
             </div>
             <p className="text-sm font-medium leading-relaxed">
               Lộ trình tối ưu. Cần sạc 1 lần ước tính 45 phút tại Vincom Plazza Thanh Hóa. Nên đi đều chân ga qua đoạn Ninh Bình.
             </p>
          </div>
          
          {/* Timeline Chặng sạc */}
          <div className="flex-1 overflow-y-auto pr-2 space-y-4">
             <div className="relative pl-6 border-l-2 border-emerald-500/30 pb-4">
                <div className="absolute w-4 h-4 rounded-full bg-slate-950 border-2 border-emerald-500 -left-[9px] top-0 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                <h4 className="text-slate-100 font-semibold mb-3">📍 Vincom Thanh Hóa (Trạm DC 250kW)</h4>
                <div className="grid grid-cols-3 gap-2 text-xs">
                   <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/50">
                     <span className="text-slate-400 block mb-1">Tới dự kiến</span>
                     <span className="text-emerald-400 font-bold text-lg">22%</span>
                   </div>
                   <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/50">
                     <span className="text-slate-400 block mb-1">Thời gian đỗ sạc</span>
                     <span className="text-white font-bold text-lg">45m</span>
                   </div>
                   <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/50">
                     <span className="text-slate-400 block mb-1">Pin rời đi</span>
                     <span className="text-emerald-400 font-bold text-lg">80%</span>
                   </div>
                </div>
             </div>
          </div>

          {/* Assistant Chatbot */}
          <ChatbotModule />
        </div>
      </div>
    </div>
  );
}

function ChatbotModule() {
  return (
    <div className="h-[250px] mt-auto rounded-xl border border-slate-800 bg-slate-900/60 flex flex-col overflow-hidden backdrop-blur-md">
      <div className="flex-1 p-4 overflow-y-auto space-y-3">
         <div className="bg-slate-800 text-slate-200 p-3 w-3/4 inline-block rounded-2xl rounded-tl-sm text-sm border-l-2 border-emerald-500 shadow-sm leading-relaxed">
           Hệ thống đã nhận diện 2 trạm sạc đang bận. Đã tự động đổi lộ trình vòng sang trạm sạc cách 5km (Hoàn toàn trống).
         </div>
      </div>
      <div className="p-3 bg-slate-950/80 border-t border-slate-800">
         <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide text-xs">
            <button className="px-4 py-2 rounded-full bg-slate-800 hover:bg-slate-700 whitespace-nowrap text-emerald-400 border border-slate-700 transition">Tìm nhà hàng gần trạm sạc</button>
            <button className="px-4 py-2 rounded-full bg-slate-800 hover:bg-slate-700 whitespace-nowrap text-emerald-400 border border-slate-700 transition">Rút ngắn thời gian sạc?</button>
         </div>
         <input 
            type="text" 
            placeholder="Hỏi AI thông tin chuyến đi..." 
            className="w-full bg-slate-900 border border-slate-700 rounded-lg text-sm px-4 py-3 text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-shadow" 
         />
      </div>
    </div>
  );
}
```

## 9. Benchmark Insights (Bài học Quốc tế)
- **A Better Routeplanner (ABRP):** Tránh thiết kế "ngợp Data" như ABRP. Chỉ nên giữ logic Engine đỉnh cao ở backend. Khi qua front-end MVP VinFast, ẩn mọi kỹ thuật thừa thải.
- **Tesla UI:** Tích hợp thời gian sạc vào thanh ETA tự nhiên, minh bạch lộ trình.
- **Google Maps (Chế độ EV):** Hình vuông/chữ nhật vát góc cho trạm sạc sạc nổi bật trên lớp Map. Không lẫn với địa điểm POI thông thường.

## 10. Chatbot UI System (Hệ thống AI Chatbot Trọn vẹn)
- **Positioning (Vị trí):** Màn hình lớn dùng góc phải (Right panel split). Mobile dùng Bottom Sheet giật lên.
- **States:**
  - *Thinking state:* 3 chấm shimmer đập nhịp nhàng (Dot pulse).
  - *Stream state:* Cuộn mượt màn hình lên khi tin nhắn xổ xuống liên tiếp.
- **Interaction Messages:** 
  - Chat Bubble User: Thạch bản màu xám đen trơn (giảm nhiễu).
  - Chat Bubble AI: Bắt buộc đính viền mép trái `border-emerald-500` tạo sự tin cậy công nghệ.
- **Smart suggestions:** Thanh Chip nằm chìm dưới hộp thoại, nội dung bắt tự động dựa vào chặng hiện hành. Thao tác dễ bấm khi lái (One-touch request).
