from config import db
from fastapi import Depends, HTTPException, status
from models.PostModel import BasePost, PostOut
from models.TypeModel import PostStatus
from psycopg.rows import dict_row
from typing import Annotated
from utils.dependencies import CheckJwt
from utils.common import check_character_limit

async def get_post(post_id: int, user_id: Annotated[int, Depends(CheckJwt())]):
    async with db.db_pool:
        async with db.db_pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute("""
                SELECT * 
                FROM posts
                WHERE posts.id = %(post_id)s AND
                    posts.user_id = %(user_id)s
            """, {"post_id": post_id, 
                  "user_id": user_id})
                result = await cur.fetchone()
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Server could not find post created by current user.")
    post = PostOut(**result)
    return post

async def create_post(user_id: Annotated[int, Depends(CheckJwt())], post_body: BasePost):
    try:
        check_limit = await check_character_limit(post_body.content, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail=str(e))
    else:
        async with db.db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
            INSERT INTO posts (text, media, scheduled_time, user_id)
            VALUES 
            (%s, %s, %s, %s)            
            """, (post_body.text, 
                post_body.media, 
                post_body.scheduled_time, 
                user_id))
        return post_body

async def update_post(post_id: int, user_id: Annotated[int, Depends(CheckJwt())], post_body: BasePost):
    try:
        check_limit = await check_character_limit(post_body.content, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail=str(e))
    else:
        async with db.db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
            UPDATE posts
            SET text = %(text)s,
                media = %(media)s,
                scheduled_time = %(scheduled_time)s
            WHERE posts.user_id = %(user_id)s AND
                    posts.id = %(post_id)s AND
                    posts.post_status <> %(post_status)s
            RETURNING id
    """, {"text": post_body.text, 
          "media": post_body.media, 
          "scheduled_time": post_body.scheduled_time,
          "user_id": user_id,
          "post_id": post_id,
          "post_status": PostStatus.sent})
                result = await cur.fetchone()
            if result is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                    detail="Cannot update an already sent post.")
    return post_body