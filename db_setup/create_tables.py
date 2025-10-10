from db import db_pool
import asyncio

## CREATE TABLES IN DATABASE 
async def main():
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            async with open('../init_db.sql', 'r') as f:
                sql_script = await f.read()
            await cur.execute(sql_script)
            await conn.commit()

if __name__ == "__main__":
    asyncio.run(main)