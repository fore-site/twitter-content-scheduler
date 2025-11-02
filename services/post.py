from config import db
from fastapi import Depends
from models.PostModel import Post
from typing import Annotated
from utils.dependencies import CheckJwt

async def create_post(user_id: Annotated[int, Depends(CheckJwt)], post_body: Post):
    async with db.db_pool:
        async with db.db_pool.connection() as conn:
            async with conn.cursor() as cur:
                cur.execute("""
            INSERT INTO posts (content, post_img, scheduled_time, user_id)
            VALUES 
            (%s, %s, %s, %s)            
            """, (post_body.content, 
                post_body.post_img, 
                post_body.scheduled_time, 
                user_id))
        await conn.commit()