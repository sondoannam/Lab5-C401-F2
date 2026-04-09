# Individual reflection — Quí (AI/LLM)

## 1. Role
Prompt Engineer & AI Service. Phụ trách thiết kế system prompt, agent tools schema, và kết nối LLM (OpenRouter) để AI Agent phân tích và tóm tắt lộ trình bằng ngôn ngữ tự nhiên.

## 2. Đóng góp cụ thể
- Thiết kế `services/agent_tools.py` — định nghĩa tool schema (Function Calling) cấp cho LLM.
- Viết logic bypass bằng "dummy key" để team chạy app không bị crash khi thiếu `.env`.
- Thiết kế system prompt với kiến trúc hòa trộn linh hoạt: Instructions bằng Tiếng Anh (để AI hiểu logic) + Format output bằng Tiếng Việt.
- Hỗ trợ fix giao diện React frontend (ChatbotUI, layout).
- Xây dựng prototype chatbot riêng (Streamlit) dùng để demo nội bộ và trao đổi kỹ thuật giữa các nhóm: agentic loop với Function Calling qua OpenRouter, hiển thị thinking log real-time (agent gọi tool gì, bước nào), chip gợi ý context-aware, bản đồ lộ trình on-demand trong chat bubble.

## 3. SPEC mạnh/yếu
- Mạnh nhất: Áp dụng tư duy đa ngôn ngữ trong 1 prompt (Mixed-language Prompt). Hệ quả là Force LLM nói thuần Tiếng Việt thành công 100% thay vì tỉ lệ lỗi chèn tiếng Anh vô tình của các Open-source Models nhỏ.
- Yếu nhất: Tham số truyền vào Prompt cho xe là cố định (VF8 tĩnh). Tương lai nên nhúng Data config xe động vào Prompt context.

## 4. Đóng góp khác
- Review lại độ ổn định của giao diện (UI) để tương thích hiển thị text markdown của LLM.
- Thuyết minh và định hình Tone giọng của bot trong báo cáo demo.

## 5. Điều học được
Dù cố gắng ra lệnh "Hãy nói Tiếng Việt" cho model, nhưng model có xu hướng vỡ kịch bản nếu Template truyền mẫu bằng Tiếng Anh. Thiết kế Prompt là một dạng kĩ sư ngôn ngữ học kết hợp lập trình cấu trúc tâm lý AI.

## 6. Nếu làm lại
Sẽ áp dụng kĩ thuật Prompt Caching hoặc Streaming Output để giảm độ trễ hiển thị response của LLM trên giao diện chat.

## 7. AI giúp gì / AI sai gì
- **Giúp:** AI giải mã được hành vi "loạn ngôn ngữ" của mô hình rẻ tiền và tự đề xuất phương án mix prompt "Lõi Tiếng Anh - Format Tiếng Việt" siêu thông minh.
- **Sai:** Ban đầu AI gợi ý 1 rule ép Tiếng Việt và tự tưởng vậy là đủ, gây nguy cơ rủi ro cao khi test production nếu không tỉnh táo nghi ngờ.
