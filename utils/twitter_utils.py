from config.settings import MEDIA_UPLOAD_ENDPOINT
from fastapi import HTTPException, status, UploadFile
from utils.auth_utils import twitter_client
from utils.common import check_file_type
from utils.exceptions import twitter_timeout_exception, twitter_bad_gateway_exception
import httpx
import logging
import time

logger = logging.getLogger()

async def fetch_user(token: str | None = None):
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

    def __init__(self, token: str, file: UploadFile):
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
                "command": "INIT",
                "media_type": check_file_type(self.file),
                "total_bytes": self.total_bytes,
                "media_category": check_file_type(self.file, media_category=True)
            }
            req = await twitter_client.post(url=MEDIA_UPLOAD_ENDPOINT, data=request_data)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=str(e))
        except httpx.ConnectTimeout:
            raise twitter_timeout_exception
        except httpx.ConnectError:
            raise twitter_bad_gateway_exception
        else:
            self.media_id = req.json()['media_id']
            logger.info(f"Media ID: {self.media_id}")
            
    async def upload_append(self):
        """Uploads media in chunks and appends to chunks"""
        segment_id = 0
        bytes_sent = 0

        while bytes_sent < self.total_bytes:
            chunk = await self.file.read(4*1024*1024)
            logger.info("Append..")
            request_data = {
                'command': 'APPEND',
                'media_id': self.media_id,
                'segment_index': segment_id
            }
            files = {
                'media': chunk
            }
            try:
                req = await twitter_client.post(url=MEDIA_UPLOAD_ENDPOINT, data=request_data, files=files)
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
                segment_id += 1
                bytes_sent = self.file.file.tell()
                logger.info(f"{bytes_sent} of {self.total_bytes} uploaded...")
        logger.info("Upload chunks complete")
    
    async def upload_finalize(self):
        """Finalizes uploads and starts video processing."""
        logger.info("Finalize..")

        request_data = {
            'command': 'FINALIZE',
            'media_id': self.media_id
        }
        try:
            req = await twitter_client.post(url=MEDIA_UPLOAD_ENDPOINT, data=request_data)
        except httpx.ConnectTimeout:
            raise twitter_timeout_exception
        except httpx.ConnectError:
                raise twitter_bad_gateway_exception
        else:
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