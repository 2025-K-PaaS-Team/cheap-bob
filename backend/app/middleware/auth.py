from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from services.auth.jwt import JWTService


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, jwt_service: JWTService):
        super().__init__(app)
        self.jwt_service = jwt_service
        self.exclude_paths = [
            "/api/v1/auth/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        # 제외 경로 확인
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)
        
        # Authorization 헤더에서 access_token 가져오기
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            return JSONResponse(
                status_code=401,
                content={"detail": "인증이 필요합니다."}
            )
        
        # Bearer 토큰 형식 확인
        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "유효하지 않은 인증 형식입니다."}
            )
        
        access_token = authorization[7:]  # "Bearer " 제거
        
        # 토큰 검증 및 갱신
        is_valid, new_token, payload = self.jwt_service.verify_and_refresh_token(access_token)
        
        if not is_valid:
            return JSONResponse(
                status_code=401,
                content={"detail": "유효하지 않은 토큰입니다."}
            )
        
        # 요청에 사용자 정보 추가
        request.state.user = payload
        
        # 다음 미들웨어 또는 엔드포인트 호출
        response = await call_next(request)
        
        # 토큰이 갱신되었으면 응답 헤더에 새 토큰 전달
        if new_token:
            response.headers["X-New-Token"] = new_token
        
        return response