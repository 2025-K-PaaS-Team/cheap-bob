from fastapi import APIRouter

from app.domain.auth.router import callback, logout, login, role


auth_router = APIRouter(prefix="/auth", tags=["Auth"])
auth_router.include_router(login.router)
auth_router.include_router(callback.router)
auth_router.include_router(logout.router)


# /user/role 은 auth 도메인의 책임이지만 legacy 클라이언트와의 호환을 위해 /user prefix 를 유지한다.
user_router = APIRouter(prefix="/user", tags=["User-Role"])
user_router.include_router(role.router)
