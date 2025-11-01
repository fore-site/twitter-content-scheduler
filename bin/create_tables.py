# APPEND ROOT DIRECTORY TO SYS PATH TO ALLOW FILE IMPORTS
from os import path
import sys
sys.path.append(path.dirname(path.dirname(__file__)))

from config.db import db_pool, asyncio
import aiofiles

## CREATE TABLES IN DATABASE 
async def main():
    async with db_pool:
        async with db_pool.connection() as conn:
            async with aiofiles.open('./init_db.sql', 'r') as f:
                sql_script = await f.read()
            await conn.execute(sql_script)
            await conn.commit()

if __name__ == "__main__":
    asyncio.run(main())
