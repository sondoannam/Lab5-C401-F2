# AI Product Canvas — Vietnam Airlines Chatbot NEO

**Sản phẩm phân tích:** Vietnam Airlines — Chatbot NEO 

---

## Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì? |
| **Trả lời** | **User:** Hành khách Vietnam Airlines cần tra cứu nhanh — hành lý, giá vé, chặng bay, quy định thú cưng. **Pain:** Gọi hotline chờ lâu; NEO hiện tại ném văn bản dày đặc + 3-4 link → bắt user tự đọc tự tìm. NEO bị bó buộc keyword, không hiểu ngữ cảnh hội thoại, không nhớ context câu trước. **AI giải:** Hỏi từng bước theo Decision Tree (Duy), kết hợp memory saver + real-time giá vé (Bách) → trả lời đúng ngữ cảnh, đúng nhu cầu, không spam link. | **Khi AI sai:** User bị trừ tiền vé nhưng NEO trả lời văn bản mẫu — không nhận ra mức độ cấp thiết → user mất tin, cảm thấy bị troll (Duy). NEO nhầm "tìm vé HN→SYD" thành tra cứu mã đặt vé có sẵn — sai hoàn toàn intent (Bách). **User biết sai:** Tự phát hiện khi kết quả không khớp nhu cầu. **User sửa:** Không có cơ chế sửa rõ ràng — chỉ routing sang nhân viên. NEO có note "Neo có thể sai, hãy kiểm tra lại" nhưng không giúp user sửa trong luồng. | **Latency:** Cao >10s — dưới mức kỳ vọng với chatbot 24/7 (Duy). **Cost/request:** Rule-based + keyword hiện tại rẻ, nhưng cần upgrade LLM để hiểu ngữ cảnh → tăng cost ~$0.003-0.005/lượt. **Risk chính:** Real-time giá vé thay đổi liên tục → AI phải kết nối API giá, không được hardcode. Không có session persistence → hỏi lại từ đầu mỗi lần → UX tệ. |

---

## Automation hay Augmentation?

☐ Automation — AI làm thay, user không can thiệp  
☑ **Augmentation — AI gợi ý, user quyết định cuối cùng**

**Justify:** NEO hiện đang cố automation (trả lời thẳng luôn) nhưng accuracy chưa đủ cao → khi sai user không có cơ chế can thiệp kịp thời. Nên chuyển sang augmentation: AI hỏi từng bước (Decision Tree như Duy đề xuất), confirm intent trước khi đưa kết quả — tránh trường hợp "tìm vé" bị hiểu thành "tra mã đặt vé".

---

## Learning Signal

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| 1 | User correction đi vào đâu? | NEO đã có routing sang nhân viên khi user báo sai — nhưng correction chưa đi vào training. Cần log lại: intent gốc của user + output NEO + kết quả thực tế → dùng làm fine-tuning data. |
| 2 | Product thu signal gì để biết tốt lên hay tệ đi? | Feedback 1-5 sau mỗi đoạn chat (Bách ghi nhận — NEO đã có). Cần thêm: tỷ lệ routing sang nhân viên (proxy cho failure rate), tỷ lệ user hỏi lại cùng câu (proxy cho câu trả lời không đủ). |
| 3 | Data thuộc loại nào? | ☑ Real-time (giá vé, lịch bay thay đổi hàng ngày) · ☑ Human-judgment (nhân viên xử lý case phức tạp → correction signal) · ☑ Domain-specific (quy định hành lý, thú cưng, điều lệ vé) · ☐ User-specific · ☐ Khác |

**Có marginal value không?**  
Có — đặc biệt ở 2 loại data:  
(1) **Real-time giá vé** theo ngày và chặng bay — model chung không có, phải kết nối API Vietnam Airlines.  
(2) **Conversation context** — memory về intent trong cùng session (Bách đề xuất memory saver) là data cá nhân hóa thực sự, không ai khác thu được.

---

## Path yếu nhất & Đề xuất cải thiện

**Tổng hợp từ 2 bài:**

| Path | Vũ Đức Duy | Như Gia Bách |
|------|-----------|--------------|
| AI đúng | FAQ cơ bản OK, latency >10s | Câu hỏi đúng hướng NEO → trả lời tốt |
| AI không chắc | Ném văn bản dày + 3-4 link, bắt user tự đọc | Dường như không hỏi lại, routing thẳng sang nhân viên |
| AI sai | Trả lời văn bản mẫu, không nhận ra cấp thiết | Rule-based/keyword → sai intent, không có memory |
| User mất tin | Cảm thấy bị troll khi hỏi mã lỗi | Auto routing sang nhân viên, feedback 1-5 |

**Path yếu nhất: "AI không chắc"** (cả 2 đều ghi nhận)

### As-is
```
User: "Mang thú cưng lên máy bay"
        ↓
NEO: Đoạn văn bản dày đặc + 3-4 link
        ↓
User bị ngợp → tự đọc → bỏ cuộc     ← ĐIỂM GÃY
```

### To-be (Decision Tree — Duy đề xuất)
```
User: "Mang thú cưng lên máy bay"
        ↓
NEO: "Chào bạn! Thú cưng của bạn là?"
     [Chó]  [Mèo]  [Khác]
        ↓ (chọn Chó)
NEO: "Chó và lồng nặng bao nhiêu?"
     [< 6kg]  [6–32kg]
        ↓ (chọn < 6kg)
NEO: "Có thể mang! Giá: ... VNĐ
      Đặt tại: [link]
      Xem chi tiết: [link]"
```

**Thêm / Bớt / Đổi:**
- **Thêm:** Decision Tree hỏi từng bước, memory saver nhớ context trong session, real-time giá vé từ API
- **Bớt:** Văn bản mẫu dày đặc, giao tiếp máy móc, câu trả lời marketing chung chung không đúng sự thật
- **Đổi:** Từ "ném thông tin" → "hỏi để hiểu nhu cầu rồi mới trả lời đúng"

---

*AI Product Canvas — Tổng hợp bài UX — Ngày 5 — VinUni A20 — AI Thực Chiến · 2026*
