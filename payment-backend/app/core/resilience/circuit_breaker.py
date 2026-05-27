"""Circuit Breaker — main-backend 의 동일 모듈 미러.

CLOSED / OPEN / HALF_OPEN 의 3-state. 호출이 임계치 만큼 연속 실패하면 OPEN — 즉시 차단.
recovery_timeout 경과 후 HALF_OPEN — 1건 시험 호출. 성공이면 CLOSED 로 복귀.
"""
import time
import enum
import asyncio

from app.core.logger import get_logger


logger = get_logger("resilience.circuit_breaker")


class CircuitState(str, enum.Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(Exception):

    def __init__(self, name: str):
        super().__init__(f"circuit '{name}' is OPEN")
        self.name = name


class CircuitBreaker:

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 10.0,
        expected_exception: type[Exception] = Exception,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self._state: CircuitState = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at: float | None = None
        self._lock = asyncio.Lock()


    @property
    def state(self) -> CircuitState:
        return self._state


    @property
    def failure_count(self) -> int:
        return self._failure_count


    def snapshot(self) -> dict:
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "opened_at": self._opened_at,
        }


    async def call(self, func, *args, **kwargs):
        await self._before_call()
        try:
            result = await func(*args, **kwargs)
        except self.expected_exception:
            await self._on_failure()
            raise
        else:
            await self._on_success()
            return result


    async def _before_call(self) -> None:
        async with self._lock:
            if self._state == CircuitState.OPEN:
                if self._should_attempt_recovery():
                    self._state = CircuitState.HALF_OPEN
                    logger.info("circuit.half_open name={}", self.name)
                else:
                    raise CircuitBreakerOpenError(self.name)


    def _should_attempt_recovery(self) -> bool:
        if self._opened_at is None:
            return True
        return (time.monotonic() - self._opened_at) >= self.recovery_timeout


    async def _on_success(self) -> None:
        async with self._lock:
            if self._state != CircuitState.CLOSED:
                logger.info("circuit.closed name={}", self.name)
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._opened_at = None


    async def _on_failure(self) -> None:
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._open()
                return

            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._open()


    def _open(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = time.monotonic()
        logger.warning(
            "circuit.open name={} failure_count={} recovery_in={}s",
            self.name, self._failure_count, self.recovery_timeout,
        )
