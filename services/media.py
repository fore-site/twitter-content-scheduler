from config.db import redis_client
from fastapi import Depends, UploadFile
from typing import Annotated
from utils.dependencies import CheckJwt
from utils.TwitterUtils import ChunkedUpload
import aiofiles

async def get_media_id(user_id: Annotated[int, Depends(CheckJwt)], media: UploadFile) -> dict:
    oauth_token = redis_client.get(f"{user_id}:oauth")
    mediaTweet = ChunkedUpload(oauth_token, media)
    # async with aiofiles.open('new_figure.png', 'wb') as new_file:
    #     file = await media.read()
    #     await new_file.write(file)
    # print(file)
    # return {"file": "opened"}
    media_id = await mediaTweet.upload_init()
    return media_id