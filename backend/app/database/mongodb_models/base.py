from beanie import Document as BeanieDocument
from datetime import datetime, timedelta, timezone
from pydantic import Field


class Document(BeanieDocument):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        use_cache = True
        cache_expiration_time = timedelta(seconds=10)
        validate_on_save = True
        
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }