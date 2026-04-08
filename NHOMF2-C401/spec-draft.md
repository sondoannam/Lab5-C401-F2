# SPEC draft — Lab5-C401-F2

## Track: A — VinFast

## Problem statement

Chủ xe VinFast gặp lỗi hoặc cần bảo dưỡng không biết phải làm gì — đèn cảnh báo bật không hiểu nghĩa, gọi hotline chờ lâu, Google ra kết quả không liên quan VinFast. AI hỏi triệu chứng xe → chẩn đoán lỗi có thể → gợi ý hành động (tự xử / đặt lịch bảo dưỡng).

---

## Canvas draft

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Trả lời** | **User:** Chủ xe VinFast (VF3, VF5, VF8...) mới mua, chưa quen xe điện. **Pain:** Đèn cảnh báo bật không biết nghĩa, gọi hotline chờ 10-15 phút, Google ra kết quả xe xăng hoặc xe nước ngoài. **AI giải:** Hỏi triệu chứng cụ thể → map với manual VinFast → gợi ý lỗi + mức độ nghiêm trọng + hành động tiếp theo. | **Khi AI sai:** Chủ xe bỏ qua lỗi thật → nguy hiểm khi lái. Phải có disclaimer rõ + nút "Đặt lịch gặp kỹ thuật viên" luôn hiển thị. **User biết sai:** Khi ra garage và kỹ thuật viên nói khác → correction signal. **User sửa:** Rate câu trả lời + mô tả lỗi thật → AI học. | **Cost:** RAG trên manual VinFast + LLM call ~$0.003-0.005/lượt. **Latency:** <3s chấp nhận được. **Risk chính:** Triệu chứng mô tả mơ hồ ("xe kêu"), nhiều lỗi overlap; AI không được tự tin 100% với lỗi liên quan an toàn. |

**Auto hay Augmentation?** Augmentation — AI gợi ý chẩn đoán + hành động, chủ xe quyết định có đặt lịch không. Không tự động book lịch.

**Learning signal:**
- Explicit: user rate câu trả lời (hữu ích / không hữu ích)
- Correction: user mô tả kết quả thực tế sau khi ra garage
- Implicit: user có click "Đặt lịch bảo dưỡng" sau gợi ý không

---

## User Stories — 4 paths

| Path | Scenario | UI xử lý |
|------|----------|----------|
| AI đúng | User: "Xe VF8 bật đèn cảnh báo hình bánh xe màu vàng" → AI: "Đây là cảnh báo áp suất lốp thấp, kiểm tra lốp trước khi lái" | Hiện mức độ: ⚠️ Cần xử lý sớm + nút "Đặt lịch" |
| AI không chắc | User: "Xe kêu lạ khi phanh" → AI không đủ thông tin | Hỏi lại: "Tiếng kêu xuất hiện khi nào? Phanh gấp hay phanh nhẹ?" |
| AI sai | AI gợi ý sai lỗi → user ra garage biết khác | Nút "Kết quả thực tế là..." → user nhập → lưu correction |
| User mất tin | User không tin AI chẩn đoán xe | Luôn hiển thị: "Để chắc chắn, đặt lịch với kỹ thuật viên VinFast" |

---

## Eval metrics

- **Precision:** Trong số lỗi AI chẩn đoán → đúng bao nhiêu % (ưu tiên: sai chẩn đoán nguy hiểm hơn bỏ sót)
- **Target:** Top-3 diagnosis precision ≥ 75% trên test set manual VinFast
- **Threshold dừng:** Nếu user correction rate > 40% → review lại prompt + data
- **Kill criteria:** Cost > benefit sau 2 tháng pilot hoặc có incident an toàn do AI sai

---

## Failure modes

| Failure | Xác suất | Impact | Mitigation |
|---------|----------|--------|------------|
| AI chẩn đoán sai lỗi an toàn (phanh, lái) | Thấp | Rất cao | Disclaimer bắt buộc + escalate sang kỹ thuật viên ngay |
| Triệu chứng mơ hồ → AI đoán mò | Cao | Trung bình | Hỏi lại thay vì đoán; tối đa 3 câu hỏi làm rõ |
| Manual VinFast không có lỗi này | Trung bình | Thấp | Trả lời "Moni chưa có thông tin, vui lòng liên hệ hotline" |
| User over-trust AI, bỏ qua garage | Trung bình | Cao | Luôn gợi ý "xác nhận với kỹ thuật viên" dù AI tự tin |

---

## ROI 3 kịch bản

| | Conservative | Realistic | Optimistic |
|---|---|---|---|
| User/tháng | 1,000 | 10,000 | 50,000 |
| Tiết kiệm/user | 15 phút chờ hotline | 15 phút + 1 lần khám sai | 15 phút + tránh 1 lần hỏng xe nặng |
| Cost inference | ~$50/tháng | ~$500/tháng | ~$2,500/tháng |
| Benefit ước tính | Giảm tải hotline ~5% | Giảm tải ~30%, tăng NPS | Giảm tải ~60%, upsell bảo dưỡng |
| Net | Hòa vốn | Dương | Dương rõ |

**Kill criteria:** Cost > $2,000/tháng mà MAU < 5,000 → dừng sau 2 tháng.

---

## Mini AI spec

**Input:** Text mô tả triệu chứng xe + model xe (VF3/VF5/VF6/VF7/VF8/VF9)

**Output:** Top-3 lỗi có thể + mức độ nghiêm trọng (🔴/🟡/🟢) + hành động gợi ý

**Architecture:** RAG — embed manual VinFast theo từng model → retrieve relevant chunks → LLM synthesize

**Confidence handling:**
- High confidence (>80%): hiện chẩn đoán + hành động
- Low confidence (<50%): hỏi lại tối đa 3 câu
- Lỗi an toàn (phanh/lái/pin): luôn escalate dù confidence cao

**Data cần:** Manual xe VinFast (PDF công khai), FAQ bảo dưỡng, lịch sử correction từ user

---

## Phân công

| Thành viên | Phần phụ trách |
|------------|----------------|
| Đoàn Nam Sơn | Canvas + Failure modes |
| Hoàng Vĩnh Giang | User stories 4 paths + UX flow |
| Như Gia Bách | Eval metrics + Kill criteria |
| Trần Quang Quí | ROI 3 kịch bản + Mini AI spec |
| Vũ Đức Duy | Prototype research + RAG setup + prompt test |

---

*SPEC draft — Track A VinFast — Lab5-C401-F2 — VinUni A20 — AI Thực Chiến · 2026*
