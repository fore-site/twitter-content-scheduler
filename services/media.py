from config.db import redis_client
from fastapi import Depends, UploadFile
from typing import Annotated
from utils.dependencies import CheckJwt
from utils.AuthUtils import twitter_client
from utils.TwitterUtils import ChunkedUpload
import re

async def get_media_id(media: UploadFile):
    # oauth_token = redis_client.get(f"{user_id}:oauth")
    # ChunkedUpload(oauth_token, media)
    match = re.search("\.[^.]+$", media.filename)
    return {"file_ext": match.group()[1:]}