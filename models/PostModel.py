from datetime import datetime, timedelta
from pydantic import BaseModel, field_validator, ValidationInfo
from config.db import db_pool
from models.TypeModel import PostStatus
from starlette_context import context

class BasePost(BaseModel):
    """Table posts. Model for creating and updating posts."""
    content: str
    post_img: str | None = None
    days: int = 0
    hours: int = 0
    minutes: int = 0
    scheduled_time: datetime

    @field_validator('content', mode='after')
    @classmethod
    async def check_character_limit(cls, content: str, info: ValidationInfo) -> str:
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
            SELECT 
                is_premium
            FROM
                users
            WHERE
                id = %(user_id)s                     
        """, {'user_id': int(context.get("user_id"))})
            result = await cur.fetchone()
        is_premium, = result

        if is_premium is None and len(content) > 280:
            raise ValueError("Maximum character limit for non-premium users is 250")
        elif is_premium and len(content) > 25000:
            raise ValueError("Maximum character count for premium exceeded.")
        return content
    
    @field_validator("scheduled_time", mode="after")
    @classmethod
    async def get_scheduled_time(cls, scheduled_time: datetime, info: ValidationInfo) -> datetime:
        day = info.data.get("days")
        minute = info.data.get("minutes")
        hour = info.data.get("hours")

        scheduled_time = timedelta(day=day, minute=minute, hour=hour) + datetime.now()
        return scheduled_time

class PostOut(BasePost):
    """Table Posts. Model for output posts"""
    id: int
    user_id: int
    content: str
    post_img: str | None = None
    scheduled_time: datetime
    created_at: datetime
    post_status: PostStatus