from fastapi import UploadFile
from pathlib import Path
from utils.common import fetch_oauth_from_redis, check_file_type
import json
import pytest
import pytest_asyncio
from config.db import redis_client

@pytest_asyncio.fixture(autouse=True, loop_scope='session', scope='module')
async def mock_redis_oauth():
    await redis_client.set('123:oauth', json.dumps({"access_token": 'nalfo', "refresh_token": 'ahfdfn'}), ex=300)

@pytest_asyncio.fixture(loop_scope='module', scope='module')
async def mock_uploadfile():
    path = Path('C:/Users/Oguns/Figure_2.png')
    with open(path, 'rb') as file:
        content = file.read()
    uploadfile_obj = UploadFile(file=content, filename='figure_2.png')
    yield uploadfile_obj

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
    @pytest.mark.asyncio(loop_scope='module')
    async def test_check_file_type(self, mock_uploadfile):
        img_extensions = ["image/png", "image/gif", "image/bmp", "image/webp", "image/jpeg", "image/pjpeg", "image/tiff"]
        vid_extensions = ["video/mp4", "video/webm", "video/mp2t", "video/quicktime"]
        assert check_file_type(mock_uploadfile) in img_extensions or check_file_type(mock_uploadfile) in vid_extensions

    # @pytest.mark.asyncio(loop_scope='module')
    # async def test_check_unsupported_file_type(self, mock_uploadfile):
    #     with pytest.raises(ValueError):
    #         await check_file_type(mock_uploadfile)

    @pytest.mark.asyncio(loop_scope='module')
    async def test_check_media_category(self, mock_uploadfile):
        categories = ["tweet_gif", "tweet_image", "tweet_video"]
        assert check_file_type(mock_uploadfile, media_category=True) in categories