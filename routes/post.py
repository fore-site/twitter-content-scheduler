from fastapi import Depends, APIRouter, status
from typing import Annotated
from utils.AuthUtils import twitter_client
from utils.dependencies import CheckJwt
from utils.tokenUtils import fetch_oauth_from_redis
from models.PostModel import BasePost
from services.post import create_post, update_post

router = APIRouter()

@router.get("/get-post")
async def get_post(user_id: Annotated[int, Depends(CheckJwt)]):
    oauth_token = fetch_oauth_from_redis(f"{user_id}:oauth")
    twitter_client.token = oauth_token
    async_tweets = await twitter_client.get(f"https://api.x.com/2/users/{user_id}/tweets")
    tweets = async_tweets.json()
    return tweets

@router.post("/posts", response_model=PostIn, status_code=status.HTTP_201_CREATED)
async def make_post(post: Annotated[PostIn, Depends(create_post)]):
    return post

@router.put("/posts/{post_id}", response_model=BasePost)
async def post_update(post_id: int, updated_post: Annotated[BasePost, Depends(update_post)]):
    return updated_post