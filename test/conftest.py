import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from config.db import db_pool, redis_client
from datetime import datetime
from fastapi import UploadFile
from httpx import AsyncClient, ASGITransport
from main import app
from pathlib import Path
from typing import AsyncGenerator
from utils.auth_utils import create_access_token, create_refresh_token
import json
import pytest_asyncio
import pytest

@pytest_asyncio.fixture(autouse=True, scope='session', loop_scope='session')
async def mock_user_and_post() -> AsyncGenerator:
    await redis_client.set('123:oauth', json.dumps({'access_token': 'xyz'}))
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

    await redis_client.delete('123:oauth')
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

@pytest.fixture(scope='session')
def mock_uploadfile():
    path = Path('C:/Users/Oguns/Figure_2.png')
    with open(path, 'rb') as file:
        content = file.read()
    uploadfile_obj = UploadFile(file=content, filename='figure_2.png')
    yield uploadfile_obj

@pytest.fixture(scope='module')
def default_access_token():
    access_token = create_access_token({"sub": 123})
    yield access_token

@pytest.fixture(scope='module')
def default_refresh_token():
    refresh_token = create_refresh_token({"sub": 123})
    yield refresh_token


@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def async_client() -> AsyncGenerator:
    async with AsyncClient(base_url='http://127.0.0.1:5000', 
                           transport=ASGITransport(app=app)) as ac:
        yield ac