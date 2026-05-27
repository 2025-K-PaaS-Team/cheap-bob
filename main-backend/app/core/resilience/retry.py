"""Exponential backoff + jitter 재시도 헬퍼.

사용 시 쌓는 순서:
    retry_with_backoff(_call_once)
                ↓
        _call_once = breaker.call(_http_call)
                ↓
            _http_call (httpx 호출 + timeout)

`do_not_retry` 에 `CircuitBreakerOpenError` 를 넣어 회로가 열린 상태에서 의미 없는 재시도
를 막는다. 4xx 같은 비즈니스 실패도 `do_not_retry` 후보 (의미상 retry 가 결과를 바꾸지 못함).
"""
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
    """func() 를 최대 max_attempts 회 재시도.

    delay = base_delay_ms/1000 * 2^(attempt-1) + jitter(0~0.05s).
    `do_not_retry` 에 든 예외는 즉시 위로 전파.
    """
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
