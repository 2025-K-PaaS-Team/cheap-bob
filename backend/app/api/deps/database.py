from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db


AsyncSessionDep = Annotated[AsyncSession, Depends(get_db)]