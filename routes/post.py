from fastapi import Depends, APIRouter, status
from typing import Annotated
from utils.auth_utils import twitter_client
from utils.dependencies import CheckJwt
from utils.common import fetch_oauth_from_redis
from models.PostModel import BasePost, PostOut
from services.post import create_post, update_post, get_post

router = APIRouter()

@router.get("/posts/{post_id}", response_model=PostOut)
async def fetch_post(post: Annotated[PostOut, Depends(get_post)]):
    return post

@router.post("/posts", response_model=BasePost, status_code=status.HTTP_201_CREATED)
async def make_post(post: Annotated[BasePost, Depends(create_post)]):
    return post

# UPDATE PENDING POST (CANNOT UPDATE SENT OR FAILED POST)
@router.put("/posts/{post_id}", response_model=BasePost)
async def post_update(updated_post: Annotated[BasePost, Depends(update_post)]):
    return updated_post
