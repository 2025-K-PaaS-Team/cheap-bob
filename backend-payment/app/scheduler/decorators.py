"""scheduler worker 공통 데코레이터."""
from typing import Any, Awaitable, Callable, TypeVar
from functools import wraps


T = TypeVar("T")


def log_and_swallow(
    task_label: str, logger, *, fallback: Any = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[Any]]]:
    """worker entry point 의 try/except 패턴을 데코레이터로 추출."""
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
