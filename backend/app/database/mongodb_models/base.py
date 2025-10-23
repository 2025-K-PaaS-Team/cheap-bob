from beanie import Document as BeanieDocument
from datetime import datetime, timedelta, timezone
from pydantic import Field, field_validator
from typing import Optional


class Document(BeanieDocument):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('*', mode='before')
    @classmethod
    def ensure_timezone_aware(cls, v):
        """Ensure all datetime fields are timezone-aware (UTC)"""
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
    
    class Settings:
        use_cache = True
        cache_expiration_time = timedelta(seconds=10)
        validate_on_save = True
        timezone_aware = True
        
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }