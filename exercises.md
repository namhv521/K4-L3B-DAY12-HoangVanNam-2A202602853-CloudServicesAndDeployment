# Phiếu Phản Ánh — K4 Level 3B, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay từng dòng trả lời mẫu bằng câu trả lời của bạn.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Hoàng Văn Nam  Mã học viên: 2A202602853

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Ví dụ cụ thể là khi deploy lên Render nhưng quên khai báo
> `AGENT_API_KEY`. Nếu khóa mặc định là `"changeme"`, service vẫn báo chạy thành công và người ngoài có thể đoán khóa này để gọi `/ask`, làm tiêu ngân sách. Với trường bắt buộc hiện tại, `Settings` báo lỗi ngay khi container khởi động; health check không qua nên tôi phát hiện cấu hình thiếu trước khi service nhận traffic

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> Một dòng log tôi thu được là:

> ```json
> {"event": "ask_completed", "level": "info", "timestamp": "2026-09-29T04:29:00.138715+00:00", "user_id": "sv-test", "tokens_in": 3, "tokens_out": 35, "cost_usd": 2.145e-05}
> ```
>
> Từ log này, tôi có thể lọc theo `user_id` và đếm số lần gọi của từng người; đồng thời cộng `cost_usd` hoặc tổng token theo thời gian để theo dõi chi phí và đặt cảnh báo. Chuỗi `print("đã trả lời xong")` không có timestamp, user,token hay chi phí nên không làm được hai việc đó một cách tin cậy

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1.7 GB |
| Multi-stage | 271 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Phần chênh lệch chủ yếu đến từ image `python:3.11` đầy đủ của bản một stage:nó mang theo nhiều công cụ hệ thống, thư viện và thành phần phục vụ build. Bản multi-stage dùng `python:3.11-slim`; stage runtime chỉ nhận các package đã cài từ builder và source cần chạy, nên không mang toàn bộ môi trường build sang image cuối. Số 271 MB được đọc từ `docker images day12-agent:prod` trên máy của tôi; bản một stage lớn khoảng 1.7 GB với base image đầy đủ

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Docker dùng lại các layer từ base image, `WORKDIR`, `COPY requirements.txt` và `RUN pip install` vì nội dung `requirements.txt` không đổi. Từ layer `COPY app ./app` trở đi phải tạo lại do `app/main.py` thay đổi; các lệnh sau đó cũng được đánh giá lại. Nếu đặt `COPY . .` trước `RUN pip install`, chỉ một thay đổi trong source cũng làm mất cache của layer copy và buộc `pip install` chạy lại dù dependency không hề đổi, khiến build chậm hơn

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Chuỗi rủi ro là: lỗi trong API cho phép thực thi lệnh trong container; tiến trình đang là root nên mã độc có quyền root bên trong container; nếu runtime có cấu hình yếu hoặc tồn tại lỗ hổng container escape, kẻ tấn công có thể lợi dụng mount, capability hoặc kernel để tác động tới host với quyền cao. `USER appuser` cắt chuỗi ở bước thứ hai: mã bị chiếm quyền chỉ chạy với UID 10001 và không có quyền root trong container. Đây là lớp giảm thiểu thiệt hại, không thay thế việc bỏ capability và bảo vệ Docker host

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Người dùng có thể gửi tối đa 20 request trong hai giây: gửi 10 request ở khoảng `10:00:59`, rồi gửi tiếp 10 request ở `10:01:00`. Bộ đếm theo phút đồng hồ reset tại giây 00 nên mỗi nhóm vẫn nằm trong hạn mức 10 của một phút, dù thực tế 20 request dồn sát nhau. Sliding window 60 giây vẫn nhìn thấy nhóm đầu khi nhóm sau tới nên sẽ chặn nhóm vượt quá 10

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate limit giới hạn tốc độ request trong 60 giây và trả 429; cost guard giới
> hạn tổng tiền đã tiêu trong tháng và trả 402. Một user chỉ gửi một request
> sau thời gian dài nên rate limit cho qua, nhưng đã dùng hết 10 USD trong
> tháng thì cost guard phải chặn. Ngược lại, user mới chưa tốn đáng kể nên cost
> guard còn cho phép, nhưng gửi request thứ 11 trong cùng cửa sổ 60 giây thì
> rate limit phải chặn.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Nếu gộp hai endpoint và bắt health check phụ thuộc Redis, trình tự sẽ là:Redis mất kết nối; cả ba container cùng trả health check lỗi; orchestrator đánh dấu cả ba là unhealthy và ngừng chuyển traffic; sau ngưỡng retry nó có thể restart cả ba container. Redis vẫn lỗi nên các container mới lại fail và tiếp tục bị restart, tạo restart loop dù tiến trình API vẫn sống. Tách `/health` giúp container không bị restart vô ích, còn `/ready` trả 503 để load balancer tạm ngừng gửi request cho đến khi Redis phục hồi.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Với Redis dùng chung, mỗi request thành công ghi hai message nên `history_length` tăng tuần tự `0, 2, 4, 6, ...` dù request rơi vào instance nào (tối đa 20 message theo cấu hình store). Nếu dùng một dict Python, mỗi container có bản lịch sử riêng. Qua load balancing tôi có thể thấy số liệu nhảy như `0, 0, 2, 0, 2, 4...`, không tăng đều; restart một container còn làm phần lịch sử nằm trong container đó mất hoàn toàn.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Lỗi tôi gặp sau khi deploy là cả `/health`, `/ready` và `/ask` đều trả `HTTP/2 404` với `{"detail":"Not Found"}`, dù header cho thấy origin là Uvicorn. Tôi kiểm tra `app/main.py` và thấy ba route đã được khai báo, đồng thời đối chiếu `Dockerfile` đang chạy đúng `uvicorn app.main:app`; vì vậy lỗi không nằm ở cú pháp URL mà do Render lúc đó vẫn phục vụ bản deploy chưa có các route mới. Sau khi bản deploy từ commit mới nhất hoàn tất, tôi gọi lại: `/health` trả 200, `/ready` trả 200 với `redis: true`, và `/ask` không có key trả 401 đúng thiết kế. Sau đó `/ask` với key thật cũng trả 200
