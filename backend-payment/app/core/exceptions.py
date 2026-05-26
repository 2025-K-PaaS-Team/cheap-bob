"""도메인 예외 base + FastAPI 전역 핸들러.

backend 와 동일 정책. service 가 던지는 비즈니스 예외는 모두 ``DomainError`` 를 상속하고
class attribute ``status_code`` 에 대응 HTTP status 를 명시한다.
"""
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request


class DomainError(Exception):
    """도메인 예외 base — FastAPI handler 가 ``status_code`` 로 응답을 만든다."""

    status_code: int = 500


async def _domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


def register_domain_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_error_handler)
