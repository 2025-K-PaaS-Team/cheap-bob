from fastapi import APIRouter

from api.v1.user import role

router = APIRouter(prefix="/user")

router.include_router(role.router)