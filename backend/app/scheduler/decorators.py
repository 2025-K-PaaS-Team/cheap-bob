"""scheduler worker 공통 데코레이터.

worker 진입점은 APScheduler 가 호출하므로 예외가 위로 새면 다음 fire 까지 영향을 줄 수
있다. ``@log_and_swallow`` 는 예외를 ``logger.exception`` 으로 trace + fallback 반환으로
삼켜 cron 자체의 안정성을 보장한다.

성공 로그/timing 은 worker 마다 포맷이 달라 본 데코레이터에 통합하지 않는다. worker 는
함수 본문 안에서 직접 측정/로깅한다.
"""
from typing import Any, Awaitable, Callable, TypeVar
from functools import wraps


T = TypeVar("T")


def log_and_swallow(
    task_label: str, logger, *, fallback: Any = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[Any]]]:
    """worker entry point 의 try/except 패턴을 데코레이터로 추출.

    Args:
        task_label: 예외 메시지 prefix — ``"{task_label} 중 오류 발생"`` 형태로 기록.
        logger: 호출 worker module 의 logger (loguru 네임스페이스 유지).
        fallback: 예외 시 반환값. APScheduler 는 반환값을 사용하지 않으므로 보통 ``None``,
            ``int`` 등 caller 가 count 를 기대하면 ``0``.
    """
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception:
                logger.exception(f"{task_label} 중 오류 발생")
                return fallback
        return wrapper
    return decorator
