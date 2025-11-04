from config.db import redis_client
from fastapi import HTTPException, status, Depends
from typing import Annotated
from utils.dependencies import CheckJwt
from utils.AuthUtils import twitter_client
import httpx

async def fetch_user(token: str | None = None):
    if token:
        twitter_client.token = token
    try:
        async_current_user = await twitter_client.get(url=f"https://api.x.com/2/users/me?user.fields=id,username,name,profile_image_url,verified")
    except httpx.ConnectTimeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Oauth service took too long to respond. Please try again."
        )
    else:
        current_user = async_current_user.json()
        return current_user
    
# SAVE OAUTH TOKEN TO DB DURING AUTOMATIC TOKEN REFRESH
async def update_oauth_token(token, user_id: Annotated[int, Depends(CheckJwt())], refresh_token = None, access_token = None):    
    # SAVE TOKEN TO REDIS, THIS IS A TEMPORARY STORAGE
    if refresh_token:
        key = f"{user_id}:oauth"
        await redis_client.set(key, token)
    else:
        print("Unable to save token in redis")
        return