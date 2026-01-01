from fastapi import HTTPException
from utils.common import update_oauth_token, fetch_oauth_from_redis, check_file_type
import json
import pytest
import pytest_asyncio
from config.db import redis_client

@pytest_asyncio.fixture(autouse=True, loop_scope='session', scope='module')
async def mock_redis_oauth():
    await redis_client.set('123:oauth', json.dumps({"access_token": 'nalfo', "refresh_token": 'ahfdfn'}), ex=300)

class TestTokens:

    @pytest.mark.asyncio(loop_scope='session')
    async def test_fetch_oauth_from_redis(self):
        key = '123:oauth'
        oauth = await fetch_oauth_from_redis(key)
        assert oauth != None

    # @pytest.mark.asyncio(loop_scope='session')
    # async def test_fetch_oauth_from_redis_no_connection(self):
    #     key = '123:oauth'
    #     with pytest.raises(HTTPException):
    #         await fetch_oauth_from_redis(key)

    @pytest.mark.asyncio(loop_scope='session')
    async def test_fetch_oauth_from_redis_invalid_key(self):
        key = '1234:oauth'
        with pytest.raises(ValueError):
            await fetch_oauth_from_redis(key)

class TestCheckFileType:
    async def test_check_file_type(self):
        pass