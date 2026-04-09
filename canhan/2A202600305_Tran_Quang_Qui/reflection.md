# Individual reflection — Quí (AI/LLM)

## 1. Role
UX / Prompt Engineer & AI Service. Phụ trách kết nối LLM (OpenRouter) để phân tích báo cáo chuyến đi bằng ngôn ngữ tự nhiên.

## 2. Đóng góp cụ thể
- Viết `services/summary_service.py` gọi API gen tóm tắt.
- Viết logic bypass bằng "dummy key" để team chạy app UI không bị Crash lúc chèn Code thiếu `.env`.
- Thiết kế `services/system_prompt.txt` với kiến trúc hòa trộn linh hoạt: Instructions đóng trong ngoặc bằng Tiếng Anh (để AI hiểu logic) + Template Format xuất ngoài bằng Tiếng Việt.

## 3. SPEC mạnh/yếu
- Mạnh nhất: Áp dụng tư duy đa ngôn ngữ trong 1 prompt (Mixed-language Prompt). Hệ quả là Force LLM nói thuần Tiếng Việt thành công 100% thay vì tỉ lệ lỗi chèn tiếng Anh vô tình của các Open-source Models nhỏ.
- Yếu nhất: Tham số truyền vào Prompt cho xe là cố định (VF8 tĩnh). Tương lai nên nhúng Data config xe động vào Prompt context.

## 4. Đóng góp khác
- Review lại độ ổn định của giao diện (UI) để tương thích hiển thị text markdown của LLM.
- Thuyết minh và định hình Tone giọng của bot trong báo cáo demo.

## 5. Điều học được
Dù cố gắng ra lệnh "Hãy nói Tiếng Việt" cho model, nhưng model có xu hướng vỡ kịch bản nếu Template truyền mẫu bằng Tiếng Anh. Thiết kế Prompt là một dạng kĩ sư ngôn ngữ học kết hợp lập trình cấu trúc tâm lý AI.

## 6. Nếu làm lại
Sẽ áp dụng kĩ thuật Prompt Caching hoặc Streaming Output để giảm độ trễ hiển thị LLM Report trên thanh Sidebar.

## 7. AI giúp gì / AI sai gì
- **Giúp:** AI giải mã được hành vi "loạn ngôn ngữ" của mô hình rẻ tiền và tự đề xuất phương án mix prompt "Lõi Tiếng Anh - Format Tiếng Việt" siêu thông minh.
- **Sai:** Ban đầu AI gợi ý 1 rule ép Tiếng Việt và tự tưởng vậy là đủ, gây nguy cơ rủi ro cao khi test production nếu không tỉnh táo nghi ngờ.
