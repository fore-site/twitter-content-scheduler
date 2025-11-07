from config.db import redis_client, db_pool
from starlette_context import context
import json

async def update_oauth_token(token, refresh_token = None, access_token = None):    
    # SAVE TOKEN TO REDIS, THIS IS A TEMPORARY STORAGE
    if refresh_token:
        user_id = context.get("user_id")
        key = f"{user_id}:oauth"

        # SERIALIZE THE TOKEN TO AVOID REDIS DATATYPE ERROR
        serialized_token = json.dumps(token)

        await redis_client.set(key, serialized_token)
    else:
        print("Unable to save token in redis")
        return

async def fetch_oauth_from_redis(key):
    token = await redis_client.get(key)
    deserialized_token = json.loads(token)
    return deserialized_token

async def check_character_limit(content: str, user_id: int) -> None:
    async with db_pool:
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
            SELECT 
                is_premium
            FROM
                users
            WHERE
                id = %(user_id)s                     
        """, {'user_id': user_id})
                result = await cur.fetchone()
        is_premium, = result

        if is_premium is None and len(content) > 280:
            raise ValueError("Maximum character limit for non-premium users is 250")
        elif is_premium and len(content) > 25000:
            raise ValueError("Maximum character count for premium exceeded.")
        return