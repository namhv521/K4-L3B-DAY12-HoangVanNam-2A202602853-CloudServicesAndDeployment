# ═══════════════════════════════════════════════════════════════════
# CP2 — Containerization (production-ready)
# ═══════════════════════════════════════════════════════════════════

# ── Stage 1: builder ──────────────────────────────────────────────
# Stage này cài thư viện (có thể cần compiler). Nó sẽ bị bỏ đi sau,
# chỉ giữ lại /install — nên image cuối không mang theo build tools.
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy requirements TRƯỚC — Docker cache layer này riêng.
# Nếu chỉ sửa code (không đổi requirements.txt), layer pip install
# được dùng lại từ cache → build nhanh hơn nhiều.
COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────
# Chỉ copy KẾT QUẢ từ builder, không mang theo compiler hay build tools.
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy thư viện đã cài từ stage builder
COPY --from=builder /install /usr/local

# Tạo user thường (không phải root).
# Container chạy root: nếu có lỗ hổng trong app, kẻ tấn công
# có thể thoát container với quyền root trên host.
RUN useradd --create-home --uid 10001 appuser

# Copy source code (SAU khi copy requirements → cache hit khi chỉ đổi code)
COPY app ./app
COPY utils ./utils

# Chuyển sang user thường trước khi chạy
USER appuser

# Cloud (Railway, Render, Cloud Run) tự gán cổng qua biến PORT.
# 0.0.0.0 để nhận kết nối từ bên ngoài container (127.0.0.1 thì không ai gọi được).
EXPOSE 8000

# Kiểm tra process còn sống không — orchestrator dùng để quyết định có restart không.
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:${PORT:-8000}/health').read()" || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
