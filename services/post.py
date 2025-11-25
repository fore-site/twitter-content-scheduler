from config import db
from config.wasabi import WasabiClient
from fastapi import Depends, HTTPException, status, UploadFile
from models.PostModel import BasePost, PostOut, UpdatePost
from models.TypeModel import PostStatus
from psycopg.rows import dict_row
from services.media import get_media_id, upload_to_wasabi
from typing import Annotated
from utils.dependencies import CheckJwt
from utils.common import check_character_limit
import logging

logger = logging.getLogger()

async def get_post(post_id: int, user_id: Annotated[int, Depends(CheckJwt())]):
    """Logic to fetch tweet and media from database"""
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

async def create_post(user_id: Annotated[int, Depends(CheckJwt())], post_body: BasePost, file: UploadFile | None = None):
    """Logic to create tweet and attach media."""
    media_list = []

    if post_body.text:
        try:
            await check_character_limit(post_body.text, user_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail=str(e))  

    if file:
        s3 = WasabiClient()
        media_id = await get_media_id(user_id=user_id, media=file)
        logger.info(f"Upload to Twitter/X complete, Media ID: {media_id}")

        # GENERATE URL FOR UPLOAD AND UPLOAD FILE TO WASABI STORAGE
        put_url = await s3.generate_presigned_url(key=file.filename)
        await upload_to_wasabi(url=put_url, file=file)
        
        # GENERATE URL FOR DOWNLOAD/READING FILE FROM WASABI AND APPEND TO LIST
        get_url = await s3.generate_presigned_url(key=file.filename, method='get')
        media_list.append(get_url)
    
    async with db.db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            INSERT INTO posts (text, media, scheduled_time, user_id)
            VALUES 
            (%s, %s, %s, %s)            
            """, (post_body.text, 
                media_list, 
                post_body.scheduled_time, 
                user_id))
    return post_body

async def update_post(post_id: int, user_id: Annotated[int, Depends(CheckJwt())], post_body: UpdatePost, file: UploadFile | None = None):
    if post_body.text:
        try:
            await check_character_limit(post_body.text, user_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail=str(e))

    if file:
        s3 = WasabiClient()
        media_id = await get_media_id(user_id=user_id, media=file)
        logger.info(f"Upload complete, Media ID: {media_id}")

        # GENERATE URL FOR UPLOAD AND UPLOAD FILE TO WASABI STORAGE
        put_url = await s3.generate_presigned_url(key=file.filename)
        await upload_to_wasabi(url=put_url, file=file)
        
        # GENERATE URL FOR DOWNLOAD/READING FILE FROM WASABI AND APPEND TO LIST
        get_url = await s3.generate_presigned_url(key=file.filename, method='get')
        post_body.media.append(get_url)

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