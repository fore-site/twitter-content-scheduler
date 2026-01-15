from config import db
from object_storage.wasabi_service import wasabi_file_handling
from fastapi import Depends, Form, HTTPException, status
from models.PostModel import BasePost, PostOut, UpdatePost
from models.TypeModel import PostStatus
from psycopg.rows import dict_row
from scheduler.job import add_job_to_scheduler, modify_job_in_scheduler
from typing import Annotated
from utils.dependencies import CheckJwt
from utils.common import check_character_limit
import logging
import math

logger = logging.getLogger()

async def get_all_posts(user_id: Annotated[int, Depends(CheckJwt())], page: int = 1, page_size: int = 10):
    """Logic to fetch all scheduled tweets from database."""
    if page_size > 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Page size cannot exceed 10.")
    
    offset = (page_size * page) - page_size
    async with db.db_pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("""
                SELECT * FROM posts
                WHERE posts.user_id = %(user_id)s
                OFFSET %(offset)s
                LIMIT %(limit)s
                """,{"user_id": user_id,
                     "limit": page_size,
                     "offset": offset})
            result = await cur.fetchall()
            if not result:
                return []
            else:
                return {"data": result,
                        "pagination": {
                            "current_page": page,
                            "total_pages": math.ceil(len(result)/page_size),
                            "total_records": len(result),
                            "per_page": page_size,
                            "next_page": f'/v1/posts?page={page + 1}&page_size={page_size}'
                        }}

async def get_post(post_id: int, user_id: Annotated[int, Depends(CheckJwt())]):
    """Logic to fetch tweet and media from database"""
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
    if not result:
        return []
    post = PostOut(**result)
    return post

async def create_post(user_id: Annotated[int, Depends(CheckJwt())], 
                      post_body: Annotated[BasePost, Form(media_type="multipart/form-data")]):
    """Logic to create tweet and attach media."""
    media_list = []

    if post_body.text:
        try:
            await check_character_limit(post_body.text, user_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail=str(e))  

    if post_body.files:
        media_dict = await wasabi_file_handling(user_id, post_body)
        media_list = media_dict.get('media_list')

    # ADD TWEET TO DATABASE
    async with db.db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            INSERT INTO posts (text, media, scheduled_time, user_id)
            VALUES 
            (%s, %s, %s, %s)
            RETURNING id          
            """, (post_body.text, 
                media_list, 
                post_body.scheduled_time, 
                user_id))
            result = await cur.fetchone()
            post_id = result[0]

    # DELETE files ATTRIBUTE FROM POST_BODY OBJECT
    delattr(post_body, 'files')

    await add_job_to_scheduler(user_id, post_id, post_body)

    return post_body

async def update_post(post_id: int, user_id: Annotated[int, Depends(CheckJwt())], 
                      post_body: Annotated[UpdatePost, Form(media_type="multipart/form-data")]):
    if post_body.text:
        try:
            await check_character_limit(post_body.text, user_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail=str(e))

    if post_body.files:
        media_dict = await wasabi_file_handling(user_id, post_body, post_body.media)
        post_body.media = media_dict.get('media_list')

    async with db.db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""SELECT id FROM posts WHERE id = %(post_id)s""",
                              {"post_id": post_id})
            
            result = await cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found.")
            
            await cur.execute("""
            UPDATE posts
            SET text = %(text)s,
                media = %(media)s,
                scheduled_time = %(scheduled_time)s
            WHERE posts.user_id = %(user_id)s AND
                    posts.id = %(post_id)s AND
                    posts.post_status = %(post_status)s
    """, {"text": post_body.text, 
          "media": post_body.media, 
          "scheduled_time": post_body.scheduled_time,
          "user_id": user_id,
          "post_id": post_id,
          "post_status": PostStatus.pending.value})
            affected_row = cur.rowcount
            if not affected_row:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Can only update a post of 'pending' status.")
    
    # DELETE files ATTRIBUTE FROM POST_BODY OBJECT
    delattr(post_body, 'files')

    # await modify_job_in_scheduler(user_id, post_id, post_body)

    return post_body

async def delete_post(post_id: int, user_id: Annotated[int, Depends(CheckJwt())]) -> None:
    async with db.db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
        DELETE FROM posts
        WHERE id = %s AND user_id = %s
        """,  (post_id, user_id))
            affected_row = cur.rowcount
            if affected_row == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Post does not exist.")
    return None