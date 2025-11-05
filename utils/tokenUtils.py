from config.db import redis_client
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
