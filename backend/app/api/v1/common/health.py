from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def health_check():
    """
    인증 불필요한 API들 추가 될 거임
    """
    return {
        "status": "OK"
    }