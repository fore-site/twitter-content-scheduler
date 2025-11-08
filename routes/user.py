from utils import AuthUtils as auth
from authlib.integrations.base_client.errors import OAuthError
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from models.UserModel import BaseUser, UserOut
from models.TokenModel import Token
from services.user import get_access_refresh_token, get_current_active_user, get_new_access_token, revoke_tokens, update_user
from typing import Annotated
import httpx

router = APIRouter()

@router.get("/login")
async def login_user():
    res = RedirectResponse(auth.auth_url)
    # res.set_cookie(key="oauth_state", value=auth.state, httponly=True)
    return res

@router.get("/", response_model=Token)
async def callback_home(request: Request):
    # request_state = request.query_params.get("state")
    # stored_state = request.cookies.get("oauth_state")

    # if stored_state != request_state:
    #     raise HTTPException(status_code=403, detail="Invalid state string.")
    try:
        token = await auth.twitter_client.fetch_token(url=auth.token_uri,
                                  authorization_response=str(request.url),
                                  code_verifier=auth.code_verifier)
    except httpx.ConnectTimeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Oauth service took too long to respond. Please try again."
        )
    except OAuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail=str(e))
    # response.delete_cookie(key="oauth_state")
    access_refresh_token = await get_access_refresh_token()
    return access_refresh_token

@router.get("/profile", response_model=UserOut)
async def get_profile(current_user: Annotated[UserOut, Depends(get_current_active_user)]):
    return current_user

@router.put("/profile", response_model=BaseUser)
async def update_profile(update_user_from_x: Annotated[BaseUser, Depends(update_user)]):
    return update_user_from_x

@router.get("/refresh", response_model=Token)
async def token_refresh(new_access_token: Annotated[Token, Depends(get_new_access_token)]):
    return new_access_token

@router.post("/logout")
async def logout_user(msg: Annotated[dict, Depends(revoke_tokens)]) -> dict:
    return msg
