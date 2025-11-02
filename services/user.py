from config import db
from datetime import timedelta
from utils.dependencies import CheckJwt
from fastapi import Depends, HTTPException, status
from psycopg.rows import dict_row
from typing import Annotated
from utils.AuthUtils import twitter_client, create_access_token, create_refresh_token
from models.UserModel import BaseUser, UserOut
from models.TypeModel import UserStatus
from models.TokenModel import Token
import httpx

async def create_user_in_db(user) -> tuple:
    async with db.db_pool:
        async with db.db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
            INSERT INTO users (id, username, display_name, profile_img, is_premium)
            VALUES
                (%s, %s, %s, %s, %s)
            """, (user.id, 
                  user.username, 
                  user.display_name, 
                  user.profile_img, 
                  user.is_premium))
        await conn.commit()
        
    # SAVE OAUTH TOKEN TO REDIS
    await db.redis_client.set(f"{user.id}:oauth", twitter_client.token)

    # CREATE AND RETURN JWT ACCESS TOKEN 
    payload = {"sub": user.id}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return access_token, refresh_token

async def get_access_refresh_token() -> Token:
    try:
        async_current_user = await twitter_client.get(url="https://api.x.com/2/users/me?user.fields=id,username,name,profile_image_url,verified")
    except httpx.ConnectTimeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Oauth service took too long to respond. Please try again."
        )
    else:
        current_user = async_current_user.json()
    
    # VALIDATE AGAINST PYDANTIC MODEL
    validated_user = BaseUser(id=current_user["data"].get("id"),
                  username=current_user["data"].get("username"),
                  display_name=current_user["data"].get("name"),
                  profile_img=current_user["data"].get("profile_image_url"), 
                  is_premium=current_user["data"].get("verified"))
    
    # CHECK IF USER ALREADY EXISTS IN DATABASE, ELSE CREATE NEW USER
    payload = {"sub": validated_user.id}
    user_exists_in_db = await db.redis_client.exists(f"{validated_user.id}:oauth")
    if user_exists_in_db:
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)
    else:
        tokens = create_user_in_db(validated_user)
        access_token = tokens[0]
        refresh_token = tokens[1]
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

async def get_current_user(user_id: Annotated[int, Depends(CheckJwt())]):
    async with db.db_pool:
        async with db.db_pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute("""
                    SELECT 
                        *, 
                        (SELECT COUNT(*) FROM posts WHERE posts.user_id = %(user_id)s AND posts.post_status ='pending') AS pending_posts, 
                        (SELECT COUNT(*) FROM posts WHERE posts.user_id = %(user_id)s AND posts.post_status = 'sent') AS sent_posts, 
                        (SELECT COUNT(*) FROM posts WHERE posts.user_id = %(user_id)s AND posts.post_status = 'failed') AS failed_posts, 
                        FROM users 
                        WHERE users.id = %(user_id)s               
                    """, {"user_id": user_id})
            result = await cur.fetchall()
            result_dict = result[0]
            user = UserOut(**result_dict)
            return user
        
async def get_current_active_user(current_user: Annotated[UserOut, Depends(get_current_user)]):
    if current_user.user_status == UserStatus.DEACTIVATED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail="User does not exist.")
    elif current_user.user_status == UserStatus.DISABLED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                        detail="User suspended.")
    else:
        return current_user       

async def get_new_access_token(user_id: Annotated[int, Depends(CheckJwt(refresh=True))]):
    new_access_token = create_access_token({"sub": user_id})
    return Token(access_token=new_access_token, token_type="bearer")

async def revoke_tokens(payload: Annotated[dict, Depends(CheckJwt(verify_type=False, dict_format=True))]):
    jti = payload.get("jti")
    ttype = payload.get("type")
    await db.redis_client.set(jti, "")
    return {"detail": f"{ttype} token revoked successfully."}