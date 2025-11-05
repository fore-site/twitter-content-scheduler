from fastapi import Depends, APIRouter, status
from typing import Annotated
from utils.AuthUtils import twitter_client
from utils.dependencies import CheckJwt
from config import db
from config.db import redis_client
from models.PostModel import PostIn, UpdatePost
from services.post import create_post, update_post

router = APIRouter()

@router.get("/get-post")
async def get_post(user_id: Annotated[int, Depends(CheckJwt)]):
    oauth_token = redis_client.get(f"{user_id}:oauth")
    twitter_client.token = oauth_token
    async_tweets = await twitter_client.get(f"https://api.x.com/2/users/{user_id}/tweets")
    tweets = async_tweets.json()
    return tweets

@router.post("/posts", response_model=PostIn, status_code=status.HTTP_201_CREATED)
async def make_post(post: Annotated[PostIn, Depends(create_post)]):
    return post

@router.put("/posts/{post_id}", response_model=UpdatePost)
async def post_update(post_id: int, updated_post: Annotated[UpdatePost, Depends(update_post)]):
    return updated_post