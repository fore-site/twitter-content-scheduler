from config.db import redis_client, db_pool
from starlette_context import context
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

        await redis_client.set(key, serialized_token)
    else:
        logger.error("Unable to save oauth token in redis. No refresh or access token")
        return

async def fetch_oauth_from_redis(key):
    token = await redis_client.get(key)
    deserialized_token = json.loads(token)
    return deserialized_token

async def check_character_limit(content: str, user_id: int) -> bool:
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
    return True

def check_file_type(filename, media_category=False) -> str:
    img_extensions = ["png", "gif", "bmp", "webp", "jpeg", "pjpeg", "tiff"]
    vid_extensions = ["mp4", "webm", "mp2t", "quicktime"]
    type_error = ValueError("Unsupported media type.")

    find_match = re.search(r'\.[^.]+$', filename)
    match = find_match.group()

    if media_category:
        if match[1:] == "gif":
            return "gif"
        elif match[1:] in img_extensions:
            return "image"
        elif match[1:] in vid_extensions:
            return "video"
        else: 
            raise type_error

    if match[1:] in img_extensions:
        return f"image/{match[1:]}"
    elif match[1:] in vid_extensions:
        return f"video/{match[1:]}"
    else:
        raise type_error