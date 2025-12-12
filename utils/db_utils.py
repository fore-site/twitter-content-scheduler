from psycopg_pool import AsyncConnectionPool

async def update_post_status_in_db(db_pool: AsyncConnectionPool, post_id: int, post_status: str):
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            cur.execute(
                """UPDATE posts 
                SET post_status = %(post_status)s 
                WHERE posts.id = %(post_id)s""", 
                {"post_status": post_status, "post_id": post_id})