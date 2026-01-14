import uuid
from config.db import redis_client
from models.PostModel import BasePost, UpdatePost
from redis.exceptions import ConnectionError as RedisConnectionError
from scheduler.settings import scheduler
from utils.common import fetch_oauth_from_redis
from utils.exceptions import redis_connection_exception
from utils.twitter_utils import send_scheduled_tweet
import logging

logger = logging.getLogger()

# ADD JOB TO SCHEDULER
async def add_job_to_scheduler(user_id: int, post_id: int, post_body: BasePost) -> None:
    job_id = str(uuid.uuid4())
    token = await fetch_oauth_from_redis(f"{user_id}:oauth")
    scheduler.add_job(send_scheduled_tweet,
                            'date',
                            run_date=post_body.scheduled_time,
                            args=[post_id, token, post_body],
                            id=job_id,
                            jobstore='postgres',
                            misfire_grace_time=None)
    
    # SAVE JOB ID TO REDIS FOR FUTURE MODIFICATION
    try:
        await redis_client.set(f'{post_id}:job_id', job_id)
    except RedisConnectionError:
        logger.warning(f"Job ID failed to save to redis, {redis_connection_exception}")


# MODIFY JOB IN SCHEDULER
async def modify_job_in_scheduler(user_id: int, post_id: int, post_body: UpdatePost) -> None:
    job_id = await redis_client.get(f"{post_id}:job_id")
    token = await fetch_oauth_from_redis(f"{user_id}:oauth")
    scheduler.modify_job(job_id=job_id, 
                        jobstore='postgres', 
                        func=send_scheduled_tweet,
                        trigger='date',
                        run_date=post_body.scheduled_time,
                        args=[post_id, token, post_body])
    