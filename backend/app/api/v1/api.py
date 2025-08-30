from fastapi import APIRouter

from api.v1 import auth, test, payment, search

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(test.router)
api_router.include_router(payment.router)
api_router.include_router(search.router)