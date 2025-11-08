from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from models.TypeModel import PostStatus

class BasePost(BaseModel):
    """Table posts. Model for creating and updating posts."""
    content: str | None = None
    post_img: str | None = None
    days: int = 0
    hours: int  = 0
    minutes: int = 0
    scheduled_time: datetime = Field(datetime.now(), validate_default=True)
    
    @field_validator("scheduled_time", mode="before")
    @classmethod
    def get_scheduled_time(cls, scheduled_time: datetime, info: ValidationInfo) -> datetime:
        day = info.data.get("days")
        minute = info.data.get("minutes")
        hour = info.data.get("hours")

        scheduled_time = timedelta(days=day, minutes=minute, hours=hour) + datetime.now()
        return scheduled_time

class PostOut(BaseModel):
    """Table Posts. Model for output posts"""
    id: int
    user_id: int
    content: str
    post_img: str | None = None
    scheduled_time: datetime
    created_at: datetime
    post_status: PostStatus