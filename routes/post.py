from fastapi import Depends, APIRouter
from typing import Annotated
from utils.AuthUtils import twitter_client
from utils.dependencies import check_jwt
from config import db
from config.db import redis_client

router = APIRouter()

@router.get("/get-post")
async def get_post(user_id: Annotated[int, Depends(check_jwt)]):
    oauth_token = redis_client.get(f"{user_id}:oauth")
    twitter_client.token = oauth_token
    async_tweets = await twitter_client.get(f"https://api.x.com/2/users/{user_id}/tweets")
    tweets = async_tweets.json()
    return tweets
