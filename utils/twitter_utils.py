from config.settings import MEDIA_UPLOAD_ENDPOINT
from config.db import db_pool, redis_client
from utils.db_utils import update_post_status_in_db
from fastapi import HTTPException, status, UploadFile
from models.PostModel import BasePost, UpdatePost
from utils.auth_utils import twitter_client
from redis.exceptions import ConnectionError as RedisConnectionError
from utils.common import check_file_type
from utils.exceptions import twitter_timeout_exception, twitter_bad_gateway_exception, redis_connection_exception
import httpx
import logging
import time

logger = logging.getLogger()
file_logger = logging.getLogger('fileLogger')

async def fetch_user(token = None):
    """Get user details from Twitter/X"""
    if token:
        twitter_client.token = token
    try:
        async_current_user = await twitter_client.get(url="https://api.x.com/2/users/me?user.fields=id,username,name,profile_image_url,verified")
    except httpx.ConnectTimeout:
        raise twitter_timeout_exception
    except httpx.ConnectError:
        raise twitter_bad_gateway_exception
    else:
        current_user = async_current_user.json()
        return current_user
    
class ChunkedUpload(object):

    def __init__(self, token, file: UploadFile):
        """Defines media tweet properties """
        self.file = file
        self.total_bytes = file.size
        self.media_id = None
        self.processing_info = None
        twitter_client.token = token

    async def upload_init(self):
        """Initializes Upload. Returns media ID"""
        try:
            request_data = {
                "media_type": check_file_type(self.file),
                "total_bytes": self.total_bytes,
                "media_category": check_file_type(self.file, media_category=True)
            }
            req = await twitter_client.post(
                url=f"{MEDIA_UPLOAD_ENDPOINT}/initialize",
                json=request_data, 
                headers={'Content-Type': 'application/json'})
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=str(e))
        except httpx.ConnectTimeout:
            raise twitter_timeout_exception
        except httpx.ConnectError:
            raise twitter_bad_gateway_exception
        else:
            file_logger.info(f"Request res: {req.json()}")
            self.media_id = req.json()['data']['id']
            
    async def upload_append(self):
        """Uploads media in chunks and appends to chunks"""
        print(f"MEDIA ID: {self.media_id}")
        segment_id = 0
        bytes_sent = 0

        while bytes_sent < self.total_bytes:
            chunk = await self.file.read(4*1024*1024)
            logger.info("Append..")
            request_data = {
                'segment_index': segment_id,
                'media': chunk
            }
            try:
                req = await twitter_client.post(
                    url=f"{MEDIA_UPLOAD_ENDPOINT}/{self.media_id}/append", 
                    json=request_data,
                    headers={"Content-Type": "application/json"})
            except httpx.ConnectTimeout:
                raise twitter_timeout_exception
            except httpx.ConnectError:
                raise twitter_bad_gateway_exception
            else:
                if req.status_code < 200 or req.status_code > 299:
                    file_logger.info(req.json())
                    raise HTTPException(
                        status_code=req.status_code,
                        detail=req.text
                    )
                segment_id += 1
                bytes_sent = self.file.file.tell()
                logger.info(f"{bytes_sent} of {self.total_bytes} uploaded...")
        logger.info("Upload chunks complete")
    
    async def upload_finalize(self):
        """Finalizes uploads and starts video processing."""
        logger.info("Finalize..")

        try:
            req = await twitter_client.post(
                url=f"{MEDIA_UPLOAD_ENDPOINT}/{self.media_id}/finalize")
        except httpx.ConnectTimeout:
            raise twitter_timeout_exception
        except httpx.ConnectError:
                raise twitter_bad_gateway_exception
        else:
            if req.status_code < 200 or req.status_code > 299:
                raise HTTPException(
                    status_code=req.status_code,
                    detail=req.text
                )
            self.processing_info = req.json().get("processing_info", None)
            res = await self.check_status()
            if res is None:
                return req.json()
            else:
                return res
    
    async def check_status(self):
        """Checks video processing status"""
        if self.processing_info is None:
            return
        state = self.processing_info["state"]

        logger.info(f"Media processing status: {state}")

        if state == u'succeeded':
            return
        elif state == u'failed':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Media upload failed."
            )
        else:
            check_after = self.processing_info["check_after_secs"]
            logging.info(f"Checking after {check_after} seconds")

            time.sleep(check_after)

            logging.info("Checking status again...")

            request_params = {
                'command': 'STATUS',
                'media_id': self.media_id
            }

            try:
                req = await twitter_client.get(url=MEDIA_UPLOAD_ENDPOINT, params=request_params)
            except httpx.ConnectTimeout:
                raise twitter_timeout_exception
            except httpx.ConnectError:
                raise twitter_bad_gateway_exception
            else:
                self.processing_info = req.json().get('processing_info', None)
                res = await self.check_status()
                if res is None:
                    return req.json()
                else:
                    return res
                
async def send_scheduled_tweet(post_id: int, token: dict, tweet_body: BasePost | UpdatePost, media_ids: list | None = None):
    twitter_client.token = token

    request_data = {
        "text": tweet_body.text
    }
    
    if media_ids:
        request_data.update({"media": {"media_ids": media_ids}})

    # REMOVE JOB ID FROM REDIS SINCE JOB WILL BE REMOVED FROM DATABASE UPON EXECUTION BY THE SCHEDULER
    try:
        await redis_client.delete(f"{post_id}:job_id")
        logger.info("Job ID removed from redis")
    except RedisConnectionError:
        logger.warning(f"Failed to remove job ID from redis, {redis_connection_exception}")
    
    # SEND TWEET
    try:
        req = await twitter_client.post(
            url="https://api.x.com/2/tweets",
            headers={"Content-Type": "application/json"},
            json=request_data
        )
    except httpx.ConnectTimeout:
        logging.error(f"{twitter_timeout_exception}, retrying after 10 seconds...")
        
        time.sleep(10)

        send_scheduled_tweet(post_id=post_id, token=token, tweet_body=tweet_body)
        # await update_post_status_in_db(db_pool, post_id, 'failed')
    except httpx.ConnectError:
        logging.error(f"{twitter_bad_gateway_exception}, retrying after 10 seconds...")
        
        time.sleep(10)

        send_scheduled_tweet(post_id=post_id, token=token, tweet_body=tweet_body)
        # await update_post_status_in_db(db_pool, post_id, 'failed')
    else:
        if req.status_code < 200 or req.status_code > 299:
            await update_post_status_in_db(db_pool, post_id, 'failed')
            raise HTTPException(
                status_code=req.status_code,
                detail=req. text
            )
        file_logger.info(f"Scheduled post successfully sent: {req.json()}")
        
        await update_post_status_in_db(db_pool, post_id, 'sent')