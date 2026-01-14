from datetime import datetime, timedelta, timezone
from fastapi import UploadFile
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from models.TypeModel import PostStatus
from typing import List

class BasePost(BaseModel):
    """Table posts. Model for creating posts."""
    text: str | None = None
    days: int = 0
    hours: int  = 0
    minutes: int = 0
    files: List[UploadFile] | None = Field(None, validate_default=True)
    scheduled_time: datetime = Field(datetime.now(), validate_default=True)
    
    @field_validator("scheduled_time", mode="before")
    @classmethod
    def get_scheduled_time(cls, scheduled_time: datetime, info: ValidationInfo) -> datetime:
        day = info.data.get("days")
        minute = info.data.get("minutes")
        hour = info.data.get("hours")

        scheduled_time = timedelta(days=day, minutes=minute, hours=hour) + datetime.now(tz=timezone.utc)
        return scheduled_time
    
    @field_validator("files", mode='after')
    @classmethod
    def check_empty_text_and_fileUpload(cls, files: List[str] | None, info: ValidationInfo) -> List[str] | None:
        text = info.data.get('text')
        if not text and not files:
            raise ValueError("Both text and file upload cannot be empty at the same time")
        return files

class UpdatePost(BasePost):
    """Table Posts. Model for updating posts."""
    media: List[str] = Field(default=list())

class PostOut(BaseModel):
    """Table Posts. Model for output posts"""
    id: int
    user_id: int
    text: str | None = None
    media: List[str]
    scheduled_time: datetime
    created_at: datetime
    post_status: PostStatus