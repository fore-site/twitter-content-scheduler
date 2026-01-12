import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import pytest_asyncio
from fastapi import UploadFile
from pathlib import Path
from config.db import db_pool
from datetime import datetime

@pytest_asyncio.fixture(autouse=True, scope='session', loop_scope='session')
async def mock_user_and_post():
    await db_pool.open()
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            INSERT INTO users (id, username, display_name, is_premium)
            VALUES
            (%s, %s, %s, %s)
            """, (123, 'fore', 'gump', True))
            await cur.execute("""
            INSERT INTO posts
            (text, media, scheduled_time, user_id)
            VALUES
            (%s, %s, %s, %s)
            RETURNING id            
            """, ('Test data', [], datetime.now(), 123))
            result = await cur.fetchone()
            post_id = result[0]
    yield post_id

    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                DELETE FROM users
                WHERE id = %(user_id)s
            """, {"user_id": 123})
            await cur.execute("""
            DELETE FROM posts 
            WHERE id = %(post_id)s
        """, {"post_id": post_id})
    await db_pool.close()

@pytest_asyncio.fixture(loop_scope='session', scope='session')
async def mock_uploadfile():
    path = Path('C:/Users/Oguns/Figure_2.png')
    with open(path, 'rb') as file:
        content = file.read()
    uploadfile_obj = UploadFile(file=content, filename='figure_2.png')
    yield uploadfile_obj