from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, DateTime, String
from datetime import datetime

from app.database.session import Base


class Seller(Base):
    """판매자 계정. email 이 인증 principal 이자 PK.

    customer 와 마찬가지로 auth 에서 분리해 seller 도메인 소유. auth 는 OAuth/JWT 전담.
    """

    __tablename__ = "sellers"
    __mapper_args__ = {"eager_defaults": True}

    email: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
