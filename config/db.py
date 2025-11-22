from psycopg_pool import AsyncConnectionPool
from config.settings import DB_URI, REDIS_URI

import asyncio
import platform

# MAKE ASYNCIO COMPATIBLE WITH PSYCOPG
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

db_pool = AsyncConnectionPool(conninfo=DB_URI, open=False)

import redis.asyncio as aioredis

redis_client = aioredis.from_url(REDIS_URI)
