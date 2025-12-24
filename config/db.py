from psycopg_pool import AsyncConnectionPool
from config.settings import DB_URI, REDIS_URI

db_pool = AsyncConnectionPool(conninfo=DB_URI, open=False)

import redis.asyncio as aioredis

redis_client = aioredis.from_url(REDIS_URI, decode_responses=True)
