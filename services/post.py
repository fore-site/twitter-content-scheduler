from config import db
from fastapi import Depends, HTTPException, status
from models.PostModel import BasePost
from models.TypeModel import PostStatus
from typing import Annotated
from utils.dependencies import CheckJwt
from utils.otherUtils import check_character_limit

async def create_post(user_id: Annotated[int, Depends(CheckJwt())], post_body: BasePost):
    try:
        check_limit = await check_character_limit(post_body.content, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail=e)
    else:
        async with db.db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
            INSERT INTO posts (content, post_img, scheduled_time, user_id)
            VALUES 
            (%s, %s, %s, %s)            
            """, (post_body.content, 
                post_body.post_img, 
                post_body.scheduled_time, 
                user_id))
    return post_body

async def update_post(post_id: int, user_id: Annotated[int, Depends(CheckJwt())], post_body: BasePost):
    try:
        check_limit = check_character_limit(post_body.content, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail=e)
    else:
        async with db.db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
            UPDATE posts
            SET content = %(content)s,
                post_img = %(post_img)s,
                scheduled_time = %(scheduled_time)s
            WHERE posts.user_id = %(user_id)s AND
                    posts.id = %(post_id)s AND
                    posts.post_status <> %(post_status)s
    """, {"content": post_body.content, 
          "post_img": post_body.post_img, 
          "scheduled_time": post_body.scheduled_time,
          "user_id": user_id,
          "id": post_id,
          "post_status": PostStatus.sent})
        return post_body