# Thông Tin Deploy — Checkpoint 5

> Điền file này sau khi deploy xong. `pytest tests/test_cp5.py` đọc file này
> để tìm địa chỉ service của bạn và gọi thử.
>
> **Chỉ ghi TÊN biến môi trường, tuyệt đối không dán giá trị API key vào đây.**
> Repo này công khai — dán khóa vào là mất khóa.

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Hoàng Văn Nam |
| Mã học viên | 2A202602853 |
| Repo | https://github.com/namhv521/K4-L3B-DAY12-HoangVanNam-2A202602853-CloudServicesAndDeployment |

## Service

| Mục | Nội dung |
|-----|----------|
| Public URL | https://day12-agent-ntit.onrender.com |
| Platform | Render |
| Ngày deploy | 29/09/2026 |

## Biến Môi Trường Đã Set Trên Cloud

Ghi tên biến và **nguồn giá trị**, không ghi giá trị:

| Biến | Đã set | Ghi chú |
|------|--------|---------|
| `PORT` | ✅ | platform tự gán |
| `AGENT_API_KEY` | ✅ | đặt trong dashboard, không nằm trong repo |
| `REDIS_URL` | ✅ | Redis service `day12-redis` trên Render |
| `RATE_LIMIT_PER_MINUTE` | ✅ | 10 |
| `MONTHLY_BUDGET_USD` | ✅ | 10.0 |
| `LOG_LEVEL` | ✅ | INFO |

## Lệnh Kiểm Tra

Public URL sử dụng: `https://day12-agent-ntit.onrender.com`

```bash
# 1. Liveness — mong đợi 200 {"status":"ok"}
curl -i https://day12-agent-ntit.onrender.com/health

# 2. Readiness — mong đợi 200 {"status":"ready"} (đã nối được Redis)
curl -i https://day12-agent-ntit.onrender.com/ready

# 3. Không có API key — mong đợi 401
curl -i -X POST https://day12-agent-ntit.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'

# 4. Có API key — mong đợi 200 kèm câu trả lời
curl -i -X POST https://day12-agent-ntit.onrender.com/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AGENT_API_KEY" \
  -H "X-User-Id: sv-test" \
  -d '{"question":"Deploy là gì?"}'

# 5. Rate limit — gọi 15 lần, những lần cuối phải trả 429
for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code} " -X POST https://day12-agent-ntit.onrender.com/ask \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $AGENT_API_KEY" \
    -H "X-User-Id: sv-test" \
    -d '{"question":"test"}'
done; echo
```

## Kết Quả Chạy Thật


```
curl -i https://day12-agent-ntit.onrender.com/health
HTTP/2 200
date: Tue, 29 Sep 2026 04:10:02 GMT
content-type: application/json
cf-cache-status: DYNAMIC
rndr-id: 918404fd-ad24-480f
server: cloudflare
vary: Accept-Encoding
x-render-origin-server: uvicorn
cf-ray: a42822c3f8176198-SIN
alt-svc: h3=":443"; ma=86400

{"status":"ok","service":"day12-agent","version":"1.0.0"}




lenovo@DESKTOP-1ND9CM8:/mnt/c/WINDOWS/system32$ curl -i https://day12-agent-ntit.onrender.com/ready
HTTP/2 200
date: Tue, 29 Sep 2026 04:10:41 GMT
content-type: application/json
rndr-id: 09edfe5c-e783-4703
server: cloudflare
vary: Accept-Encoding
x-render-origin-server: uvicorn
cf-cache-status: DYNAMIC
cf-ray: a42823b61f3fce15-SIN
alt-svc: h3=":443"; ma=86400

{"status":"ready","redis":true}




lenovo@DESKTOP-1ND9CM8:/mnt/c/WINDOWS/system32$ curl -i -X POST https://day12-agent-ntit.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
HTTP/2 401
date: Tue, 29 Sep 2026 04:11:05 GMT
content-type: application/json
rndr-id: e1b9302b-078d-4547
server: cloudflare
vary: Accept-Encoding
x-render-origin-server: uvicorn
cf-cache-status: DYNAMIC
cf-ray: a42824497c1efd6c-SIN
alt-svc: h3=":443"; ma=86400

{"detail":"invalid or missing API key"}



curl -i -X POST "https://day12-agent-ntit.onrender.com/ask" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AGENT_API_KEY" \
  -H "X-User-Id: sv-test" \
  -d '{"question":"Deploy là gì?"}'
HTTP/2 200
date: Tue, 29 Sep 2026 04:16:38 GMT
content-type: application/json
cf-cache-status: DYNAMIC
rndr-id: af43e333-2436-45a0
server: cloudflare
vary: Accept-Encoding
x-render-origin-server: uvicorn
cf-ray: a4282c6dfde7fdab-SIN
alt-svc: h3=":443"; ma=86400

{"answer":"Câu hỏi hay. Deploy là gì thường được giải quyết bằng cách chuẩn hóa môi trường chạy: cùng một image chạy giống nhau ở laptop và trên cloud.","user_id":"sv-test","history_length":0,"cost_usd":2.145e-05,"tokens":{"in":3,"out":35}}





for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code} " \
    -X POST "https://day12-agent-ntit.onrender.com/ask" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $AGENT_API_KEY" \
    -H "X-User-Id: rate-limit-test" \
    -d '{"question":"test"}'
done
echo
200 200 200 200 200 000 200 200 200 200 200 429 429 429 429


```

`/ask` có khóa và kiểm tra rate limit cần chạy trong môi trường có biến
`AGENT_API_KEY`; giá trị khóa không được ghi vào repository.

## Ảnh Chụp Màn Hình

Đặt ảnh trong thư mục `screenshots/`:

- `screenshots/dashboard.png` — trang quản lý service trên platform
- `screenshots/health.png` — kết quả gọi `/health` từ trình duyệt hoặc curl

---

