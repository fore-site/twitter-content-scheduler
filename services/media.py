from fastapi import Depends, UploadFile
from typing import Annotated
from utils.dependencies import CheckJwt
from utils.AuthUtils import twitter_client
import re

async def get_media_id(media: UploadFile):
    match = re.search("\.[^.]+$", media.filename)
    return {"file_ext": match.group()[1:]}