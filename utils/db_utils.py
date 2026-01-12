from psycopg_pool import AsyncConnectionPool
from models.TypeModel import PostStatus

async def update_post_status_in_db(db_pool: AsyncConnectionPool, post_id: int, post_status: PostStatus):
    if post_status not in PostStatus:
        raise ValueError("Invalid input value for post status. Status must be 'sent', 'failed' or 'pending'")
    
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """UPDATE posts 
                SET post_status = %(post_status)s 
                WHERE posts.id = %(post_id)s""", 
                {"post_status": post_status, "post_id": post_id})