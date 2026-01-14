from models.PostModel import BasePost, UpdatePost
from object_storage.wasabi_setup import WasabiClient
from services.media import get_media_id, upload_to_wasabi
from typing import List
import logging

logger = logging.getLogger()

async def wasabi_file_handling(user_id: int, 
                               post_body: BasePost | UpdatePost, 
                               media_list: List[str] = []) -> dict:
    s3 = WasabiClient()
    
    media_id_list = []
    
    for file in post_body.files:
        media_id = await get_media_id(user_id=user_id, media=file)
        logger.info(f"Upload to Twitter/X complete, Media ID: {media_id}")
        media_id_list.append(media_id)

    # GENERATE URL FOR UPLOAD AND UPLOAD FILE TO WASABI STORAGE
        put_url = await s3.generate_presigned_url(key=file.filename)
        await upload_to_wasabi(url=put_url, file=file)
    
    # GENERATE URL FOR DOWNLOAD/READING FILE FROM WASABI AND APPEND TO LIST
        get_url = await s3.generate_presigned_url(key=file.filename, method='get')
        media_list.append(get_url)

    return {"media_id_list": media_id_list, "media_list": media_list} 