from config.db import redis_client
from fastapi import UploadFile, HTTPException
from redis.exceptions import ConnectionError as RedisConnectionError
from utils.twitter_utils import ChunkedUpload
from utils.exceptions import redis_connection_exception
from utils.common import fetch_oauth_from_redis
import logging
import requests

logger = logging.getLogger()

async def get_media_id(user_id: int, media: UploadFile):
    """Upload media to X and return media ID valid for 24h"""
    try:
        oauth_token = await fetch_oauth_from_redis(f"{user_id}:oauth")
    except RedisConnectionError:
        raise redis_connection_exception
    
    mediaTweet = ChunkedUpload(oauth_token, media)
    
    await mediaTweet.upload_init()
    await mediaTweet.upload_append()
    media_id_response = await mediaTweet.upload_finalize()
    print(media_id_response)

    return media_id_response["data"].get("id")

async def upload_to_wasabi(url: str, file: UploadFile):
    """Upload file to wasabi using presigned url. Returns successful status code"""
    file_bytes = await file.read()
    req = requests.put(url=url, data=file_bytes)
    if req.status_code < 200 or req.status_code > 299:
        raise HTTPException(
                status_code=req.status_code,
                detail="Failed to upload to wasabi storage."
                    )
    else:
        logger.info("Upload to wasabi storage complete.")
        return
    