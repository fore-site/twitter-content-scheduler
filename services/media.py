from config.db import redis_client
from fastapi import UploadFile
from redis.exceptions import ConnectionError as RedisConnectionError
from utils.twitter_utils import ChunkedUpload
from utils.exceptions import redis_connection_exception

async def get_media_id(user_id: int, media: UploadFile) -> dict:
    """Upload media to X and return media ID valid for 24h"""
    try:
        oauth_token = redis_client.get(f"{user_id}:oauth")
    except RedisConnectionError:
        raise redis_connection_exception
    
    mediaTweet = ChunkedUpload(oauth_token, media)
    
    await mediaTweet.upload_init()
    await mediaTweet.upload_append()
    media_id_response = await mediaTweet.upload_finalize()

    return media_id_response["data"].get("id")
