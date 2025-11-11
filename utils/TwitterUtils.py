from fastapi import HTTPException, status
from utils.AuthUtils import twitter_client
import httpx

async def fetch_user(token: str | None = None):
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