from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie

from config.settings import settings
from database.mongodb_models import OrderHistoryItem, SellerWithdrawReservation, CustomerWithdrawReservation

class MongoDB:
    """MongoDB 클라이언트 및 데이터베이스 관리"""
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database: AsyncIOMotorDatabase = None
        
    async def connect(self):
        """MongoDB 연결 및 초기화"""
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.database = self.client[settings.MONGODB_NAME]
        
        await init_beanie(
            database=self.database,
            document_models=[OrderHistoryItem, SellerWithdrawReservation, CustomerWithdrawReservation]
        )
        
    async def disconnect(self):
        """MongoDB 연결 종료"""
        if self.client:
            self.client.close()
            
mongodb = MongoDB()


async def init_mongodb():
    """MongoDB 초기화 (앱 시작 시 호출)"""
    await mongodb.connect()
    

async def close_mongodb():
    """MongoDB 종료 (앱 종료 시 호출)"""
    await mongodb.disconnect()