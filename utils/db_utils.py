from psycopg_pool import AsyncConnectionPool
from models.TypeModel import PostStatus, UserStatus

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
            
async def check_or_update_user_status(db_pool: AsyncConnectionPool, user_id: int):
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT user_status FROM users WHERE users.id = %(user_id)s
            """, {'user_id': user_id})
            status = await cur.fetchone()
        if status == UserStatus.DEACTIVATED:
            await cur.execute("""
            UPDATE users
            SET user_status = %s
            WHERE users.id = %s
            RETURNING user_status
            """, (UserStatus.ACTIVE.value, user_id))
            user_status = await cur.fetchone()
            return user_status[0]
        else:
            return status[0]
