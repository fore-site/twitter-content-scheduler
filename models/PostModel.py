from datetime import datetime
from pydantic import BaseModel, field_validator, ValidationInfo
from config.db import db_pool
from models.TypeModel import PostStatus

class Post(BaseModel):
    """Table posts. Model for input posts."""
    id: int
    user_id: int
    content: str
    post_img: str | None = None
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
        """, {'user_id': info.data["user_id"]})
            result = await cur.fetchone()
        is_premium, = result

        if is_premium is None and len(content) > 280:
            raise ValueError("Maximum character limit for non-premium users is 250")
        elif is_premium and len(content) > 25000:
            raise ValueError("Maximum character count for premium exceeded.")
        return content
    
class PostOut(Post):
    """Table Posts. Model for output posts"""
    created_at: datetime
    post_status: PostStatus