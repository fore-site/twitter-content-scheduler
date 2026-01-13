import pytest
from config.db import db_pool
from utils.db_utils import update_post_status_in_db, check_or_update_user_status
from models.TypeModel import UserStatus
            
@pytest.mark.asyncio(loop_scope='session')
async def test_update_post_status_in_db(mock_user_and_post):
    status = 'sent'
    await update_post_status_in_db(db_pool, mock_user_and_post, status)
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            SELECT post_status FROM posts WHERE id = %(post_id)s""", 
            {"post_id": mock_user_and_post})
            result = await cur.fetchone()
            assert status == result[0]

@pytest.mark.asyncio(loop_scope='session')
async def test_update_post_status_invalid_id(mock_user_and_post):
    status = 'ssent'
    with pytest.raises(ValueError):
        await update_post_status_in_db(db_pool, mock_user_and_post, status)

@pytest.mark.asyncio(loop_scope='session')
async def test_check_or_update_userStatus():
    user_status = await check_or_update_user_status(db_pool, 1234)
    assert user_status == UserStatus.DISABLED