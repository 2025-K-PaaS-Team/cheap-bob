from fastapi import APIRouter

from api.v1.test import auth

router = APIRouter(prefix="/test", tags=["Test"])

router.include_router(auth.router)