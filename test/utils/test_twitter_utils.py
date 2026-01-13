from utils.twitter_utils import fetch_user, send_scheduled_tweet, ChunkedUpload
from fastapi import HTTPException
from models.PostModel import BasePost, UpdatePost
from redis.exceptions import ConnectionError as RedisConnectionError
import pytest
import requests
import uuid

# @pytest.mark.asyncio(loop_scope='session')
# async def test_fetch_user_from_x():
#     oauth_token = {"access_token": str(uuid.uuid4()), "refresh_token": str(uuid.uuid4())}
#     user = await fetch_user(oauth_token)
#     assert user["data"].get('username') == 'fore_site'

@pytest.mark.asyncio(loop_scope='session')
async def test_fetch_user_from_x_with_exception():
    oauth_token = {"access_token": str(uuid.uuid4()), "refresh_token": str(uuid.uuid4())}
    with pytest.raises(HTTPException):
        await fetch_user(oauth_token)

# @pytest.mark.asyncio(loop_scope='session')
# async def test_send_scheduled_tweet(mock_user_and_post):
#     oauth_token = {"access_token": str(uuid.uuid4()), "refresh_token": str(uuid.uuid4())}
#     tweet_body = BasePost(text="Hello there, from test session", hours=1)
#     assert await send_scheduled_tweet(mock_user_and_post, oauth_token, tweet_body) == None

@pytest.mark.asyncio(loop_scope='session')
async def test_send_scheduled_tweet_with_redis_exception(mock_user_and_post):
    oauth_token = {"access_token": str(uuid.uuid4()), "refresh_token": str(uuid.uuid4())}
    tweet_body = BasePost(text="Hello there from test session", hours=1)
    with pytest.raises(RedisConnectionError):
        await send_scheduled_tweet(mock_user_and_post, oauth_token, tweet_body)

@pytest.mark.asyncio(loop_scope='session')
async def test_send_scheduled_tweet_with_http_exception(mock_user_and_post):
    oauth_token = {"access_token": str(uuid.uuid4()), "refresh_token": str(uuid.uuid4())}
    tweet_body = BasePost(text="Hello there from test session", hours=1)
    with pytest.raises(HTTPException):
        await send_scheduled_tweet(mock_user_and_post, oauth_token, tweet_body)

class TestChunkedUpload:

    @pytest.mark.asyncio(loop_scope='session')
    async def test_init_chunked_upload(self, mock_uploadfile):
        oauth_token = {"access_token": str(uuid.uuid4()), "refresh_token": str(uuid.uuid4())}
        upload_file = ChunkedUpload(oauth_token, mock_uploadfile)
        assert await upload_file.upload_init() == None

    @pytest.mark.asyncio(loop_scope='session')
    async def test_init_chunked_upload_with_exception(self, mock_uploadfile):
        oauth_token = {"access_token": str(uuid.uuid4()), "refresh_token": str(uuid.uuid4())}
        upload_file = ChunkedUpload(oauth_token, mock_uploadfile)
        with pytest.raises(HTTPException):
            await upload_file.upload_init()

    