from utils.twitter_utils import fetch_user, send_scheduled_tweet, ChunkedUpload
import pytest
import pytest_asyncio
import requests
import uuid

@pytest.mark.asyncio(loop_scope='session')
async def test_fetch_user_from_x():
    oauth_token = {"access_token": str(uuid.uuid4()), "refresh_token": str(uuid.uuid4())}
    user = await fetch_user(oauth_token)
    assert user["data"].get('username') == 'fore_site'