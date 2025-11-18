from config.settings import MEDIA_UPLOAD_ENDPOINT
from fastapi import HTTPException, status, UploadFile
from utils.AuthUtils import twitter_client
from utils.common import check_file_type
import httpx
import logging

logger = logging.getLogger()

async def fetch_user(token: str | None = None):
    """Get user details from Twitter/X"""
    if token:
        twitter_client.token = token
    try:
        async_current_user = await twitter_client.get(url="https://api.x.com/2/users/me?user.fields=id,username,name,profile_image_url,verified")
    except httpx.ConnectTimeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Oauth service took too long to respond. Please try again."
        )
    except httpx.ConnectError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, 
                            detail="Failed to connect to oauth provider.")
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
                "media_type": check_file_type(self.filename),
                "total_bytes": self.total_bytes,
                "media_category": check_file_type(self.filename, media_category=True)
            }
            req = await twitter_client.post(url=MEDIA_UPLOAD_ENDPOINT, data=request_data)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=str(e))
        except httpx.ConnectTimeout:
            raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Oauth service took too long to respond. Please try again."
        )
        except httpx.ConnectError:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, 
                            detail="Failed to connect to oauth provider.")
        else:
            media_id = req.json()['media_id']
            self.media_id = media_id
            logger.info(f"Media ID: {media_id}")
    
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
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Oauth service took too long to respond. Please try again.")
            except httpx.ConnectError:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, 
                            detail="Failed to connect to oauth provider.")
            else:
                if req.status_code < 200 or req.status_code > 299:
                    raise HTTPException(
                        status_code=req.status_code,
                        detail=req.text
                    )
                segment_id += 1