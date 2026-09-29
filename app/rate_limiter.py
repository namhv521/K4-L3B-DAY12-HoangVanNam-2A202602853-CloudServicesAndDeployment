"""CP3 — Rate limiting bằng thuật toán sliding window.

Đếm số request trong 60 giây **gần nhất** (cửa sổ trượt), thay vì đếm theo
phút đồng hồ. Đếm theo phút đồng hồ có lỗ hổng: 10 request lúc 10:00:59 và
10 request lúc 10:01:01 = 20 request trong 2 giây mà vẫn "đúng luật".

Cấu trúc dữ liệu: Redis Sorted Set (ZSET), score = timestamp của request.
"""

from __future__ import annotations

import time
import uuid

from fastapi import HTTPException, status

WINDOW_SECONDS = 60


class RateLimiter:
    def __init__(self, client, limit_per_minute: int) -> None:
        self.client = client
        self.limit = limit_per_minute

    @staticmethod
    def _key(user_id: str) -> str:
        """CHO SẴN — mỗi user một key riêng."""
        return f"ratelimit:{user_id}"

    def hit_count(self, user_id: str, now: float | None = None) -> int:
        """Số request của user trong ``WINDOW_SECONDS`` giây gần nhất."""
        now = now if now is not None else time.time()
        key = self._key(user_id)
        # Vứt các entry đã ra khỏi cửa sổ 60 giây
        self.client.zremrangebyscore(key, 0, now - WINDOW_SECONDS)
        # Đếm số request còn trong cửa sổ
        return self.client.zcard(key)

    def check(self, user_id: str, now: float | None = None) -> None:
        """Cho qua nếu còn quota, ngược lại raise 429.

        THỨ TỰ QUAN TRỌNG: kiểm tra trước → ghi nhận sau.
        Ghi trước rồi đếm sẽ chặn nhầm ngay ở request thứ ``limit``.
        """
        now = now if now is not None else time.time()
        key = self._key(user_id)

        # 1. Kiểm tra trước
        count = self.hit_count(user_id, now)
        if count >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="rate limit exceeded",
                headers={"Retry-After": str(WINDOW_SECONDS)},
            )

        # 2. Ghi nhận sau — member phải DUY NHẤT:
        #    nếu 2 request cùng timestamp mà trùng member → ZSET chỉ giữ một
        self.client.zadd(key, {f"{now}:{uuid.uuid4().hex}": now})
        self.client.expire(key, WINDOW_SECONDS)
