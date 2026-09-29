"""CP3 — Xác thực bằng API key.

Public URL = ai cũng gọi được. Không có lớp này, hóa đơn LLM của bạn do
người lạ quyết định.
"""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from .config import get_settings

ANONYMOUS_USER = "anonymous"


def verify_api_key(
    x_api_key: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> str:
    """Kiểm tra header ``X-API-Key``; trả về user_id nếu hợp lệ.

    Dùng ``secrets.compare_digest`` thay vì ``==`` để tránh timing attack:
    toán tử ``==`` dừng ngay tại ký tự đầu khác nhau → thời gian phản hồi
    rò rỉ thông tin về khóa. ``compare_digest`` luôn chạy hết chuỗi.
    """
    expected = get_settings().agent_api_key

    # Thiếu key hoặc key sai → 401
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing API key",
        )

    # Trả user_id do client gửi, hoặc "anonymous" nếu không có
    return x_user_id if x_user_id else ANONYMOUS_USER
