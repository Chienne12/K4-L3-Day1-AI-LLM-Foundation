# K4 — Ngày 1: Bài Tập & Phản Ánh
## Khám Phá LLM API | Phiếu Thực Hành

**Thời lượng:** 4 tiếng
**Cách làm:** Trả lời từng câu ngay sau khi hoàn thành block tương ứng —
đừng để dồn hết về cuối buổi. Thay dòng `*Câu trả lời của bạn*` bằng câu
trả lời thật (chấm tự động sẽ đếm số câu đã trả lời).

---

## Block 1 — API Cơ Bản (trả lời sau Checkpoint 1)

### Câu 1.1 — Độ nhạy của temperature
Gọi `call_openai` với temperature 0.0, 0.5, 1.0 và 1.5 dùng prompt
**"Hãy kể cho tôi một sự thật thú vị về Việt Nam."**

**Bạn nhận thấy quy luật gì qua bốn phản hồi?** (2–3 câu)
> Khi temperature tăng từ 0.0 lên 1.5, phản hồi trở nên đa dạng và sáng tạo hơn; ở mức thấp, nội dung khá nhất quán, còn ở mức cao, chủ đề và số liệu dễ thay đổi. Thời gian phản hồi không có quy luật rõ ràng theo temperature.

### Câu 1.2 — Chọn temperature cho sản phẩm
**Bạn sẽ đặt temperature bao nhiêu cho chatbot hỗ trợ khách hàng, và tại sao?**
> Tôi chọn temperature khoảng 0.2 để câu trả lời ổn định, chính xác nhưng vẫn đủ tự nhiên khi giao tiếp với khách hàng.

### Câu 1.3 — Đánh đổi chi phí
Kịch bản: 10.000 người dùng hoạt động mỗi ngày, mỗi người gọi API 3 lần,
mỗi lần trung bình ~350 token đầu ra.

**Ước tính GPT-4o đắt hơn GPT-4o-mini bao nhiêu lần cho workload này? Nêu một
trường hợp GPT-4o xứng đáng với chi phí và một trường hợp nên dùng mini:**
> Với 10,5 triệu token đầu ra mỗi ngày, GPT-4o tốn khoảng 105 USD còn GPT-4o-mini khoảng 6,3 USD, tức đắt hơn khoảng 16,7 lần. GPT-4o phù hợp với yêu cầu phân tích phức tạp, còn mini phù hợp để trả lời FAQ hoặc tác vụ lặp lại.

---

## Block 2 — System Prompt & Token (trả lời sau Checkpoint 2)

### Câu 2.1 — Sức mạnh của persona
Gọi `chat_with_system_prompt` hai lần với cùng câu hỏi
**"Giải thích blockchain là gì?"** nhưng hai system prompt khác nhau:
- "Bạn là giáo viên tiểu học, giải thích thật đơn giản cho trẻ 8 tuổi."
- "Bạn là chuyên gia tài chính, trả lời chuyên sâu bằng thuật ngữ kỹ thuật."

**Hai phản hồi khác nhau như thế nào (độ dài, từ vựng, ví dụ)? System prompt
ảnh hưởng đến hành vi model ra sao?** (3–4 câu)
> Persona giáo viên tạo câu trả lời ngắn, dùng từ đơn giản và ví dụ gần gũi như cuốn sổ chung. Persona chuyên gia tạo câu trả lời dài hơn, dùng các thuật ngữ như phi tập trung, đồng thuận và mật mã học. System prompt định hướng vai trò, giọng điệu và mức độ chuyên sâu của model.

### Câu 2.2 — tiktoken vs đếm từ
Chọn một đoạn văn tiếng Việt ~100 từ. So sánh số token theo `count_tokens`
(tiktoken) với ước lượng `số từ / 0.75` mà Part 1 đã dùng.

**Hai con số chênh nhau bao nhiêu phần trăm? Vì sao tiếng Việt thường tốn
nhiều token hơn tiếng Anh cùng độ dài?**
> Với đoạn tiếng Việt 102 từ, tiktoken đếm được 134 token, còn công thức số từ/0,75 ước tính 136 token, chênh khoảng 1,5%. Tiếng Việt thường tốn nhiều token hơn vì dấu thanh và cách bộ mã hóa tách từ thành nhiều đơn vị nhỏ.

---

## Block 3 — Streaming & Độ Bền (trả lời sau Checkpoint 3)

### Câu 3.1 — Trải nghiệm người dùng với streaming
**Streaming quan trọng nhất trong trường hợp nào, và khi nào thì
non-streaming lại phù hợp hơn?** (1 đoạn văn)
> Streaming hữu ích nhất khi phản hồi dài hoặc chatbot cần hiển thị nội dung ngay để người dùng không phải chờ. Non-streaming phù hợp với câu trả lời ngắn, dữ liệu có cấu trúc hoặc khi ứng dụng cần nhận đủ kết quả rồi mới xử lý.

### Câu 3.2 — Vì sao backoff theo cấp số nhân?
**So với delay cố định (ví dụ luôn chờ 1 giây), exponential backoff có lợi
thế gì khi API bị quá tải? Điều gì xảy ra nếu hàng nghìn client cùng retry
với delay cố định giống nhau?**
> Exponential backoff giãn dần thời gian retry, giúp giảm áp lực để API có thời gian phục hồi. Nếu hàng nghìn client cùng retry theo delay cố định, chúng có thể gửi lại đồng thời và tiếp tục làm server quá tải; có thể thêm jitter để phân tán request tốt hơn.

---

## Block 4 — Mini-Project (trả lời sau Checkpoint 4)

### Câu 4.1 — Thiết kế persona
**Bạn chọn persona gì cho trợ lý của mình? Viết lại system prompt đó và giải
thích 1–2 lựa chọn từ ngữ quan trọng trong prompt (ví dụ: vì sao yêu cầu
"trả lời ngắn gọn", vì sao chỉ định ngôn ngữ...):**
> Tôi chọn persona: “Bạn là trợ giảng thân thiện của khóa AI, trả lời ngắn gọn bằng tiếng Việt.” Từ “thân thiện” tạo giọng điệu gần gũi, còn “ngắn gọn bằng tiếng Việt” giúp câu trả lời dễ hiểu và đúng nhu cầu người học.

### Câu 4.2 — Hạn chế & cải thiện
**Trợ lý của bạn hiện có hạn chế lớn nhất là gì (ví dụ: history chỉ 3 lượt,
không có bộ nhớ dài hạn, không kiểm duyệt nội dung...)? Đề xuất một cải
thiện cụ thể và mô tả ngắn cách triển khai:**
> Hạn chế lớn nhất là trợ lý chỉ giữ ba lượt hội thoại nên dễ mất ngữ cảnh cũ. Tôi sẽ tóm tắt các lượt cũ và đưa bản tóm tắt vào system message để duy trì ngữ cảnh mà không dùng quá nhiều token.

---

## Danh Sách Kiểm Tra Nộp Bài

- [ ] `python grade.py` — xem điểm tự động, mục tiêu ≥ 75/100
- [ ] Cả 4 checkpoint pytest đều pass
- [ ] Tất cả 9 câu trong file này đã được trả lời
- [ ] Đã copy bài làm vào folder `solution/`, push lên fork và dán link trên trang bài Lab ở VLearn trước 23:59 ngày 11/09/2026
