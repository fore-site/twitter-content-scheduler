from fastapi import HTTPException
from utils.common import update_oauth_token, fetch_oauth_from_redis, check_file_type
import pytest

@pytest.mark.anyio
async def test_fetch_oauth_from_redis():
    key = '123:oauth'
    oauth = await fetch_oauth_from_redis(key)
    assert oauth != None

@pytest.mark.anyio
async def test_fetch_oauth_from_redis_no_connection():
    key = '123:oauth'
    with pytest.raises(HTTPException):
        await fetch_oauth_from_redis(key)

@pytest.mark.anyio
async def test_fetch_oauth_from_redis_invalid_key():
    key = '123:oauth'
    with pytest.raises(ValueError):
        await fetch_oauth_from_redis(key)