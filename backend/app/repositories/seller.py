from sqlalchemy.ext.asyncio import AsyncSession

from database.models.seller import Seller
from repositories.base import BaseRepository


class SellerRepository(BaseRepository[Seller]):
    def __init__(self, session: AsyncSession):
        super().__init__(Seller, session)