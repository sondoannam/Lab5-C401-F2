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
- Mạnh nhất: Nhóm giữ được đúng core value của spec — giải quyết bài toán "range anxiety" bằng route planning có tính đến SoC, mức pin an toàn, điểm dừng sạc và cảnh báo rủi ro. Phần AI Agent cũng hoạt động thật: LLM tự quyết định gọi tool nào, không cần hard-code flow, và vẫn trả lời tự nhiên bằng tiếng Việt nhờ cách thiết kế prompt.
- Yếu nhất: Tham số truyền vào Prompt cho xe là cố định (VF8 tĩnh). Tương lai nên nhúng Data config xe động vào Prompt context.

## 4. Đóng góp khác
Ngoài phần kỹ thuật, mình cũng ngồi kiểm tra lại xem chatbot hiển thị markdown có bị lỗi format không — vì LLM hay trả về text có bullet, bold, code block mà giao diện không render đúng thì trông rất tệ. Ngoài ra mình cũng là người chốt tone giọng cho bot: thân thiện, nói tiếng Việt tự nhiên, không quá robot, không quá "thư ký văn phòng".

## 5. Điều học được
Cái mình học được nhiều nhất là: chỉ nói "hãy trả lời bằng tiếng Việt" trong prompt là chưa đủ. Mấy model nhỏ, rẻ tiền rất hay bị "loạn ngôn ngữ" — đặc biệt khi phần template ví dụ trong prompt lại viết bằng tiếng Anh, nó sẽ học theo template đó và trộn ngôn ngữ vô tình. Giải pháp là tách rõ: phần logic/instruction viết tiếng Anh để model hiểu cấu trúc, còn phần format output thì viết tiếng Việt để nó bắt chước đúng giọng. Cách này hiệu quả hơn nhiều so với chỉ ra lệnh.

## 6. Nếu làm lại
Phần mình tiếc nhất là chưa làm được Streaming — tức là để response của LLM hiện ra từng chữ thay vì chờ cả đoạn rồi mới hiện. Với demo thì độ trễ vài giây vẫn chấp nhận được, nhưng nếu thực sự deploy cho người dùng thì cảm giác "chờ" đó sẽ làm người ta mất kiên nhẫn rất nhanh. Lần sau sẽ ưu tiên làm streaming từ đầu.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Khi mình mô tả vấn đề "model cứ chèn tiếng Anh dù đã dặn tiếng Việt", AI phân tích được nguyên nhân khá chính xác và gợi ý ngay cách mix prompt — thứ mình không nghĩ tới lúc đầu. Tiết kiệm được kha khá thời gian thử sai.
- **Sai:** AI ban đầu tự tin gợi ý chỉ cần thêm 1 dòng "Always respond in Vietnamese" là xong. Mình test thử thì vẫn lỗi. Phải hỏi thêm vài vòng nó mới ra được giải pháp thực sự. Bài học là không nên tin AI ở lần đầu tiên, nhất là với những thứ liên quan đến behavior của model.
