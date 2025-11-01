from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from services.auth.jwt import JWTService
from config.settings import settings

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, jwt_service: JWTService):
        super().__init__(app)
        self.jwt_service = jwt_service
        self.exclude_start_paths = [
            "/api/v1/auth/",
            "/api/v1/common/",
            "/api/v1/test/qr",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
        
        self.exclude_end_paths = [
            "/qr/callback"
        ]
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        # WebSocket 요청 인증 제외 (웹소켓은 별도로 처리 해야 함)
        if request.headers.get("upgrade") == "websocket":
            path = request.url.path
            if any(path.endswith(excluded) for excluded in self.exclude_end_paths):
                return await call_next(request)
        
        # 제외 경로 확인
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_start_paths):
            return await call_next(request)
        
        # if any(path.endswith(excluded) for excluded in self.exclude_end_paths):
        #     return await call_next(request)
        
        access_token = None
        
        if settings.ENVIRONMENT == "dev":
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                access_token = authorization[7:]  # "Bearer " 제거
            
            if not access_token:
                access_token = request.query_params.get("token")
            
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
        
        # 다음 미들웨어 또는 엔드포인트 호출
        response = await call_next(request)
        
        if new_token:
            response.set_cookie(
                key="access_token",
                value=new_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=settings.COOKIE_EXPIRE_MINUTES,
                path="/"
            )
        
        return response