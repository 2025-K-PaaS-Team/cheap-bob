from fastapi import APIRouter

from api.v1.common import options

router = APIRouter(prefix="/common")

router.include_router(options.router)