from fastapi import APIRouter

from api.v1 import auth, customer, seller, common, test

api_router = APIRouter()

# 인증 관련 API (공개)
api_router.include_router(auth.router)

# 인증 불필요
api_router.include_router(common.router)

# Customer 전용
api_router.include_router(customer.router)

# Seller 전용
api_router.include_router(seller.router)

# Test
api_router.include_router(test.router)