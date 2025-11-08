# APPEND ROOT DIRECTORY TO SYS PATH TO ALLOW FILE IMPORTS
from psycopg_pool import AsyncConnectionPool
from os import path
import sys
sys.path.append(path.dirname(path.dirname(__file__)))

import asyncio
import platform
from config.settings import DB_URI, REDIS_URI
import aiofiles

# MAKE ASYNCIO COMPATIBLE WITH PSYCOPG
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

## CREATE TABLES IN DATABASE 
async def main():
    pool = AsyncConnectionPool(conninfo=DB_URI, open=False)
    await pool.open()
    async with pool.connection() as conn:
        async with aiofiles.open('./init_db.sql', 'r') as f:
            sql_script = await f.read()
        await conn.execute(sql_script)
    await pool.close()

import redis
r = redis.from_url(REDIS_URI)
r.flushdb()

if __name__ == "__main__":
    asyncio.run(main())
