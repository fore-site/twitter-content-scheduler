import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pytest
import pytest_asyncio
from config.db import db_pool
from datetime import datetime
from utils.db_utils import update_post_status_in_db
from pydantic_core import ValidationError

@pytest_asyncio.fixture(autouse=True, scope='module', loop_scope='session')
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

            
@pytest.mark.asyncio(loop_scope='session')
async def test_update_post_status_in_db(mock_user_and_post):
    status = 'sent'
    await update_post_status_in_db(db_pool, mock_user_and_post, status)
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
SELECT post_status FROM posts WHERE id = %(post_id)s""", {"post_id":mock_user_and_post})
            result = await cur.fetchone()
            assert status == result[0]

@pytest.mark.asyncio(loop_scope='session')
async def test_update_post_status_invalid_id(mock_user_and_post):
    status = 'ssent'
    with pytest.raises(ValidationError):
        await update_post_status_in_db(db_pool,mock_user_and_post, status)

