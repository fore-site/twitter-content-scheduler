from config.db import redis_client
from fastapi import Depends, UploadFile
from typing import Annotated
from utils.dependencies import CheckJwt
from utils.TwitterUtils import ChunkedUpload

async def get_media_id(user_id: Annotated[int, Depends(CheckJwt)], media: UploadFile) -> dict:
    oauth_token = redis_client.get(f"{user_id}:oauth")
    mediaTweet = ChunkedUpload(oauth_token, media)
    await mediaTweet.upload_init()
    await mediaTweet.upload_append()
    media_id_response = await mediaTweet.upload_finalize()
    return media_id_response