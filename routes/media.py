from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from services.media import get_media_id
from models.mediaModel import Media

router = APIRouter()

@router.post("/media/upload")
def upload_media(media_id: Annotated[str, Depends(get_media_id)]):
    return media_id