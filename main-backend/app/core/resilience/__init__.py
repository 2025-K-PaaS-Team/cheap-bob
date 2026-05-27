"""Resilience 패턴 모음 — Circuit Breaker / Retry.

internal_client (서비스 간 HTTP 호출) 와 외부 SaaS (PortOne 등) 에 동일하게 사용.
"""
from app.core.resilience.retry import retry_with_backoff
from app.core.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)


__all__ = [
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "CircuitState",
    "retry_with_backoff",
]
