# Individual reflection — Nhữ Gia Bách (2A202600248)

## 1. Role
Product owner + planner/UI integrator. Phụ trách chuyển spec thành MVP chạy được, chuẩn hóa mock data, hoàn thiện logic route planner, kết nối workflow tool-call, và build giao diện Streamlit để demo.

## 2. Đóng góp cụ thể
- Chuyển spec draft thành project structure hoàn chỉnh cho demo EV trip planner
- Điều chỉnh model và data loader để code đọc đúng schema mock data mà không phải sửa dữ liệu gốc
- Hoàn thiện route planner:
  - tính tính khả thi của hành trình
  - chọn điểm dừng sạc
  - tính SoC khi đến/rời trạm
  - tính thời gian sạc và tổng thời gian hành trình
- Tối ưu planner khi số lượng mock station tăng:
  - giảm chi phí search
  - chỉ build geometry khi cần
  - ưu tiên OSRM cho distance/duration, có fallback khi OSRM lỗi
- Build và chỉnh UI Streamlit:
  - chọn origin/destination từ option
  - hiển thị stop list, warnings, total time, mức pin dự phòng
  - xử lý case infeasible
  - chuyển visible UI text sang tiếng Việt
- Tách workflow theo kiểu tool-call:
  - planner tool
  - validation tool
  - summary tool
- Chỉnh prompt và summary layer để tránh hallucination, đồng bộ format input/output, rồi chuyển prompt/payload sang English nội bộ
- Viết/chỉnh test cho planner, workflow, summary service và cập nhật test khi dataset thay đổi
- Xử lý nhiều issue kỹ thuật trong quá trình merge, import path, gitignore, pycache, requirements, env

## 3. SPEC mạnh/yếu
- Mạnh nhất: nhóm đã giữ được đúng core value của spec, tức là giải quyết bài toán "range anxiety" bằng route planning có tính đến SoC, mức pin an toàn, điểm dừng sạc và cảnh báo. Demo hiện tại đã hiện thực được phần lõi của MVP khá rõ.
- Yếu nhất: demo vẫn còn cách khá xa vision đầy đủ trong spec. Hiện tại mới có 1 route, dữ liệu trạm còn là mock/static, mô hình tiêu thụ và charging còn đơn giản, chưa có multi-vehicle, chưa có real-time station validation, và LLM mới chủ yếu làm lớp diễn giải chứ chưa phải reasoning agent đầy đủ.

## 4. Đóng góp khác
- Tạo `requirements.txt`, `.env.example`, `.gitignore` và hướng dẫn setup để project chạy được ổn định hơn
- Dọn các lỗi import/package để Streamlit app chạy đúng theo package path
- Kiểm tra và sửa merge conflict trong các file quan trọng như planner, data loader, app, tests
- Viết tài liệu giải thích codebase, limitations của demo so với spec.
- Hỗ trợ chuẩn hóa cách commit, test, push code và giải thích cho teammate cách đọc kết quả pytest

## 5. Điều học được
Trước khi làm hackathon, mình nghĩ phần khó nhất là viết thuật toán planner. Sau khi làm mới thấy phần khó hơn là giữ cho toàn bộ hệ thống nhất quán giữa spec, mock data, planner, summary và UI. Chỉ cần một lớp diễn giải hoặc một assumption dữ liệu lệch đi là output đã nhìn “đúng cú pháp nhưng sai logic”. Mình học được rằng với AI product, deterministic logic và data contract quan trọng không kém gì prompt hay model. Nếu planner chưa chặt thì LLM summary sẽ rất dễ làm người xem hiểu sai hệ thống.

## 6. Nếu làm lại
Mình sẽ chốt data contract và test cases sớm hơn. Ở giai đoạn đầu nhóm thay đổi dataset, schema và planner khá nhiều, nên phải update code và test nhiều lần. Nếu ngay từ đầu khóa rõ schema mock data, route scenarios, warning rules và output contract thì tốc độ build sẽ nhanh hơn và ít bug integration hơn.

## 7. AI giúp gì / AI sai gì
- **Giúp:** AI hỗ trợ rất tốt trong việc scaffold project, đề xuất structure, tạo test cases, rà soát inconsistency giữa prompt và planner, và giúp debug nhanh các lỗi import, merge, cache, UI text, workflow. AI cũng giúp rút ngắn thời gian chuyển từ spec sang MVP code chạy được.
- **Sai/mislead:** AI nhiều lần có xu hướng đi quá nhanh so với scope thật, ví dụ tự scaffold code khi chưa xin phép, hoặc đề xuất những phần “đẹp” nhưng chưa cần cho MVP. Ngoài ra, ở summary layer nếu prompt/input chưa chặt thì AI có thể tự bịa số liệu, stop hoặc total time. Bài học là AI hỗ trợ tốt cho tốc độ, nhưng người làm vẫn phải kiểm soát scope, data contract và logic rất chặt.
