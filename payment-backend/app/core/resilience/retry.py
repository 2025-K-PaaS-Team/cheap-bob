"""Exponential backoff + jitter — main-backend 의 동일 모듈 미러."""
from typing import Awaitable, Callable, TypeVar
import random
import asyncio

from app.core.logger import get_logger


logger = get_logger("resilience.retry")

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    base_delay_ms: int = 200,
    retriable: tuple[type[Exception], ...] = (Exception,),
    do_not_retry: tuple[type[Exception], ...] = (),
) -> T:
    """func() 를 최대 max_attempts 회 재시도. backoff = base * 2^(n-1) + jitter."""
    attempt = 0
    while True:
        attempt += 1
        try:
            return await func()
        except do_not_retry:
            raise
        except retriable as exc:
            if attempt >= max_attempts:
                logger.warning(
                    "retry.exhausted attempts={} error={}",
                    attempt, type(exc).__name__,
                )
                raise

            delay = (base_delay_ms / 1000) * (2 ** (attempt - 1)) + random.random() * 0.05
            logger.info(
                "retry.scheduled attempt={} delay_sec={} error={}",
                attempt, round(delay, 3), type(exc).__name__,
            )
            await asyncio.sleep(delay)
