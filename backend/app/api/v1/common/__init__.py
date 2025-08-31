from fastapi import APIRouter

from api.v1.common import health, test

router = APIRouter(prefix="/common", tags=["Common"])

router.include_router(health.router)