from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.seller import Seller
from app.repositories.base import BaseRepository


class SellerRepository(BaseRepository[Seller]):
    def __init__(self, session: AsyncSession):
        super().__init__(Seller, session)