from fastapi import APIRouter

from api.v1.auth import login, callback

router = APIRouter(prefix="/auth", tags=["Auth"])

router.include_router(login.router)
router.include_router(callback.router)