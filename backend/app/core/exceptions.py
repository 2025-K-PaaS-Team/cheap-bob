"""도메인 예외 base + FastAPI 전역 핸들러.

각 도메인의 service 레이어가 던지는 비즈니스 예외는 모두 ``DomainError`` 를 상속하고
class attribute ``status_code`` 에 대응 HTTP status 를 명시한다. 라우터는 더이상
``try/except → HTTPException`` 변환을 하지 않고, 본 모듈의 핸들러가 일괄 처리한다.
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
    """FastAPI 앱에 ``DomainError`` 핸들러를 등록한다.

    FastAPI 는 base class 핸들러로 sub-class 도 잡으므로, 모든 도메인 예외가 본 핸들러로
    수렴한다. ``main.create_app`` 에서 호출.
    """
    app.add_exception_handler(DomainError, _domain_error_handler)
