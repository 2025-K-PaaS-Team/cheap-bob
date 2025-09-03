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
            "/api/v1/common/",
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
        
        access_token = None
        
        # 1. Authorization 헤더에서 토큰 확인
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            access_token = authorization[7:]  # "Bearer " 제거
        
        # 2. URL 쿼리 파라미터에서 토큰 확인
        if not access_token:
            access_token = request.query_params.get("token")
        
        # 3. 쿠키에서 토큰 확인 (옵션)
        if not access_token:
            access_token = request.cookies.get("access_token")
        
        if not access_token:
            return JSONResponse(
                status_code=401,
                content={"detail": "인증이 필요합니다."}
            )
        
        # 토큰 검증 및 갱신
        is_valid, new_token, payload = self.jwt_service.verify_and_refresh_token(access_token)
        
        if not is_valid:
            return JSONResponse(
                status_code=401,
                content={"detail": "유효하지 않은 토큰입니다."}
            )
        
        # 요청에 사용자 정보 추가
        request.state.user = payload
        request.state.new_token = new_token  # 갱신된 토큰 저장
        
        # 다음 미들웨어 또는 엔드포인트 호출
        response = await call_next(request)
        
        # 토큰이 갱신되었으면 응답 헤더에 새 토큰 전달
        if new_token:
            response.headers["X-New-Token"] = new_token
        
        return response