from config.db import redis_client, db_pool
from fastapi import UploadFile
from redis.exceptions import ConnectionError as RedisConnectionError
from starlette_context import context
from utils.exceptions import redis_connection_exception
import json
import re
import logging

logger = logging.getLogger('fileLogger')

async def update_oauth_token(token, refresh_token = None, access_token = None):
    """Callable that saves new oauth token to redis database."""    
    # SAVE TOKEN TO REDIS, THIS IS A TEMPORARY STORAGE
    if refresh_token or access_token:
        user_id = context.get("user_id")
        
        key = f"{user_id}:oauth"

        # SERIALIZE THE TOKEN TO AVOID REDIS DATATYPE ERROR
        serialized_token = json.dumps(token)
        try:
            await redis_client.set(key, serialized_token)
            logger.info(f"New oauth token saved to redis")
            logger.info(serialized_token)
        except RedisConnectionError:
            logger.exception("Failed to save new oauth token. Redis database connection cannot be established.")
    else:
        logger.error("Failed to save oauth token in redis. No refresh or access token")
        return

async def fetch_oauth_from_redis(key):
    """Fetch oauth token from redis database."""
    try:
        token = await redis_client.get(key)
        token = token.decode('utf-8')
    except RedisConnectionError:
        raise redis_connection_exception
    else:
        deserialized_token = json.loads(token)
    return deserialized_token

async def check_character_limit(content: str, user_id: int) -> bool:
    """Check character limit of input text based on user's X premium status"""
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            SELECT 
                is_premium
            FROM
                users
            WHERE
                id = %(user_id)s                     
        """, {"user_id": user_id})
            result = await cur.fetchone()
    is_premium, = result

    if not is_premium and len(content) > 280:
        raise ValueError("Maximum character limit for non-premium users is 250")
    elif is_premium and len(content) > 25000:
        raise ValueError("Maximum character count for premium exceeded.")
    return

def check_file_type(file: UploadFile, media_category=False) -> str:
    """Check and return file type or media category from file extension"""
    img_extensions = ["png", "gif", "bmp", "webp", "jpeg", "pjpeg", "tiff"]
    vid_extensions = ["mp4", "webm", "mp2t", "quicktime"]
    type_error = ValueError("Unsupported media type.")

    find_match = re.search(r'\.[^.]+$', file.filename)
    match = find_match.group()

    if media_category:
        if match[1:] == "gif":
            return "tweet_gif"
        elif match[1:] in img_extensions:
            return "tweet_image"
        elif match[1:] in vid_extensions:
            return "tweet_video"
        else: 
            raise type_error

    if match[1:] in img_extensions:
        return f"image/{match[1:]}"
    elif match[1:] in vid_extensions:
        return f"video/{match[1:]}"
    else:
        raise type_error