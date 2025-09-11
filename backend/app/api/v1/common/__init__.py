from fastapi import APIRouter

from api.v1.common import health, options

router = APIRouter(prefix="/common")

router.include_router(health.router)
router.include_router(options.router)